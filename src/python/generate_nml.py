from pathlib import Path
import sys
import os

from industry import generateIndustryNml


def errorExit(error):
    print(f"\033[91mError\033[0m {str(error)}", file=sys.stderr)
    sys.exit(1)


def main(argv):
    if len(argv) == 1:
        errorExit("Output directory not specified!")

    output_directory = Path(argv[1])
    if not output_directory.is_dir():
        errorExit(f'Specified path "{output_directory}" is not a directory!')

    industry_file = output_directory / "industry.pnml"
    try:
        industry_file.write_text(generateIndustryNml())
    except OSError as err:
        errorExit(err)

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv))
