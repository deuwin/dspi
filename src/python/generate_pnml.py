from pathlib import Path
import sys
import os
import argparse
import importlib


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
    return  parser.parse_args()


def addHeaderGuards(filename, text):
    macro_name = "__GENERATED_" + filename.upper().replace(".", "_")
    return (
        f"#ifndef {macro_name}\n"
        + f"#define {macro_name}\n\n"
        + text
        + f"\n\n#endif // {macro_name}"
    )


MODULES = [
    "cargotable",
    "stockpile",
    "industry_items",
]

def main():
    args = parseArguments()

    output_files = {}
    for module in MODULES:
        output_files[module + ".pnml"] = importlib.import_module(module)

    if args.list_files:
        filenames = []
        for filename in list(output_files) + ["header.pnml"]:
            filenames.append(str(args.output_directory / filename))
        print(" ".join(filenames))
        exit(os.EX_OK)

    try:
        if not args.output_directory.is_dir():
            raise NotADirectoryError(
                f'Output directory "{args.output_directory}" does not exist!'
            )

        header = ""
        for filename, generator in output_files.items():
            file = args.output_directory / filename
            file.write_text(addHeaderGuards(filename, generator.generate()))
            header += f'#include "{filename}"\n'
    except OSError as err:
        errorExit(err)

    # create header
    (args.output_directory / "header.pnml").write_text(header)

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
