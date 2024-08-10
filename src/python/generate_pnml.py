from pathlib import Path
import sys
import os
import argparse

from industry import generateIndustryPnml
from industry_functions import genIsStockpileFull
from cargotable import generateCargoTable


def errorExit(error):
    print(f"\033[91mError\033[0m {str(error)}", file=sys.stderr)
    sys.exit(1)


def parseArguments():
    parser = argparse.ArgumentParser(
        description=(
            "Generate .pnml files for use in dSPI.grf. Called without arguments "
            "will create files in the current directory."
        )
    )
    parser.add_argument(
        "-d",
        "--output-directory",
        help="Directory to place generated .pnml files",
        default=".",
        type=Path,
    )
    parser.add_argument(
        "-l",
        "--list-files",
        help="List output files that would be generated but do not generate them",
        action="store_true",
    )
    args = parser.parse_args()

    return args


def generateIndustryFile():
    # functions shared by all industries
    pnml = genIsStockpileFull()
    # item blocks and functions particular to each industry
    pnml += generateIndustryPnml()
    return pnml


_OUTPUT_FILES = {
    "cargotable.pnml": generateCargoTable,
    "industry.pnml": generateIndustryFile,
}


def main():
    args = parseArguments()

    if args.list_files:
        files = []
        for file in _OUTPUT_FILES.keys():
            files.append(str(args.output_directory / file))
        print(" ".join(files))
        exit(os.EX_OK)

    try:
        for file, generator in _OUTPUT_FILES.items():
            file_out = args.output_directory / file
            file_out.write_text(generator())
    except OSError as err:
        errorExit(err)

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
