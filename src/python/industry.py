from enum import Flag, unique
from dataclasses import dataclass, InitVar, field

from cargotable import CargoTable as Cargo


# fmt: off
@unique
class Sector(Flag):
    # matches the definition in industry.pnml, if that ever becomes relevant
    Primary   = 0x01
    Secondary = 0x03
    Tertiary  = 0x02


@dataclass
class IndustryTile:
    """
    Storage for industry tile properties.
    https://newgrf-specs.tt-wiki.net/wiki/NML:IndustryTiles#Industry_tile_properties

    Args:
        Property arguments:
        id (int): Tile ID to override. A list of default industry tile IDs can
            be found here:
            https://newgrf-specs.tt-wiki.net/wiki/NML:Default_industry_tiles
            ID to position in layout is described here:
            https://newgrf-specs.tt-wiki.net/wiki/IndustryDefaultProps#Industry_Layouts
        info (str, optional): animation_info property.
        speed (int, optional): animation_speed property.
        triggers (list[str], optional): List of animation_triggers.

        Callback arguments:
        control (str, optional): anim_control callback.
        next_frame (str, optional): anim_next_frame callback.
        default (str, optional): default callback.
    """

    # properties
    id:         int
    info:       list[str|int] = None
    speed:      int = None
    triggers:   list[str] = None
    # callbacks
    control:    str = None
    next_frame: str = None
    default:    str = None


# specific industry tile definitions
def getPowerPlantTiles():
    return [
        # cooling tower
        IndustryTile(7),
        # chimney
        IndustryTile(
            id         = 8,
            info       = "[ANIMATION_LOOPING, 7]",
            speed      = 3,
            triggers   = ["ANIM_TRIGGER_INDTILE_CONSTRUCTION_STATE"],
            next_frame = "CB_RESULT_NEXT_FRAME",
            default    = "power_plant_getChimneyGraphics",
        ),
        # small building
        IndustryTile(9),
        # substation
        IndustryTile(
            id    = 10,
            info  = "[ANIMATION_LOOPING, 128]",
            speed = 2,
        ),
    ]


@dataclass(frozen=True)
class Industry:
    """
    Storage for basic data about each industry.

    Args:
        id (str): The industry identifier. Should be a string from the list of
            default industries. See:
            https://newgrf-specs.tt-wiki.net/wiki/NML:Default_industries
        input(str|list[str]): Cargo accepted by the industry.
        output(str): Cargo generated by the industry.
        tiles (list[IndustryTiles], optional): Industry tiles to override. Only
            required if you change accepted cargo from the default or wish to
            have custom animations.
        ratio (list[int], optional): Ratio of inputs consumed to output
            generated. e.g. A ratio of [2, 1, 2] consumes 2 units of input_0 and
            1 unit of input_1 to produce 2 units of output.
    """

    id:     str
    input:  str | list[str]
    output: str | None
    tiles:  list[IndustryTile] = None
    ratio:  list[int] = field(default=None)

    def __post_init__(self):
        # convert input if required
        input = [self.input] if isinstance(self.input, str) else self.input
        object.__setattr__(self, "input", input)

        # validate ratio
        if self.ratio and len(self.ratio) != len(self.input) + 1:
            raise ValueError("Incorrect ratio length!")

    @property
    def name(self):
        return self.id[13:].lower()

    @property
    def sector(self):
        sector = 0
        sector += 2 if self.input else 0
        sector += 1 if self.output else 0
        return Sector(sector)


def getBasicIndustryTiles(start, end):
    """
    Create a list of IndustryTile, populating only the ID.

    Args:
        start (int): The ID to start at.
        end (int): The ID to end with (inclusive).
    """

    tiles =  []
    for id in range(start, end + 1):
        tiles.append(IndustryTile(id))
    return tiles


# temperate industries
INDUSTRIES = [
    # secondary
    Industry(
        id     = "INDUSTRYTYPE_STEEL_MILL",
        input  = [
            Cargo.IronOre,
            Cargo.Coal,
        ],
        output = Cargo.Steel,
        tiles  = getBasicIndustryTiles(52, 57),
        ratio  = [2, 1, 2],
    ),
    Industry(
        id     = "INDUSTRYTYPE_SAWMILL",
        input  = Cargo.Wood,
        output = Cargo.Goods,
    ),
    Industry(
        id     = "INDUSTRYTYPE_TEMPERATE_FACTORY",
        input  = [
            Cargo.Livestock,
            Cargo.Grain,
            Cargo.Steel,
        ],
        output = Cargo.Goods,
    ),
    Industry(
        id     = "INDUSTRYTYPE_OIL_REFINERY",
        input  = Cargo.Oil,
        output = Cargo.Goods
    ),
    # tertiary
    Industry(
        id     = "INDUSTRYTYPE_POWER_PLANT",
        input  = [
            Cargo.Coal,
            Cargo.Oil,
        ],
        output = None,
        tiles  = getPowerPlantTiles(),
    ),
]
# fmt: on


def main(argv):
    for industry in INDUSTRIES:
        pprint.pprint(industry)


if __name__ == "__main__":
    import sys
    import pprint

    sys.exit(main(sys.argv))
