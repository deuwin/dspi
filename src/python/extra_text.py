from string import Template

from industry import INDUSTRIES, Sector
from template_utils import getTemplate, getRatioString, cargoToPluralString


def generate():
    template = getTemplate("extra_text_ratio")

    pnml = ""
    for industry in INDUSTRIES:
        if not industry.ratio:
            continue
        pnml += template.substitute(getTemplateMapping(industry))

    return pnml


def getTemplateMapping(industry):
    mapping = {
        "name": industry.name,
    }

    cargo_prefix = "cargo_name_"
    for idx, cargo in enumerate(industry.input):
        mapping[cargo_prefix + str(idx)] = cargoToPluralString(cargo)

    proportion_out = industry.ratio[-1]
    ratio_prefix = "ratio_"
    for idx, ratio in enumerate(industry.ratio[:-1]):
        mapping[ratio_prefix + str(idx)] = getRatioString(
            industry.ratio[idx], proportion_out
        )

    return mapping


def main(argv):
    print(generate())


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
