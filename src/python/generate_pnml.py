from pathlib import Path
import sys
import os
import argparse

from industry import generateIndustryPnml
from stockpile import genIsStockpileFull
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


_OUTPUT_FILES = {
    "cargotable.pnml": generateCargoTable,
    "stockpile.pnml" : genIsStockpileFull,
    "industry_items.pnml": generateIndustryPnml,
}


def createHeader(output_directory):
    header = ""
    for file in _OUTPUT_FILES:
        header += f'#include "{file}"\n'
    try:
        file_out = (output_directory / "header.pnml").write_text(header)
    except OSError as err:
        errorExit(err)


def addHeaderGuards(filename, text):
    macro_name = "__GENERATED_" + filename.upper().replace(".", "_")
    return (
        f"#ifndef {macro_name}\n"
        + f"#define {macro_name}\n\n"
        + text
        + f"\n\n#endif // {macro_name}"
    )


def main():
    args = parseArguments()

    if args.list_files:
        files = []
        for file in list(_OUTPUT_FILES) + ["header.pnml"]:
            files.append(str(args.output_directory / file))
        print(" ".join(files))
        exit(os.EX_OK)

    try:
        if not args.output_directory.is_dir():
            raise NotADirectoryError(
                f'Output directory "{args.output_directory}" does not exist!'
            )

        for file, generator in _OUTPUT_FILES.items():
            file_out = args.output_directory / file
            file_out.write_text(addHeaderGuards(file, generator()))
    except OSError as err:
        errorExit(err)

    createHeader(args.output_directory)

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
