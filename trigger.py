"""Pythonスクリプト `main_routine.py` をProcessingJobで実行するためのスクリプトです。

実行にあたっては `get_parameters()` の値を設定し、その後下記のコマンドを実行してください。

Usage:
    > python trigger.py --job-name job
"""
import os
from pathlib import Path
from typing import Final

import click
from processing_job_sample.processing import (
    run_processor,
    upload_package,
)
from s3pathlib import S3Path
from sagemaker import get_execution_role
from sagemaker.pytorch.processing import PyTorchProcessor


# NOTE: AWSの権限を取得します。
ROLE = get_execution_role()

# NOTE: ProcessingJobで使用するインスタンスのディレクトリを指定します。
INPUT_DIR = "/opt/ml/processing/input"
OUTPUT_DIR = "/opt/ml/processing/output"


def get_parameters() -> dict[str, str]:
    # TODO: この関数内部のパラメータはユーザ毎に変更してください。
    return {
        "s3_root_dir_path": "processing-job-sample"  # NOTE: S3上のルートディレクトリのパス
    }


@click.command()
@click.option("--job-name", type=str, default="job")
def main(job_name: str):
    """ ProcessingJobに `main_routine.py` を実行するジョブを流します。

    Args:
        job_name (str): CloudWatch, S3で参照する際に用いる任意のジョブ名
    """
    params = get_parameters()

    # NOTE: ProcessingJobで用いるインスタンスを設定します。
    processor_framework_ver: Final[str] = "2.1.0"
    processor_python_ver: Final[str] = "py310"
    processor_instance_type: Final[str] = "ml.m5.24xlarge"

    # NOTE: 入出力ディレクトリ置き場であるS3上のバケット名を指定します。
    bucket_name: Final[str] = os.getenv("BUCKET_NAME")

    # NOTE: Pythonパッケージ名を指定します。
    package_name: Final[str] = "processing-job-sample"

    # NOTE: S3上の入出力ディレクトリのルートを指定します。
    s3_root_dir_path = params["s3_root_dir_path"]
    s3_root_dir = S3Path(bucket_name, f"{s3_root_dir_path}/")

    # NOTE: 入出力ディレクトリのルートを指定します。
    package_root_dir = Path("/home/sagemaker-user")
    s3_package_dir = S3Path(
        bucket_name,
        f"{s3_root_dir_path}/package",
        f"{package_name}.tar.gz",
    )

    # NOTE: 入力ディレクトリを指定します。
    s3_data_dir = S3Path(bucket_name, "processing-job-sample/")
    s3_inputs = [
        s3_data_dir.joinpath("input/"),
        s3_data_dir.joinpath("package/"),
    ]

    # NOTE: 出力ディレクトリを指定します。
    s3_out_dir = s3_root_dir

    # NOTE: ProcessingJob上の実行スクリプトとそのパラメータを指定します。
    run_script = "launcher.sh"
    script_arguments = [
        "--input-dir",
        f"{INPUT_DIR}/input/",
        "--out-dir",
        f"{OUTPUT_DIR}/",
    ]

    # NOTE: ローカルのパッケージをProcessingJobのインスタンスへアップロードします。
    upload_package(
        package_root_dir,
        package_name,
        s3_package_dir,
    )

    # NOTE: ProcessingJobのインスタンスを取得します。
    processor = PyTorchProcessor(
        framework_version=processor_framework_ver,
        py_version=processor_python_ver,
        role=ROLE,
        instance_type=processor_instance_type,
        instance_count=1,
    )

    # NOTE: ProcessingJobへジョブを流します。
    run_processor(
        processor=processor,
        s3_inputs=s3_inputs,
        s3_out_dir=s3_out_dir,
        run_script=run_script,
        script_arguments=script_arguments,
        job_name_prefix=job_name,
    )


if __name__ == "__main__":
    main()
