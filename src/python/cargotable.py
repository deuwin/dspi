from enum import StrEnum, unique
import textwrap

# fmt: off
@unique
class CargoTable(StrEnum):
    Passengers = "PASS"
    Coal       = "COAL"
    Mail       = "MAIL"
    Oil        = "OIL_"
    Livestock  = "LVST"
    Goods      = "GOOD"
    Grain      = "GRAI"
    Wood       = "WOOD"
    IronOre    = "IORE"
    Steel      = "STEL"
    Valuables  = "VALU"
# fmt: on


def generate():
    cargoes = ", ".join([cargo for cargo in CargoTable])
    cargoes = "\n".join(
        textwrap.wrap(cargoes, initial_indent="    ", subsequent_indent="    ")
    )

    return f"cargotable {{\n{cargoes}\n}}"


def main(argv):
    print(generate())


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
