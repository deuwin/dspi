from dataclasses import dataclass
from string import Template
from pathlib import Path

from cargo import Cargo


# fmt: off
@dataclass(frozen=True)
class Industry:
    id:     str
    input:  str | list[str]
    output: str

    @property
    def name(self):
        return self.id[13:].lower()

# temperate secondary industries
INDUSTRIES = [
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
# fmt: on


@dataclass(frozen=True)
class IndTemplate:
    production_limit: Template = Template(
        'STORE_TEMP(min(GET_PERM(PRODUCTION_RATE), incoming_cargo_waiting("$input")), $temp_reg),'

    )


# fmt: off
def generateIndustryNml():
    template_file = Path(__file__).parent / "industry_template.txt"
    template = Template(template_file.read_text())

    nml = ""
    for industry in INDUSTRIES:
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
        nml += template.substitute(template_values)
    return nml
# fmt: on


def genProductionLimit(industry):
    if type(industry.input) == list:
        limit = ""
        for temp_reg, input in enumerate(industry.input):
            limit += (
                IndTemplate.production_limit.substitute(input=input, temp_reg=temp_reg)
                + "\n    "
            )
        return limit[:-5]
    else:
        temp_reg = 0
        return IndTemplate.production_limit.substitute(
            input=industry.input, temp_reg=temp_reg
        )


def genCycleConsume(industry):
    if type(industry.input) == list:
        consume = ""
        for temp_reg, input in enumerate(industry.input):
            consume += f"{input}: LOAD_TEMP({temp_reg});\n        "
        return consume[:-9]
    else:
        return f"{industry.input}: LOAD_TEMP(0);"


def genCycleProduce(industry):
    if type(industry.input) == list:
        produce = f"{industry.output}: "
        for temp_reg, input in enumerate(industry.input):
            produce += f"LOAD_TEMP({temp_reg}) + "
        return produce[:-3] + ";"
    else:
        return f"{industry.output}: LOAD_TEMP(0);"


def genCargoTypeAccept(ind):
    if type(ind.input) == list:
        accept_cargo = ""
        for input in ind.input:
            accept_cargo += f'accept_cargo("{input}"),\n' + " " * 12
        return accept_cargo[:-13]
    else:
        return f'accept_cargo("{ind.input}"),'


def genCargoTypeProduce(ind):
    return f'produce_cargo("{ind.output}", 0),'


def genRelevantLevel(ind):
    if type(ind.input) is str:
        return f'incoming_cargo_waiting("{ind.input}")'

    relevant_level = f'incoming_cargo_waiting("{ind.input[0]}")'
    for input in ind.input[1:]:
        relevant_level = f'max(incoming_cargo_waiting("{input}"), ' + relevant_level + ")"

    return relevant_level


def main(argv):
    print(generateIndustryNml())


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
