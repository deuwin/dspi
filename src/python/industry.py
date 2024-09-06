from dataclasses import dataclass, InitVar
from string import Template
from pathlib import Path
from typing import Optional

from cargotable import CargoTable as Cargo


# fmt: off
@dataclass(frozen=True)
class Industry:
    """
    Storage for basic data about each industry.

    Args:
        id (str): The industry identifier. Should be a string from the list of
            default industries. See:
            https://newgrf-specs.tt-wiki.net/wiki/NML:Default_industries
        input(str|list[str]): Cargo accepted by the industry.
        output(str): Cargo generated by the industry.
        tiles (list[int], optional): Industry tile IDs to override. Only
            required if you change accepted cargo from the default. A list of
            industry tile IDs can be found here:
            https://newgrf-specs.tt-wiki.net/wiki/NML:Default_industry_tiles
        ratio (list[int], optional): Ratio of inputs consumed to produce 1 unit
            of output cargo.
    """

    id:     str
    input:  InitVar[str | list[str]]
    output: str | None
    tiles:  Optional[list[int]] = None
    ratio:  Optional[list[int]] = None

    def __post_init__(self, input):
        if type(input) == list:
            object.__setattr__(self, "input", input)
        else:
            object.__setattr__(self, "input", [input])

    @property
    def name(self):
        return self.id[13:].lower()


# temperate industries
SECONDARY_INDUSTRIES = [
    Industry(
        "INDUSTRYTYPE_STEEL_MILL",
        Cargo.IronOre,
        Cargo.Steel,
    ),
    Industry(
        "INDUSTRYTYPE_SAWMILL",
        Cargo.Wood,
        Cargo.Goods,
    ),
    Industry(
        "INDUSTRYTYPE_TEMPERATE_FACTORY",
        [
            Cargo.Livestock,
            Cargo.Grain,
            Cargo.Steel,
        ],
        Cargo.Goods,
    ),
    Industry(
        "INDUSTRYTYPE_OIL_REFINERY",
        Cargo.Oil,
        Cargo.Goods
    ),
]

TERTIARY_INDUSTRIES = [
    Industry(
        "INDUSTRYTYPE_POWER_PLANT",
        Cargo.Coal,
        None
    ),
]


def generateIndustryPnml():
    pnml = ""

    template_file = Path(__file__).parent / "templates" / "secondary.txt"
    template = Template(template_file.read_text())
    for industry in SECONDARY_INDUSTRIES:
        template_values = {
            "id":               industry.id,
            "name":             industry.name,
            "prodtick_consume": genProdTickConsume(industry),
            "prodtick_produce": genProdTickProduce(industry),
            "production_limit": genProductionLimitSecondary(industry),
            "consumed_total":   genConsumedTotal(industry),
            "stockpile_level":  genRelevantLevel(industry),
            "output":           industry.output,
            "accept_cargo":     genCargoTypeAccept(industry),
            "produce_cargo":    genCargoTypeProduce(industry),
        }
        pnml += template.substitute(template_values)

    template_file = template_file.with_stem("tertiary")
    template = Template(template_file.read_text())
    for industry in TERTIARY_INDUSTRIES:
        template_values = {
            "id":               industry.id,
            "name":             industry.name,
            "prodtick_consume": genProdTickConsume(industry),
            "consume_limit":    genConsumeLimitTertiary(industry),
            "consume_total":    genConsumedTotal(industry),
            "stockpile_level":  genRelevantLevel(industry),
            "accept_cargo":     genCargoTypeAccept(industry),
        }
        pnml += template.substitute(template_values)

    return pnml
# fmt: on


def indent(text, indent_level):
    for idx, line in enumerate(text[1:], start=1):
        text[idx] = "    " * indent_level + line
    return "\n".join(text)


def genProdTickConsume(industry):
    consume = []
    for reg_idx, input in enumerate(industry.input):
        consume.append(f"{input}: GET_TEMP(CONSUMED_{reg_idx});")
    return indent(consume, 2)


def genProdTickProduce(industry):
    return f"{industry.output}: GET_TEMP(CONSUMED_TOTAL);"


def genProductionLimitSecondary(industry):
    limit = []
    for reg_idx, input in enumerate(industry.input):
        limit.append(
            f"SET_TEMP(CONSUMED_{reg_idx}, "
                f'min(incoming_cargo_waiting("{input}"), GET_PERM(PRODUCTION_RATE))'
            "),"
        )
    return indent(limit, 1)


def genConsumeLimitTertiary(industry):
    limit = []
    for reg_idx, input in enumerate(industry.input):
       limit.append(
            f"SET_TEMP(CONSUMED_{reg_idx}, "
                f'min(incoming_cargo_waiting("{input}"), GET_TEMP(FUEL_REQUIRED))'
            "),"
        )
    return indent(limit, 1)


def genConsumedTotal(industry):
    produced = "SET_TEMP(CONSUMED_TOTAL, "
    for reg_idx, input in enumerate(industry.input):
        produced += f"GET_TEMP(CONSUMED_{reg_idx}) + "
    return produced[:-3] + "),"


def genRelevantLevel(ind):
    relevant_level = f'incoming_cargo_waiting("{ind.input[0]}")'
    for input in ind.input[1:]:
        relevant_level = (
            f'max(incoming_cargo_waiting("{input}"), ' + relevant_level + ")"
        )
    return relevant_level


def genCargoTypeAccept(ind):
    accept_cargo = []
    for input in ind.input:
        accept_cargo.append(f'accept_cargo("{input}"),')
    return indent(accept_cargo, 3)


def genCargoTypeProduce(ind):
    return f'produce_cargo("{ind.output}", 0),'


def main(argv):
    print(generateIndustryPnml())


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
