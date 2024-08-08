import sys
from dataclasses import dataclass
from string import Template

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
    item: Template = Template(
        """produce(${name}_produceCargo,
    [
        $cycle_consume
    ],
    [
        $cycle_produce
    ],
    0
)

switch(FEAT_INDUSTRIES, SELF, ${name}_calcProduction, [
    STORE_TEMP(GET_PERM(PRODUCTION_RATE), 0),
    $production_limit
]) { return ${name}_produceCargo; }

item(FEAT_INDUSTRIES, $name) {
    property {
        substitute: $id;
        override:   $id;
        cargo_types {
            $accept_cargo
            $produce_cargo
        };
    }
    graphics {
        build_prod_change:     initPermanentStorage;
        extra_text_industry:   genExtraText;

        produce_cargo_arrival: noProduction;
        produce_256_ticks:     ${name}_calcProduction();

        stop_accept_cargo:     $stop_accept_cargo;

        random_prod_change:    CB_RESULT_IND_PROD_NO_CHANGE;
        monthly_prod_change:   $monthly_prod_change
    }
}
"""
    )
    stop_accept_cargo: Template = Template(
        'stopAccept(incoming_cargo_waiting("$input"))'
    )
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
def generateIndustryNml(industry):
    template_values = {
        "id":                  industry.id,
        "name":                industry.name,
        "cycle_consume":       genCycleConsume(industry),
        "cycle_produce":       genCycleProduce(industry),
        "production_limit":    genProductionLimit(industry),
        "accept_cargo":        genCargoTypeAccept(industry),
        "produce_cargo":       genCargoTypeProduce(industry),
        "stop_accept_cargo":   genStopAccept(industry),
        "monthly_prod_change": genProdChange(industry),
    }

    return IndTemplate.item.substitute(template_values)
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


def genStopAccept(ind):
    if ind.id == "INDUSTRYTYPE_FACTORY":
        return "stopAcceptFactory()"
    else:
        return IndTemplate.stop_accept_cargo.substitute(input=ind.input)


def genProdChange(ind):
    return IndTemplate.monthly_prod_change.substitute(
        input=ind.input, output=ind.output
    )


def main(argv):
    if len(argv) == 1:
        for ind in INDUSTRIES:
            print(generateIndustryNml(ind))
    else:
        print(generateIndustryNml(argv[1]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
