from cargotable import CargoTable as Cargo


def genIsStockpileFull():
    cargo_cases = []
    for index, cargo in enumerate(Cargo):
        cargo_cases.append(
            f'    {index}: incoming_cargo_waiting("{cargo}") < STOCKPILE_LIMIT;'
        )
    cargo_cases = "\n".join(cargo_cases)

    # it feels like there should be a neater way to do this...
    return (
        "switch(FEAT_INDUSTRIES, SELF, isStockpileFull,\n"
        "    getbits(extra_callback_info2, 0, 8)\n"
        ") {\n"
        f"{cargo_cases}\n"
        "}\n\n"
    )


def main():
    print(genIsStockpileFull())


if __name__ == "__main__":
    import sys
    sys.exit(main())
