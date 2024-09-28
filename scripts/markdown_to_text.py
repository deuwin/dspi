import sys
import argparse
import re
import textwrap


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
    def __init__(self, label, level):
        if type(label) is list:
            self.label = " ".join(label)
        else:
            self.label = label
        match level:
            case 1:
                self.sep = "="
            case 2:
                self.sep = "-"

    def format(self):
        return "\n" + self.label + "\n" + self.sep * len(self.label) + "\n"


class Paragraph:
    def __init__(self, lines):
        self.lines = lines
        self.is_bullet = self._isBulletpointList()

    def _isBulletpointList(self):
        for line in self.lines:
            if line and line.lstrip()[0] == "*":
                return True
        else:
            return False

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

        if self.is_bullet:
            formatted = "\n".join(self.lines)
        else:
            formatted = textwrap.fill(" ".join(self.lines))

        return formatted + "\n\n"


def main(argv):
    args = parseArguments()

    with open(args.input) as input_file:
        input = input_file.read()

    sections = []
    paragraph = []
    for line in input.splitlines():
        if line:
            if line.startswith("#"):
                split = line.split()
                sections.append(Heading(split[1:], len(split[0])))
            else:
                paragraph.append(line)
        elif paragraph:
            sections.append(Paragraph(paragraph))
            paragraph = []

    if paragraph:
        sections.append(Paragraph(paragraph))

    output = ""
    for section in sections:
        output += section.format()
    output = output.strip()

    with open(args.output, "w") as output_file:
        output_file.write(output)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
