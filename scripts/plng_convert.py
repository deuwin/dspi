import sys
import argparse
import re


def parseArguments():
    parser = argparse.ArgumentParser(
        description=(
            "Convert .plng files to .lng files, basically just joins lines. "
            "See docs/plng.md for more detail."
        )
    )
    parser.add_argument(
        "input",
        metavar="INPUT_FILE",
        help="Path to .plng file to convert",
    )
    parser.add_argument(
        "output",
        metavar="OUTPUT_FILE",
        help="Path to store result of conversion",
    )
    return parser.parse_args()


class StringDefinition:
    def __init__(self, name, text=""):
        self.name = name
        self.text = []
        self.appendText(text)

    def appendText(self, text):
        text = text.strip()
        if len(text) == 0:
            return
        if not text.endswith("{}"):
            text += " "
        self.text.append(text)

    def create(self):
        return self.name + ":" + "".join(self.text)


string_definition = re.compile("([A-Za-z0-9_]+):(.*)")
def main(argv):
    args = parseArguments()

    with open(args.input) as input_file:
        input = input_file.read()

    string_def = None
    output = []
    for line in input.splitlines():
        match = string_definition.match(line)
        if match:
            # write previous string definition
            if string_def:
                output.append(string_def.create())

            # new string definition
            string_def = StringDefinition(match.group(1), match.group(2))
            continue

        new_line = None
        if not line:
            # blank line
            new_line = ""
        elif line[0] == "#":
            # comment or pragma, leave as is
            new_line = line
        else:
            # text continuation
            string_def.appendText(line)

        if new_line is not None:
            # write previous string definition
            if string_def:
                output.append(string_def.create())
                string_def = None
            output.append(new_line)
    else:
        if string_def:
            output.append(string_def.create())

    output_text = "\n".join(output)

    with open(args.output, "w") as output_file:
        output_file.write(output_text)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
