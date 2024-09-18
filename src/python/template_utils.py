from pathlib import Path
from string import Template
import re


TEMPLATE_DIR = Path(__file__).parent / "templates"
def getTemplate(name):
    return Template((TEMPLATE_DIR / (name + ".txt")).read_text())


def getRatioString(numerator, denominator):
    ratio_str = ""
    if numerator != denominator:
        if numerator != 1:
            ratio_str += f" * {numerator}"
        if denominator != 1:
            ratio_str += f" / {denominator}"
    return ratio_str


def cargoToPluralString(cargo):
    # https://newgrf-specs.tt-wiki.net/wiki/NML:Default_TTD_strings
    return (
        "TTD_STR_CARGO_PLURAL_"
        + "_".join(re.findall("[A-Z][a-z]+", cargo.name)).upper()
    )
