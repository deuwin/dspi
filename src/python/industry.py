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
        "INDUSTRYTYPE_FACTORY",
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
    monthly_prod_change: Template = Template(
        "changeProduction(\n"
        + " " * 36
        + 'incoming_cargo_waiting("$input"),\n'
        + " " * 36
        + 'last_month_production("$output"),\n'
        + " " * 36
        + 'transported_last_month_pct("$output")\n'
        + " " * 31
        + ");"
    )
    production_limit: Template = Template(
        'STORE_TEMP(min(LOAD_TEMP(0), incoming_cargo_waiting("$input"), $temp_reg),'
    )


# fmt: off
def generateIndustryNml(template_file):
    template = Template(Path(template_file).read_text())

    nml = ""
    for industry in INDUSTRIES:
        template_values = {
            "id":                  industry.id,
            "name":                industry.name,
            "cycle_consume":       genCycleConsume(industry),
            "cycle_produce":       genCycleProduce(industry),
            "production_limit":    genProductionLimit(industry),
            "accept_cargo":        genCargoTypeAccept(industry),
            "produce_cargo":       genCargoTypeProduce(industry),
            "monthly_prod_change": genProdChange(industry),
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


def genProdChange(ind):
    return IndTemplate.monthly_prod_change.substitute(
        input=ind.input, output=ind.output
    )


def main(argv):
    print(generateIndustryNml(argv[1]))


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
