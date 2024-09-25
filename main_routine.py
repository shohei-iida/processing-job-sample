from pathlib import Path

import click
from processing_job_sample.hello_world import read_msg, write_msg


@click.command()
@click.option("--input-dir", type=Path)
@click.option("--out-dir", type=Path)
def main(
    input_dir: Path,
    out_dir: Path,
) -> None:
    input_file = input_dir.joinpath("sample_msg.txt")
    out_file = out_dir.joinpath("stdout.txt")

    read_msg(input_file)
    write_msg(out_file)


if __name__ == "__main__":
    main()
