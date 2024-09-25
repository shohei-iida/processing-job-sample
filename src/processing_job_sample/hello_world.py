from pathlib import Path


def read_msg(input_dir: Path):
    with open(input_dir, "r") as f:
        print("\n".join(f.readlines()).strip())


def write_msg(out_file: Path):
    print(f"Output to {out_file}")
    with open(out_file, "w") as f:
        print("Hello, Processing Job!", file=f)
