"""For debug before running on SageMaker.Processing."""
from pathlib import Path

import click
from main_routine import main as main_routine


@click.command()
@click.option("--input-dir", type=Path)
@click.option("--out-dir", type=Path)
def main(input_dir: Path, out_dir: Path):
    args = [
        "--input-dir",
        input_dir,
        "--out-dir",
        out_dir,
    ]
    main_routine(args)


if __name__ == "__main__":
    main()
