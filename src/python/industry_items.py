from string import Template
from functools import singledispatch

from industry import INDUSTRIES, Sector
from template_utils import getTemplate, getRatioString, cargoToPluralString


def generate():
    secondary_template = getTemplate("secondary")
    tertiary_template = getTemplate("tertiary")

    pnml = ""
    for industry in INDUSTRIES:
        match industry.sector:
            case Sector.Secondary:
                template = secondary_template
            case Sector.Tertiary:
                template = tertiary_template
            case _:
                raise NotImplementedError(
                    f'Cannot generate industry sector "{industry.sector.name}"!'
                )

        pnml += template.substitute(getTemplateMapping(industry))
        pnml += genIndustryTiles(industry)

    return pnml


# fmt: off
def getTemplateMapping(industry):
    if industry.sector == Sector.Secondary:
        return {
            "name":              industry.name,
            "produceblock":      genProduceBlock(industry),
            "update_stockpile":  genUpdateStockpile(industry),
            "input_output":      genInputOutput(industry),
            "power_limit":       genInputOutputPowerLimit(industry),
            "output_rate_max":   genOutputRateMax(industry),
            "stockpile_average": genStockpileAverage(industry),
            "output":            industry.output,
            "id":                industry.id,
            "cargo_types":       genCargoTypes(industry),
            "extra_text":        genExtraTextCall(industry),
        }
    else:
        return {
            "name":        industry.name,
            "id":          industry.id,
            "cargo_types": genCargoTypes(industry)
        }
# fmt: on


@singledispatch
def indent(lines, indent_level, start=1):
    for idx, line in enumerate(lines[start:], start=start):
        lines[idx] = "    " * indent_level + line
    return "\n".join(lines)


@indent.register
def _(text: str, indent_level, start=1):
    lines = text.splitlines()
    return indent(lines, indent_level, start)


def genProduceBlock(industry):
    consume = []
    for reg_idx, input in enumerate(industry.input):
        consume.append(f"{input}: getTemp(CONSUME_{reg_idx});")
    consume = "\n" + indent(consume, 1, start=0) + "\n"

    if industry.output:
        produce = f"\n    {industry.output}: getTemp(PRODUCE);\n"
    else:
        produce = ""

    block = f"[{consume}], [{produce}]"

    return indent(block, 1)


def genInputOutput(industry):
    if industry.ratio:
        return genInputOutputRatio(industry)
    else:
        return genInputOutputStandard(industry)


def genInputOutputStandard(industry):
    consume_str = (
        "setTemp("
            "CONSUME_{idx}, "
            'min(incoming_cargo_waiting("{input}"), getPerm(PRODUCTION_RATE))'
        "),"
    )
    consume_limits = []
    for idx, input in enumerate(industry.input):
        consume_limits.append(consume_str.format(idx=idx, input=input))

    produce_str = genProduceStringStandard(industry)
    return indent(consume_limits + [produce_str], 1)


def genProduceStringStandard(industry):
    produce_str = "setTemp(PRODUCE, "
    for idx in range(len(industry.input)):
        produce_str += f"getTemp(CONSUME_{idx}) + "
    return produce_str[:-3] + "),"


CONSUME_STR_RATIO = (
    "setTemp("
        "CONSUME_{idx}, "
        "getTemp(PRODUCE){ratio}"
    "),"
)

def genInputOutputRatio(industry):
    produce_str = "setTemp(PRODUCE, min(getPerm(PRODUCTION_RATE), min("
    proportion_out = industry.ratio[-1]
    consume_limits = []
    for idx, input in enumerate(industry.input):
        produce_str += (
            f'incoming_cargo_waiting("{input}")'
            f"{getRatioString(proportion_out, industry.ratio[idx])}, "
        )
        consume_limits.append(
            CONSUME_STR_RATIO.format(
                idx=idx,
                input=input,
                ratio=getRatioString(industry.ratio[idx], proportion_out)
            )
        )
    produce_str = produce_str[:-2] + "))),"
    return indent([produce_str] + consume_limits, 1)


def genInputOutputPowerLimit(industry):
    if industry.ratio:
        produce_str = genRegisterPowerLimit("PRODUCE")
        consume_str = CONSUME_STR_RATIO
    else:
        produce_str = genProduceStringStandard(industry)
        consume_str = genRegisterPowerLimit("CONSUME_{idx}")

    consume_limits = []
    for idx in range(len(industry.input)):
        values = {"idx": idx}
        if industry.ratio:
            values["ratio"] = getRatioString(industry.ratio[idx], industry.ratio[-1])
        consume_limits.append(consume_str.format(**values))

    if industry.ratio:
        power_limit = [produce_str] + consume_limits
    else:
        power_limit = consume_limits + [produce_str]

    return indent(power_limit, 2)


def genOutputRateMax(industry):
    output_rate_max = "getPerm(PRODUCTION_RATE)"
    if len(industry.input) > 1 and not industry.ratio:
        output_rate_max += f" * {len(industry.input)}"
    return output_rate_max


def genRegisterPowerLimit(register):
    return (
        f"setTemp({register}, "
            f"getTemp({register}) * getPowerSuppliedPct() / 100"
        "),"
    )


def genUpdateStockpile(industry):
    update_stockpile = []
    for idx, input in enumerate(industry.input):
        update_stockpile.append(
            f'updateStockpileAverage({idx}, incoming_cargo_waiting("{input}")),'
        )
    return indent(update_stockpile, 1)


def genStockpileAverage(industry):
    if industry.ratio:
        average_str = "getStockpileAverage(0)" + getRatioString(
            industry.ratio[-1], industry.ratio[0]
        )
        for idx in range(1, len(industry.input)):
            ratio = getRatioString(industry.ratio[-1], industry.ratio[idx])
            average_str = f"min(getStockpileAverage({idx}){ratio}, " + average_str + ")"
    else:
        average_str = "getStockpileAverage(0)"
        for idx in range(1, len(industry.input)):
            average_str = f"max(getStockpileAverage({idx}), " + average_str + ")"
    return average_str


def genCargoTypes(industry):
    accept_cargo = []
    for input in industry.input:
        accept_cargo.append(f'accept_cargo("{input}"),')
    accept_cargo = indent(accept_cargo, 3)

    produce_cargo = ""
    if industry.output:
        produce_cargo = indent(f'\nproduce_cargo("{industry.output}", 0),', 3)

    return accept_cargo + produce_cargo


def genExtraTextCall(industry):
    if len(industry.input) > 1:
        return f"{industry.name}_genExtraText()"
    else:
        return f"genExtraText({cargoToPluralString(industry.input[0])})"


def genIndustryTiles(industry):
    if not industry.tiles:
        return ""

    tile_items = ""
    tile_template = getTemplate("industry_tile")
    for idx, tile_id in enumerate(industry.tiles):
        tile_items += tile_template.substitute(
            name=industry.name, idx=idx, tile_id=tile_id
        )

    return tile_items


def main(argv):
    print(generate())


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
