from types import SimpleNamespace
from string import Template

# fmt: off
CargoTable = SimpleNamespace(
    Passengers = "PASS",
    Coal       = "COAL",
    Mail       = "MAIL",
    Oil        = "OIL_",
    Livestock  = "LVST",
    Goods      = "GOOD",
    Grain      = "GRAI",
    Wood       = "WOOD",
    IronOre    = "IORE",
    Steel      = "STEL",
    Valuables  = "VALU",
)
# fmt: on

def generateCargoTable():
    cargoes = ""
    line = ""
    for cargo in CargoTable.__dict__.values():
        line += f"{cargo}, "
        if len(line) > 70:
            cargoes += line[:-1] + "\n    "
            line = ""

    cargoes += line[:-2]

    template = Template(
        "cargotable {\n"
        "    $cargoes\n"
        "}\n"
    )

    return template.substitute(cargoes=cargoes)
