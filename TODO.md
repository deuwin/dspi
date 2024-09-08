# TODO
Things to do, ordered roughly by importance. Nothing here is set in stone and
this list will be subject to many changes.

## Short Term
* Playtest production rate changes
* Playtest power requirements
* Extra cargo inputs for:
    * Steel Mill: Iron Ore and Coal
        * Apparently the real life ratio of Ore:Coal:Steel is about 1.6:0.77:1
          [^1][^2]
        * Probably should use 2:1:2 for gameplay reasons, especially given
          OpenTTD's tenuous grasp on
          [reality](https://web.archive.org/web/20190920110634/http://devs.openttd.org:80/~belugas/texts/realism_in_OpenTTD.txt)
    * Power Station: Coal and Oil
        * Dual fired power stations are a thing [^3]
        * Consumption options:
            * Burn both together?
            * Have one fuel as reserve?
* Temperate Farm: Make Grain and Livestock production rate the same?
* Temperate Oil Wells: Remove IND_FLAG_NO_PRODUCTION_INCREASE?

## Medium Term
* Production rate changes based off cargo delivered per month, not stockpile?
* Reimplement optional features from [BSPI.grf](https://www.tt-forums.net/viewtopic.php?t=84735)?
    * Valuables requirements to boost primary industries
    * Reserves for extractive industries
    * Fertility for organic industries
* Temperate Bank, two options:
    * production correlates to town size, or
    * act like a secondary industry

## Possible Ideas
* Acceptance limit for Goods in towns?
* Add support for all default landscapes/climates
    * Water Tower: Consumption correlates to town size
    * Toy Shop: Consumption correlates to town size?
* Randomise initial production rate?
* Parameter for production change frequency?
    * Standard, Keen, or Zealous/Intense/Fervid


[^1]: https://www.bhp.com/what-we-do/products/iron-ore
[^2]: https://www.bhp.com/what-we-do/products/metallurgical-coal
[^3]: https://en.wikipedia.org/wiki/Kingsnorth_power_station
