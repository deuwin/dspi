from dataclasses import dataclass
from string import Template
from pathlib import Path

from cargotable import CargoTable as Cargo


# fmt: off
@dataclass(frozen=True)
class Industry:
    id:     str
    input:  str | list[str]
    output: str

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
            "cycle_consume":    genCycleConsume(industry),
            "cycle_produce":    genCycleProduce(industry),
            "production_limit": genProductionLimit(industry),
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
            "cycle_consume":    genCycleConsume(industry),
            "production_limit": genProductionLimit(industry),
            "stockpile_level":  genRelevantLevel(industry),
            "accept_cargo":     genCargoTypeAccept(industry),
        }
        pnml += template.substitute(template_values)

    return pnml

# fmt: on


def genCycleConsume(industry):
    if type(industry.input) == str:
        return f"{industry.input}: LOAD_TEMP(0);"

    consume = ""
    for temp_reg, input in enumerate(industry.input):
        consume += f"{input}: LOAD_TEMP({temp_reg});\n        "
    return consume[:-9]


def genCycleProduce(industry):
    if type(industry.input) == str:
        return f"{industry.output}: LOAD_TEMP(0);"

    produce = f"{industry.output}: "
    for temp_reg, input in enumerate(industry.input):
        produce += f"LOAD_TEMP({temp_reg}) + "
    return produce[:-3] + ";"


def genProductionLimit(industry):
    prefix = "STORE_TEMP(min(GET_PERM(PRODUCTION_RATE), incoming_cargo_waiting("

    if type(industry.input) == str:
        return prefix + f'"{industry.input}")), 0),'

    limit = ""
    for temp_reg, input in enumerate(industry.input):
        limit += prefix + f'"{input}")), {temp_reg}),\n    '
    return limit[:-5]


def genRelevantLevel(ind):
    if type(ind.input) is str:
        return f'incoming_cargo_waiting("{ind.input}")'

    relevant_level = f'incoming_cargo_waiting("{ind.input[0]}")'
    for input in ind.input[1:]:
        relevant_level = (
            f'max(incoming_cargo_waiting("{input}"), ' + relevant_level + ")"
        )
    return relevant_level


def genCargoTypeAccept(ind):
    if type(ind.input) == str:
        return f'accept_cargo("{ind.input}"),'

    accept_cargo = ""
    for input in ind.input:
        accept_cargo += f'accept_cargo("{input}"),\n' + " " * 12
    return accept_cargo[:-13]


def genCargoTypeProduce(ind):
    return f'produce_cargo("{ind.output}", 0),'


def main(argv):
    print(generateIndustryPnml())


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
