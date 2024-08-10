from string import Template

from cargotable import CargoTable as Cargo


def genIsStockpileFull():
    cargo_cases = ""
    for index, cargo in enumerate(Cargo.__dict__.values()):
        cargo_cases += (
            f'    {index}: incoming_cargo_waiting("{cargo}") < STOCKPILE_LIMIT;\n'
        )

    template = """
switch(FEAT_INDUSTRIES, SELF, isStockpileFull,
    getbits(extra_callback_info2, 0, 8)
) {
$cargo_cases
}
"""

    return Template(template).substitute(cargo_cases=cargo_cases)


def main():
    print(genIsStockpileFull())


if __name__ == "__main__":
    import sys
    sys.exit(main())
