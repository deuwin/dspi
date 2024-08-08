import sys
from dataclasses import dataclass
from string import Template

from cargo import Cargo
from util.file import writeText


# fmt: off
@dataclass(frozen=True)
class Industry:
    id:     str
    input:  str | list[str]
    output: str

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
    # TODO: Implement NML functions to deal with multiple inputs
    # Industry(
    #     "INDUSTRYTYPE_FACTORY",
    #     [
    #         Cargo.Livestock,
    #         Cargo.Grain,
    #         Cargo.Steel,
    #     ],
    #     Cargo.Goods,
    # ),
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
        """item(FEAT_INDUSTRIES, $name) {
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
        produce_256_ticks:     $produce_256_ticks;

        stop_accept_cargo:     $stop_accept_cargo;

        random_prod_change:    CB_RESULT_IND_PROD_NO_CHANGE;
        monthly_prod_change:   $monthly_prod_change
    }
}"""
    )
    accept_cargo: Template = Template('accept_cargo("$input"),')
    produce_cargo: Template = Template('produce_cargo("$output", 0),')
    produce_256_ticks: Template = Template(
        'calcProduction(incoming_cargo_waiting("$input"))'
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


def generateIndustryNml():
    industry_items = ""
    for ind in INDUSTRIES:
        template_values = {
            "id":                  ind.id,
            "name":                ind.id[13:].lower(),
            "accept_cargo":        genAcceptCargo(ind),
            "produce_cargo":       genProduceCargo(ind),
            "produce_256_ticks":   genProduceCycle(ind),
            "stop_accept_cargo":   genStopAccept(ind),
            "monthly_prod_change": genProdChange(ind),
        }
        industry_items = (
            industry_items + IndTemplate.item.substitute(template_values) + "\n\n"
        )

    return industry_items


def genAcceptCargo(ind):
    template = IndTemplate.accept_cargo
    if type(ind.input) == list:
        accept_cargo = ""
        for input in ind.input:
            accept_cargo = (
                accept_cargo + template.substitute(input=input) + "\n" + " " * 12
            )
        return accept_cargo[:-13]
    else:
        return template.substitute(input=ind.input)


def genProduceCargo(ind):
    return IndTemplate.produce_cargo.substitute(output=ind.output)


def genProduceCycle(ind):
    if ind.id == "INDUSTRYTYPE_FACTORY":
        return "calcProductionFactory()"
    else:
        return IndTemplate.produce_256_ticks.substitute(input=ind.output)


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
        file_out = None
    else:
        file_out = argv[1]

    if file_out:
        writeText(file_out, industry_items)
    else:
        print(industry_items)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
