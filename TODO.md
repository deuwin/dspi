# TODO
Things to do, ordered roughly by importance. Nothing here is set in stone and
this list will be subject to many changes.

## Short Term
* Playtest production rate changes
* Playtest power requirements
* Implement multiple power stations per town

## Medium Term
* Fix Power Plant animation
    * Re-enable chimney and sparking animation
    * Stop animations if no fuel or demand
    * Continuous sparking if overloaded
* Production Change:
    * Limit to once every 12 months?
    * Occurs at least once every 60 months?
* Reimplement optional features from [BSPI]?
    * Valuables requirements to boost primary industries
    * Reserves for extractive industries
    * Fertility for organic industries
* Temperate Bank Production options:
    * correlates to town size,
    * proportional to amount of goods delivered to town,
    * linked to town industry production, or
    * smooth economy changes depending on valuables delivered/transported.
* Secondary industry spawning:
    * Minimum town population size?
    * Maximum distance from town?
* Anything that depends on town size should have a parameter toggle

## Possible Ideas
* Power Plant: Allow closure?
* Power Plant: Base demand based on town population?
* Temperate Farm:
    * Make Grain and Livestock production rate the same?
    * Split into separate Grain and Livestock farms?
* Temperate Oil Wells: Remove IND_FLAG_NO_PRODUCTION_INCREASE?
* Add support for all default landscapes/climates
    * Water Tower: Consumption correlates to town size
    * Toy Shop: Consumption correlates to town size?
* Secondary Industries:
    * No animation if no power or no input?
    * Randomise initial production rate?
* Parameter for production change frequency?
    * Standard, Keen, or Zealous/Intense/Fervid

[BSPI]: https://www.tt-forums.net/viewtopic.php?t=84735?

