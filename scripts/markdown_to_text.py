import sys
import argparse
import re
import textwrap
from enum import Enum, auto


def parseArguments():
    parser = argparse.ArgumentParser(
        description=(
            "Convert markdown files to text files. Adjusts markdown syntax to "
            "be more like the changelog.txt style."
        )
    )
    parser.add_argument(
        "input",
        metavar="INPUT_FILE",
        help="Path to markdown file to convert",
    )
    parser.add_argument(
        "output",
        metavar="OUTPUT_FILE",
        help="Path to store result of conversion",
    )

    return parser.parse_args()


class Heading:
    def __init__(self, line):
        (level, *label) = line.split()
        if type(label) is list:
            self.label = " ".join(label)
        else:
            self.label = label
        if len(level) == 1:
            self.sep = "="
        else:
            self.sep = "-"

    def format(self):
        return self.label + "\n" + self.sep * len(self.label) + "\n"


class Block:
    def __init__(self, line):
        self.lines = [line]

    def append(self, line):
        self.lines.append(line)


class Blank(Block):
    def format(self):
        return "\n" * len(self.lines)


class BulletList(Block):
    def format(self):
        return "\n".join(self.lines) + "\n"


class Paragraph(Block):
    def _stripUrls(self, line):
        match = re.search(r"(.*)\[(.*)\](\(.*\))(.*)", line)
        if not match:
            return line
        else:
            return match.group(1) + match.group(2) + match.group(4)

    def format(self):
        # strip URLs since one cannot interact with them via the in-game reader
        for idx, line in enumerate(self.lines):
            self.lines[idx] = self._stripUrls(line)

        return textwrap.fill(" ".join(self.lines)) + "\n"


# map line type to the class that formats the line
class LineType(Enum):
    Blank = Blank
    Heading = Heading
    BulletPoint = BulletList
    Text = Paragraph


class Line:
    def __init__(self, line):
        self.text = line
        self.type = self._getLineType()

    def _getLineType(self):
        if len(self.text.strip()) == 0:
            return LineType.Blank
        elif self.text.startswith("#"):
            return LineType.Heading
        elif self.text.lstrip().startswith("*"):
            return LineType.BulletPoint
        else:
            return LineType.Text

    def newBlock(self):
        return self.type.value(self.text)


def main(argv):
    args = parseArguments()

    with open(args.input) as input_file:
        input = input_file.read()

    input_lines = input.splitlines()
    line = Line(input_lines[0])
    blocks = [line.newBlock()]
    line_type_prev = line.type
    for input_line in input_lines[1:]:
        line = Line(input_line)

        if line.type == LineType.Heading:
            blocks.append(line.newBlock())
        elif line.type == line_type_prev:
            blocks[-1].append(line.text)
        else:
            blocks.append(line.newBlock())

        line_type_prev = line.type

    output = ""
    for block in blocks:
        output += block.format()
    output = output.strip()

    with open(args.output, "w") as output_file:
        output_file.write(output)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
