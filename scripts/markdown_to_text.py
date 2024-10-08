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
        return "\n"


class BulletList(Block):
    def format(self):
        return "\n".join(self.lines) + "\n"


class ItemList(Block):
    def format(self):
        name = "  - " + self.lines[0].strip("* ") + "\n"
        definition = textwrap.fill(
            " ".join(self.lines[1:]),
            initial_indent="      ",
            subsequent_indent="      ",
        )

        return name + definition + "\n"


class Paragraph(Block):
    link = re.compile(r"\[(.*?)\](\(.*?\))")
    comment = re.compile(r"<!--.*?-->")

    def _getLinkText(self, match):
        return match.group(1)

    def format(self):
        for idx, line in enumerate(self.lines):
            # replace links
            line = re.sub(self.link, self._getLinkText, line)
            # strip comments
            line = re.sub(self.comment, "", line)
            self.lines[idx] = line

        return textwrap.fill(" ".join(self.lines)) + "\n"


# map line type to the class that formats the line
class LineType(Enum):
    Blank = Blank
    Heading = Heading
    BulletPoint = BulletList
    ItemName = ItemList
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
        elif self.text.startswith("**") and self.text.endswith("**  "):
            return LineType.ItemName
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
    always_new = set([LineType.Heading, LineType.Blank])
    for input_line in input_lines[1:]:
        line = Line(input_line)

        if always_new.intersection([line.type, line_type_prev]):
            blocks.append(line.newBlock())
        elif line.type in [line_type_prev, LineType.Text]:
            blocks[-1].append(line.text)
        else:
            blocks.append(line.newBlock())

        line_type_prev = line.type

    output = ""
    skip_block = False
    for block in blocks:
        # don't write out the screenshots section
        try:
            if block.label == "Screenshots":
                skip_block = True
            else:
                skip_block = False
        except:
            pass

        if skip_block:
            continue

        output += block.format()

    output = output.strip()

    with open(args.output, "w") as output_file:
        output_file.write(output)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
