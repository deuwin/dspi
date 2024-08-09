from pathlib import Path
import sys
import os

from industry import generateIndustryNml
from industry_functions import genIsStockpileFull

def errorExit(error):
    print(f"\033[91mError\033[0m {str(error)}", file=sys.stderr)
    sys.exit(1)


def main(argv):
    if len(argv) == 1:
        errorExit("Output directory not specified!")

    output_directory = Path(argv[1])
    if not output_directory.is_dir():
        errorExit(f'Specified path "{output_directory}" is not a directory!')

    output_files = {
        "industry.pnml": genIsStockpileFull,
        "industry_functions.pnml": generateIndustryNml
    }
    try:
        for file, generator in output_files.items():
            file_out = output_directory / file
            file_out.write_text(generator())
    except OSError as err:
        errorExit(err)

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv))
