"""Wrapper for SageMaker Processing.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from subprocess import PIPE, run
from time import tzname
from typing import Optional

from s3pathlib import S3Path
from sagemaker import get_execution_role
from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor

ROLE = get_execution_role()
INPUT_DIR = "/opt/ml/processing/input"
OUTPUT_DIR = "/opt/ml/processing/output"


def upload_script_to_s3(src_path: Path, dst_path: S3Path) -> str:
    """For ProcessingJob, upload target script and return uri.
    For another purpose, use S3Path.upload_dir() or S3Path.upload_file().

    Args:
        src_path (Path): _description_
        dst_path (S3Path): _description_

    Returns:
        str: _description_
    """
    dst_path.joinpath(src_path.name).upload_file(src_path, overwrite=True)
    return dst_path.joinpath(src_path.name).uri


def get_current_time() -> str:
    cur_time = datetime.now()
    if tzname[0] == "UTC":
        cur_time = cur_time.astimezone(timezone(timedelta(hours=9)))
    return cur_time.strftime("%Y-%m-%d-%H-%M")


def convert_pyproject_to_requirements(suffix: Path, repository_name: Path):
    requirements_file = Path(f"{suffix.joinpath(repository_name)}/requirements.txt")
    run(
        f"poetry export --format requirements.txt --output {requirements_file} --without-hashes",
        shell=True,
    )

    with open(requirements_file, "r") as f:
        requirements = f.readlines()

    requirements.insert(0, "-e .\n")

    with open(requirements_file, "w") as f:
        f.write("".join(requirements))


def archive_package(suffix: Path, repository_name: Path):
    archived_file = Path(f"{repository_name}.tar.gz")
    if archived_file.exists():
        archived_file.unlink()

    run(f"tar -C {suffix} -zcvf {archived_file} {repository_name}/", shell=True)


def upload_package(package_root_dir: Path, package_name: str, s3_dst_dir: S3Path):
    convert_pyproject_to_requirements(package_root_dir, package_name)
    archive_package(package_root_dir, package_name)

    archived_package = Path(f"{package_name}.tar.gz")
    s3_dst_dir.upload_file(archived_package, overwrite=True)
    archived_package.unlink()


def get_nearest_parent_dir(s3_input_path: S3Path) -> str:
    if s3_input_path.is_dir():
        return s3_input_path.parts[-1]
    return s3_input_path.parents[0].parts[-1]


def check_code(root_dir: Path = Path("./")):
    res = run(f"flake8 {str(root_dir)}/*.py", shell=True, stdout=PIPE)
    res_msg = res.stdout.decode("utf8").strip()
    if res_msg.strip() != "":
        print("Error: trigger.py cannot run job for coding problem.")
        print(res_msg)
        raise RuntimeError


def run_processor(
    processor: ScriptProcessor,
    s3_inputs: list[S3Path],
    s3_out_dir: S3Path,
    run_script: str | Path,
    script_arguments: list[str],
    *,
    job_name_prefix: str = "job",
    timestamp: Optional[str] = None,
):
    if timestamp is None:
        timestamp = get_current_time()

    s3_out_dir = s3_out_dir.joinpath(f"workflow/{job_name_prefix}-{timestamp}")
    processing_job_name = f"{job_name_prefix}-{timestamp}"

    run_script = Path(run_script) if isinstance(run_script, str) else run_script
    uploaded_script_path = upload_script_to_s3(run_script, s3_out_dir)
    print(f"Run script is uploaded to: {uploaded_script_path}")

    processor.run(
        code=uploaded_script_path,
        inputs=[
            ProcessingInput(
                source=s3_input.uri,
                destination=f"{INPUT_DIR}/{get_nearest_parent_dir(s3_input)}",
                # destination=INPUT_DIR,  # NOTE: ProcessingInput don't allow same dst.
            )
            for s3_input in s3_inputs
        ],
        outputs=[
            ProcessingOutput(
                source=OUTPUT_DIR,
                destination=s3_out_dir.uri,
            ),
        ],
        arguments=script_arguments if len(script_arguments) else None,
        wait=False,
        job_name=processing_job_name,
    )
