# 20: Trailer electrical system and energy model

Status: research record, 20 Nov 2026, reconciled with reports 19 and 21 the same day. It chose the 48 V system and showed that decision H3 passes, 25.1 h on the design hot day when new and 17.2 h at end of life.

It sizes the trailer's battery, system voltage, inverter-charger, solar, recharging and distribution against decision H3, now with report 19's HVAC and report 21's appliance picks in the model. The model is `research/models/20/energy.py`, its inputs are `research/models/20/loads.yaml` and its output is `research/models/20/energy.out`. The chosen products are in `research/20-electrical.yaml`. Prices are AUD including GST, checked 20 Nov 2026.

Every product reports 19 and 21 chose now carries their figures, and the provisional placeholders are gone. Two parts stay provisional because neither report gives a number: the heat pump's input on the cold day between 07:00 and 17:00, and the Combi's 12 V draw over the same hours. Report 19 gives the cold night only. Neither part enters an H3 check.

## Recommendation

| Item | Recommendation | Mass (kg) | Price (AUD) |
|---|---|---|---|
| Battery | Five Victron Lithium NG 51.2 V 100 Ah (BAT548110620), 25.6 kWh nominal, with a Lynx Smart BMS NG 500 A. Inside the cabin at floor level, centred at X 4,200 mm plus or minus 300 mm, in a sealed box vented outside | 185.0 batteries, 1.9 BMS, 18.0 box (est.) | 14,555 + 994 + 1,200 (est.) |
| System voltage | 48 V (51.2 V nominal). 24 V bus from two Orion-Tr 48/24-16, 12 V bus from two Orion-Tr 48/12-30 | 6.8 converters | 1,032 |
| Inverter-charger | Victron MultiPlus-II 48/6k5/100-50: 6.0 kW at 25 °C, 5.7 kW at 40 °C, 11 kW for 1 min, 100 A charger | 29.0 | 1,333 |
| Load management | Hard-wired holds on three contactors (oven, shower heater, background loads) plus Node-RED on the Cerbo GX. The hob has no power cap (report 21), so the shower heater is the load that drops | in the board | in the board |
| Solar | Four Sunman eArc 430 W (1,720 W) bonded to the roof, two strings of two, each on a SmartSolar MPPT 150/35 | 29.2 + 2.5 | 2,676 + 510 |
| Charging from the ute (car build TC01 and TW06) | Two Orion-Tr Smart 12/48-8 in the bike box front on the stock alternator: 720 W, 3.6 kWh on a 5 h drive. Upgrade: a Jaylec 240 A alternator and two more chargers, 7.2 kWh | 10.3 in the ute | 1,612 + 123 |
| Generator | Two Honda EU22i in parallel (3,600 W) | 42.2 | 3,700 |
| Shore power | 15 A appliance inlet, MultiPlus input limit set to the outlet | in the board | in the board |
| Whole electrical system | 16 trailer lines and 2 ute lines in `research/20-electrical.yaml` | 335.9 in the trailer (296.6 maker, 39.3 est.), against 183.9 in today's lines | 29,599 in the trailer plus about 5,000 to install (est.) |

Design days at the battery bus, from `energy.out`:

| Case | 24 h (kWh) | Worst 12 h (kWh) | Cold night, 17:00 to 07:00 (kWh) |
|---|---|---|---|
| Hot day, all electric, hot water from the Combi's 900 W element | 19.55 | 14.33 | - |
| Hot day, hot water from the Combi on diesel | 18.87 | 13.99 | - |
| Cold day, Combi D 6 E heats on diesel (as designed, H7) | 10.23 | 7.23 | 4.68 |
| Cold day, all electric, heat pump heating | 18.19 | 9.97 | 11.18 |

H3 for the chosen bank and one size each side:

| Check | Need (nominal kWh) | 4 modules, 20.5 kWh | 5 modules, 25.6 kWh | 6 modules, 30.7 kWh |
|---|---|---|---|---|
| Hot day all electric, 24 h, new | 22.6 | 0.91, fails | 1.13, passes | 1.36 |
| Hot day all electric, worst 12 h, end of life | 20.7 | 0.99, fails | 1.23, passes | 1.48 |
| Hot day, diesel hot water, 24 h, new | 21.8 | 0.94, fails | 1.17 | 1.41 |
| Cold night 14 h, diesel heating, end of life | 6.8 | 3.02 | 3.78, passes | 4.54 |
| Cold night 14 h, heat pump, end of life | 16.2 | 1.27 | 1.58, passes | 1.90 |
| Hot day from full, new and end of life (h) | | 17.2 and 11.8 | 25.1 and 17.2 | 29.4 and 24.6 |
| Mass and price of the modules | | 148 kg, 11,644 | 185 kg, 14,555 | 222 kg, 17,466 |

Figures are installed nominal over required nominal. Five modules meet H3 with 2.6 kWh a day of headroom at the bus. The inverter's worst managed load is 5,055 W on the hot day and 5,465 W on the all-electric cold day.

What fails or stays tight:

1. Four modules no longer meet H3. The hot day rose 2.4 kWh, mostly report 19's air-conditioner (8.4 kWh at 230 V against the 6 kWh placeholder) and report 21's showers (1.3 kWh against 0.8 kWh).
2. The generator pair puts a hot day back in 6.3 h with the loads off, but 8.4 h while the household runs, 0.4 h over the 8 h target. On any day with sun it is shorter (section 6).
3. One Orion-Tr 48/12-30 no longer carries the 12 V bus. reports 19 and 21 chose 12 V fans, a 12 V hood, a 12 V shower pump, a 12 V water pump and a 12 V bed lift. The worst living case is 33 A, so the design now has two converters (60 A).
4. The cold-day all-electric peak uses 96 % of the inverter's 40 °C rating. The inverter then sits in a 20 °C cabin, where it is rated 6.0 kW (91 %).

## 1. Energy model

### Method

`energy.py` builds a power trace for every load, minute by minute over 24 h, for four cases. The hot day is report 19's: 42 °C at 15:00, 27 °C at night, 1,000 W/m² of sun at noon, 24 °C inside. The cold night is report 19's: -5 °C for 14 h from 17:00 to 07:00, 20 °C inside. The cold day rises to 13 °C at noon (est.).

- `hot`: the hot day, all electric. The Combi D 6 E's element heats the water.
- `hot_diesel`: the same day with the Combi heating the water on diesel.
- `cold_diesel`: the cold day with the Combi heating the cabin and the water on diesel, as H7 designs it.
- `cold_hp`: the cold day, all electric. The heat pump heats and the element heats the water.

Each load is 230 V through the inverter (`ac`), straight off the 48 V bus (`dc`), or on the 24 V or 12 V bus through its converters (`dc24`, `dc12`). The model converts each minute to battery-bus power:

- Inverter loss at the actual load: loss = P0 + aP + bP², fitted to the 48/6k5's 28 W zero-load power and 96 % peak efficiency, with the peak at 2,000 W (est.). In the three electric-heating cases the inverter stays on all day. In `cold_diesel` it drops to its 8 W search mode whenever no 230 V load draws.
- Converters: 89 % for the 48/24 V pair and 87 % for the 48/12 V pair, plus 8.2 W of no-load draw for each pair (Orion-Tr datasheet).
- Battery: 96 % on discharge and on charge, from Victron's 92 % round trip. Usable is 90 % of nominal (H3). End of life is 80 % of nominal, the point to which Victron counts its 2,500 cycles. A battery inside the cabin is not derated for cold.

Report 19's air-conditioner input goes in hour by hour on the 230 V side, so the model adds the inverter loss itself. Report 19's own battery figure (9.0 kWh) assumed a flat 93 %. The model's figure for the same 8.40 kWh is about 9.0 kWh too, at a mean inverter efficiency of 93.5 %.

### Daily energy by load family (kWh, at each load's own supply)

| Load family | Hot, all electric | Hot, diesel hot water | Cold, diesel heating | Cold, heat pump |
|---|---|---|---|---|
| Air-conditioner, Mitsubishi MSZ-AP25 (report 19) | 8.40 | 8.40 | 0.05 standby | 7.29 |
| Ventilation, hood and sensors (report 19) | 0.41 | 0.41 | 0.40 | 0.40 |
| Fridge and freezer (report 13) | 1.55 | 1.55 | 0.90 | 0.90 |
| Kitchen: hob with a kettle on it, oven, microwave (report 21) | 1.95 | 1.95 | 2.15 | 2.15 |
| Showers, 2 x 20 min, DauerShower 2.0 (report 21) | 1.30 | 1.30 | 1.40 | 1.40 |
| Combi D 6 E: element for hot water, or its 12 V on diesel (report 19, report 21) | 0.70 | 0.03 | 0.52 | 0.83 |
| Laundry: one wash and one heat-pump dry (report 21) | 1.62 | 1.62 | 1.62 | 1.62 |
| Lights, desk, Starlink Mini, devices, lift bed | 1.49 | 1.49 | 1.57 | 1.57 |
| Water pumps and UV (report 21) | 0.03 | 0.03 | 0.03 | 0.03 |
| GX, BMS, alarms, charger standby, breakaway charger | 0.27 | 0.27 | 0.27 | 0.27 |
| Inverter loss, idle and search | 0.99 | 0.97 | 0.47 | 0.96 |
| Converter loss and idle | 0.82 | 0.83 | 0.83 | 0.75 |
| Total at the battery bus | 19.55 | 18.87 | 10.23 | 18.19 |

The basis for each row is in `loads.yaml`. The main ones:

- Air-conditioner: report 19's hourly input from `research/models/19/loads.out`, 8.40 kWh on the hot day and 6.14 kWh over the cold night. The cold day's 07:00 to 17:00 adds 1.15 kWh, report 20's estimate from report 19's heat loss (63 W/K with ventilation) and its COP of 2.9 at -5 °C rising to 4.8.
- Kitchen: report 21's hob, 1.2 kWh a day with hot drinks boiled in a kettle on it, and the Camec 053632's 0.6 kWh bake. A 5 min microwave reheat at 1,440 W (0.12 kWh) is report 20's addition. The cold day adds 0.2 kWh of hot drinks (est.).
- Showers: report 21's 0.7 kWh from a cold start and 0.6 kWh from a hot start, of which 0.024 kWh a shower is the 12 V pump and UV (est.). On the cold day both start cold.
- Hot water: report 21's 0.7 kWh by element, or 0.08 L of diesel and 0.03 kWh at 12 V. The cold day's colder inlet water (8 °C, est.) raises the element's share to 0.84 kWh. In `cold_diesel` the row is the Combi's 12 V for heating and water: report 19's 0.42 kWh over the night plus 0.10 kWh by day (est.).
- Laundry: report 21's cold-wash Camec at 0.2 kWh and the Haier heat-pump dryer at 1.4 kWh.

### Results

| Result | Hot, all electric | Hot, diesel hot water | Cold, diesel heating | Cold, heat pump |
|---|---|---|---|---|
| Daily total (kWh) | 19.55 | 18.87 | 10.23 | 18.19 |
| Worst 12 h window (kWh) | 14.33, from 07:00 | 13.99, from 07:00 | 7.23, from 07:00 | 9.97, from 16:46 |
| Cold night, 17:00 to 07:00 (kWh) | - | - | 4.68 | 11.18 |
| Scheduled peak at the inverter (W) | 3,059 | 2,850 | 2,405 | 3,042 |
| Worst coincident load the interlocks allow (W) | 5,055 | 5,055 | 4,065 | 5,465 |
| Nominal capacity for 24 h new (kWh) | 22.6 | 21.8 | 11.8 | 21.1 |
| Nominal capacity for the worst 12 h at end of life (kWh) | 20.7 | 20.2 | 10.5 | 14.4 |
| Nominal capacity for the cold night at end of life (kWh) | - | - | 6.8 | 16.2 |

On the hot day the battery gives 0.26 to 0.41 kWh an hour overnight. It gives 1.93 kWh between 07:00 and 08:00 (shower, breakfast, hot water) and 2.41 kWh between 18:00 and 19:00 (oven, hob and the air-conditioner's 912 W peak). From 10:00 to 13:00 it gives 1.5 kWh an hour while the dryer runs in the hottest part of the day.

### What a kWh a day costs in battery

For H3's 24 h case each extra kWh a day at the bus needs 1 / (0.96 x 0.90) = 1.16 kWh of nominal capacity. The NG module carries 7.23 kg per nominal kWh, so that is 8.4 kg of battery per kWh a day at the bus, or 8.8 kg per kWh a day of a 230 V load at 800 W. Report 19 used 7 kg. Use 8.8 kg for 230 V loads and 8.4 kg for DC loads. The battery comes in 37 kg modules, so a saving is real only when it removes a module or keeps a sixth one out.

### Updating the model

1. Change a load's figures in `loads.yaml` and keep its `id`, so the interlock rules still apply.
2. Run `timeout 120 uv run -q --with pyyaml python energy.py > energy.out` in `r20/`.
3. Read the battery table. Five modules hold while the all-electric hot day stays under 22.1 kWh at the bus (19.55 plus the 2.6 kWh headroom). Six are needed above that.
4. Read the managed peak against the inverter's 5,700 W at 40 °C, and the 12 V and 24 V bus checks under the hot case.

## 2. Battery

### Size

H3's governing case is the all-electric hot day for 24 h when new: 19.55 kWh at the bus, so 19.55 / 0.96 / 0.90 = 22.6 kWh nominal. The worst 12 h at end of life needs 20.7 kWh. The cold night needs 6.8 kWh on diesel heat and 16.2 kWh on the heat pump, both at end of life. Victron's 48 V modules come in 5.12 kWh steps.

Five modules (25.6 kWh, 185 kg):

- Four (20.5 kWh) fail both H3 checks: 0.91 of the 24 h need when new, and 11.8 h from full at end of life, under the 12 h minimum.
- Five pass every check. They run the hot day for 25.1 h from full when new and 17.2 h at end of life.
- Five carry the all-electric cold night 1.58 times over at end of life, so the diesel heater stays a backup, as H7 intends.
- The 2.6 kWh a day of headroom is 13 % of the day. It covers report 19's tropical day (9.9 kWh of air-conditioning at 230 V, 1.5 kWh more than the design day) or a second load of washing and drying.

A sixth module (+37 kg, AUD 2,911) gives 29.4 h new and 24.6 h at end of life, the full 24 h target even when old. H3 does not require it. Keep the box sized for six so it can be added later (open point 3).

### Options

AS/NZS 3001.2:2022 clause 5.4.12.3.1 requires every lithium battery in a caravan to comply with AS IEC 62619 as a battery, BMS included, not only its cells ([BMPRO guide quoting the clause](https://teambmpro.com/lithium-battery-guidelines-to-as-nz3001-22002/)). That is the first filter. The bank sizes are those that meet H3 at revision 2.

| Option | Bank for H3 | Mass | Size per module (mm) | Cycle life | Cold charging | Victron integration | AS IEC 62619 | Bank price (AUD) |
|---|---|---|---|---|---|---|---|---|
| Victron Lithium NG 51.2 V 100 Ah (chosen) | 5 x 5.12 = 25.6 kWh | 37 kg each, 185 kg ([datasheet](https://cdn.shopify.com/s/files/1/0497/4749/3026/files/Datasheet-Lithium-NG-batteries-12_8V-25_6V-51_2V-EN.pdf?v=1739576641), maker est.) | 235 x 648 x 162 | 2,500 at 80 % DoD to 80 % capacity | No heater. Charges from +5 °C | Native, through the Lynx Smart BMS NG, which also switches chargers and loads off | EN IEC 62619:2022 declared for every NG model, Oct 2025 ([declaration](https://www.victronenergy.com/upload/documents/Declaration-of-Conformity-Lithium-NG-Batteries.pdf)) | 14,555 + BMS 994 ([listing](https://energyconnections.net.au/products/victron-lifepo4-battery-51-2v-100ah-ng-next-gen)) |
| Victron SuperPack NG 51.2 V 100 Ah | 5 x 5.12 = 25.6 kWh | 41 kg each, 205 kg ([technical data](https://www.victronenergy.com/media/pg/Lithium_SuperPack_NG/en/technical-data.html)) | 871 x 198 x 173 | 2,500 at 80 % DoD | 260 W self-heating, charges below 0 °C after warming | Built-in BMS, Bluetooth and a feedback signal, no CAN. 50 A recommended per module | Battery pending, cells certified | 16,250 ([listing](https://energyconnections.net.au/products/victron-energy-lithium-superpack-51-2v-100ah-ng)) |
| Victron Lithium NG 25.6 V 300 Ah (24 V) | 4 x 7.68 = 30.7 kWh (three pass by 2 % only) | 52 kg each, 208 kg (datasheet) | 206 x 841 x 205 | As NG | As NG | As NG | Declared | 14,700 ([listing](https://energyconnections.net.au/products/victron-lifepo4-battery-25-6v-300ah-ng)) |
| Enerdrive B-TEC 24 V 150 Ah (24 V) | 7 x 3.84 = 26.9 kWh | 38.2 kg listed, likely shipping, 267 kg | Not checked | 2,500 at 80 % DoD ([listing](https://batteryspecialists.com.au/products/enerdrive-b-tec-24v-150ah-lithium-battery-epl-150bt-24v-g2)) | Not stated | Bluetooth only | Cells only (report 13) | 32,256 |
| Revolution Power Australia 48 V 100 Ah CAN | 5 x 5.12 = 25.6 kWh | 40 kg each, 200 kg ([listing](https://shop.revolutionpoweraustralia.com.au/products/48v-100ah-lithium-battery)) | Not published | 5,000 at 50 % DoD | No heater. Charges from 0 °C | CAN bus, protocol not stated | Not listed for this model (ISO 9001, CE, RoHS, UN38.3) | 27,990 |
| Itech World iTECH120X, 12 V 105 Ah, 4 in series | 5 strings x 5.38 = 26.9 kWh, 20 batteries | 10 kg each, 200 kg | Not checked | Not stated | Not stated | Bluetooth only | Certified ([listing](https://itechworld.com.au/products/itech120x-new-2025-model-lifepo4-105ah-lithium-deep-cycle-battery-with-bluetooth)) | 9,180 |
| DIY 16S EVE MB31 314 Ah, JK BMS | 2 packs x 16.08 = 32.2 kWh (one pack fails H3) | 5.6 kg a cell ([EV Lithium](https://www.evlithium.com/LiFePO4-Battery/eve-mb31-314ah-lifepo4-lfp-cell.html)), about 205 kg for two packs (est.) | Cell 174 x 72 x 207 | 8,000 (cell maker, stationary test) | Through a BMS heater output (not checked) | CAN to GX (not checked) | None for a home-built pack | About 9,000 ([pack listing](https://lifepo4.com.au/shop/lifepo4-battery/48v/15kwh/51-2v-314ah-16kwh-eve-8000-cycles-lifepo4-battery-copy/), 4,499 each) |

The Victron Lithium Smart 25.6 V 200 Ah is superseded by the NG and needs the older Lynx Smart BMS, so it is not taken further.

No maker publishes a road-vibration rating for any of these house batteries. Every lithium battery that ships has passed UN 38.3, which includes a vibration and a shock test, and that is the only common baseline. On corrugations the installation does the work: the box near the axle on the XT Air suspension, modules strapped to a rigid tray on rubber pads, flexible cables between modules, and every lug torqued, marked and checked after the first corrugated trip. Prismatic DIY cells add a compression frame and bolted cell terminals, which loosen under vibration, and a home-built pack cannot meet clause 5.4.12.3.1. The DIY pack is out.

The NG wins on compliance evidence, Victron integration, Australian stock and service, and serviceability: Victron calls it repairable, with a screwed cover, and a module can be replaced on its own. At 7.23 kg/kWh it is the lightest compliant 48 V option. The 24 V 300 Ah module is lighter at 6.77 kg/kWh, but it needs the 24 V system that section 3 rejects.

### Location

Put the bank inside the insulated cabin, at floor level, centred at X 4,200 mm plus or minus 300 mm (the axle group centre is X 4,196.9 mm). Within that band the ball load changes by at most 13 kg (calculated: 185 kg x 300 mm / 4,197 mm ball-to-axle). Each 100 mm forward adds 4.4 kg to the ball. The heaviest single item then sits where it changes the axle and ball loads least.

Inside wins on battery life and on the rules:

- Heat. On the design day the shade is 42 °C. An under-floor box also takes radiant heat from the road and the tyres, so the cells would sit at 45 to 55 °C (est.). The NG's limit is +50 °C for both charge and discharge (datasheet), and clause 5.4.12.2(c) requires the battery to operate inside the maker's temperature range. LiFePO4 also loses capacity faster at 45 °C than at 25 °C, in storage and in cycling ([Safari and Delacourt 2011](https://www.researchgate.net/publication/234891428_Aging_of_a_commercial_graphiteLiFePO4_cell)). Assume about twice the fade rate for each 10 to 15 °C of extra cell temperature (est.). Inside, the air-conditioner holds the cells near 24 °C.
- Cold. The NG will not charge below +5 °C. Under the floor on the -5 °C night it would need a 40 to 60 W pad heater every winter morning (model line BH-01, about 0.2 kWh) before the sun could charge it. Inside, the heated cabin keeps it above +5 °C whenever someone lives aboard.
- Space. The rear under-floor bay goes to report 21's 130 L grey tank once the battery moves inside.

What inside costs: about 0.6 m² of floor (est. box 900 x 700 mm) and a sealed, vented compartment.

### Compartment rules, AS/NZS 3001.2:2022

The clauses below are quoted in [BMPRO's guide](https://teambmpro.com/lithium-battery-guidelines-to-as-nz3001-22002/) and [Invicta's update](https://www.invictalithium.com.au/invicta-caravan-standards-update/).

| Clause | Rule | How the design meets it |
|---|---|---|
| 5.4.12.2 (a), (b) | The battery sits behind a wall, compartment or barrier that stops gases entering the habitable area | Sealed 2 mm aluminium box with a gasketed lid. Every cable enters through a gland |
| 5.4.12.2, Victorian regulator advice via CIV | Inside a cupboard, under a bed or under a seat is allowed if the box is sealed and vented outside | Two vents to outside through the floor, each at least 20 mm bore with insect mesh, one from the bottom of the box and one ducted from the top (est., open point 4) |
| 5.4.12.2 (c) | Operates inside the maker's temperature range and IP rating | Inside the conditioned cabin. NG is IP65 |
| 5.4.12.3.1 | A BMS, and AS IEC 62619 for the battery | Lynx Smart BMS NG, NG declared to EN IEC 62619:2022 |
| 5.4.12.3.3 | The BMS disconnects on over and under voltage, over and under temperature, and over current | Lynx Smart BMS NG 500 A contactor, plus its ATC and ATD outputs that stop chargers and loads first |
| 5.4.12.3.4 | A monitor that shows state of charge | Cerbo GX with GX Touch 50 |
| 5.4.7.2 | Battery fuse within 200 mm of the terminals, or directly outside the compartment, or within 1 m in a protective sleeve | 125 A MEGA per module in a 6-way holder at the bank busbar, module cables sleeved |
| 5.4.10.2 | Water, diesel and other metal service lines within 300 mm of the terminal face are shielded with dielectric material | Route the water and diesel lines at least 300 mm from the box's terminal side, or sleeve them |
| Access and labels (guide) | Access by a panel or hatch, a warning label if the hatch is not sealed, secure mounting | Lid on the top face, label on it, modules strapped to a tray bolted through the floor |

The quoted clauses set no separation from a sleeping area and no fire rating. Two design choices go beyond them: keep the box out of the bed's footprint, and line it with 3 mm ceramic-fibre paper, with a heat detector in the box wired to a Cerbo GX digital input as an alarm.

## 3. System voltage: 48 V

| | 24 V | 48 V (chosen) |
|---|---|---|
| Battery that meets H3 | 4 x NG 25.6 V 300 Ah, 30.7 kWh, 208 kg (three pass by 2 % only) | 5 x NG 51.2 V 100 Ah, 25.6 kWh, 185 kg |
| Inverter for the 5.5 kW managed peak | Two MultiPlus-II 24/5000 in parallel: 7.4 kW at 40 °C, 60 kg, 36 W idle, AUD 4,586 ([listing](https://energyconnections.net.au/products/victron-multiplus-ii-24v-5000va-120-50-230v-inverter-charger)) | One MultiPlus-II 48/6k5: 5.7 kW at 40 °C, 29 kg, 28 W idle, AUD 1,333 |
| Battery current at the 5.5 kW peak | About 250 A (calculated) | About 125 A (calculated) |
| Main cable, battery to inverter | 95 mm², about 0.95 kg/m (est.) | 50 mm², about 0.5 kg/m (est.) |
| Solar controllers | 2 x SmartSolar 150/45, 1,300 W each at 24 V | 2 x SmartSolar 150/35, 2,000 W each at 48 V |
| 24 V loads (fridge, freezer, lights, USB-C, Starlink, report 19's top-up fan and RESPA-CF2) | Straight off the bus | Two Orion-Tr 48/24-16 |
| 12 V loads (report 19's fans and hood, report 21's shower pump, water pump and bed, the Combi, the XT Air compressor) | Two Orion-Tr 24/12-30 or one Orion 24/12-70 | Two Orion-Tr 48/12-30 |
| Charging from the 12 V ute | Orion-Tr Smart 12/24-15, 360 W at 40 °C | Orion-Tr Smart 12/48-8, 360 W at 40 °C ([datasheet](https://www.victronenergy.com/upload/documents/Datasheet-Orion-Tr-Smart-DC-DC-chargers-isolated-250-400W-EN.pdf)) |
| Second alternator on the 1VD-FTV | M2K's SBC hybrid kits add a 24 V 150 or 200 A alternator that bolts on with no modification ([M2K](https://m2kinc.com/product/hybrid-12v-240a-24v-200a/)) | No 48 V kit for the 1VD-FTV found |
| Battery, inverter and converters | 208 + 60 + 3.6 = 272 kg | 185 + 29 + 6.8 = 221 kg |

48 V wins:

- One inverter does the job of two, at half the battery current, so cables, lugs and fuses are smaller.
- The 24 V layout needs a fourth large module to pass H3 with any margin, so it is now 51 kg heavier and the inverters cost AUD 3,253 more.
- Victron's larger inverters, controllers and the NG bank's 5.12 kWh steps all suit 48 V.

24 V would win only if the ute had to refill the trailer through M2K's 24 V alternator. Section 6 does not need that. The 48 V cost is the converter pairs: 6.8 kg, AUD 1,032 and 0.82 kWh a day of loss and idle (about 7 kg of battery). If the inverter fails, the 24 V and 12 V buses still run the fridge, freezer, lights, fans, pumps and Starlink.

Every 48 V part stays at extra-low voltage. The bank peaks at 56.8 V on charge, under the 120 V DC limit for ELV.

### What replaces each 24 V part in today's schedule

| Today (report 13, LA-04, UF-05) | At 48 V |
|---|---|
| 2 x Victron Lithium NG 25.6 V 200 Ah | 5 x Victron Lithium NG 51.2 V 100 Ah |
| MultiPlus-II 24/5000/120-50 | MultiPlus-II 48/6k5/100-50 |
| 2 x SmartSolar MPPT 150/45 | 2 x SmartSolar MPPT 150/35 (the 150/45 also works at 48 V, but 35 A is ample) |
| Orion-Tr Smart 12/24-15 in the trailer | 2 x Orion-Tr Smart 12/48-8, moved into the ute (TC01) |
| Orion 24/12-70 | 2 x Orion-Tr 48/12-30 for the 12 V bus, plus 2 x Orion-Tr 48/24-16 for the 24 V bus |
| Lynx Smart BMS NG 500 A, Lynx Distributor, Cerbo GX | Unchanged. The BMS detects 12, 24 or 48 V, and the Cerbo runs from 8 to 70 V |
| 24 V fridge, freezer, LED lights | Unchanged, on the 24 V bus |
| 12 V products reports 19 and 21 chose | On the 12 V bus. Report 19's note to feed the LUNOS controller from the Orion 24/12-70 now means the 48/12-30 pair |

## 4. Inverter-charger and load management

### Coincident peak with the real appliances

| Load | Peak (W) | Source |
|---|---|---|
| Air-conditioner, Mitsubishi MSZ-AP25 | 990 cooling, 1,400 heating, never shed | Report 19 |
| Dometic CVI1525 hob, both zones at level 9 | 2,300, no user power cap | Report 21 |
| Camec 053632 oven and microwave (one appliance) | 1,440 | Report 21 |
| DauerShower 2.0 heater | 2,400 | Report 21 |
| Truma Combi D 6 E element | 900, or 1,800 on its high setting | Report 21 |
| Haier heat-pump dryer | 1,000 (est.) | Report 21 |
| Camec washer, cold wash | 280 | Report 21 |
| Monitor and user outlets | 325 (300 W allowance for small appliances, est.) | Report 20 |

All at once that is 10,535 W on the hot day, nearly twice the inverter. Report 21 found the hob has no setting that caps its total, so revision 1's kitchen cap is gone. The rules below keep the worst allowed case at 5,055 W on the hot day and 5,465 W on the all-electric cold day. `energy.py` tests every combination of the heavy loads against the rules.

| Rule | What it prevents | How |
|---|---|---|
| Background loads (Combi element, washer, dryer) run only while no cooking appliance and no shower heater draws | Background heat on top of cooking or a shower | Hard-wired: current relays on the hob, oven and shower circuits open contactor S1, which feeds the three background circuits |
| The oven-microwave and the shower heater lock each other out. The first one on keeps running | Shower and oven together | Hard-wired: the shower's current relay opens K2 on the oven circuit, and the oven's current relay opens K4 on the shower heater |
| Above 1 kW on the hob, the shower heater drops out | Shower plus a hob at full power | Hard-wired: the hob's current relay, set at about 4.5 A, opens K4. The DauerShower keeps running on boiler water (open point 2) |
| Total 230 V load above 5.5 kW for 5 s | Anything the rules miss, such as a toaster on a bench outlet | Node-RED on the Cerbo GX opens S1, then K4, then K2, and closes them 5 min after the load falls below 4.0 kW |
| State of charge below 30 % | Running the bank flat | Node-RED holds S1 off and raises the air-conditioner's setpoint 2 K (report 19's low-battery mode, through the optional CN105 interface, otherwise an alarm). Below 15 %, an alarm, and heating and hot water go to diesel. The BMS's ATD output stops loads at its cell limit |

The worst allowed cases are then:

- Cooking: air-conditioner, hob at 2,300 W, oven at 1,440 W and 325 W of small loads, 5,055 W. On the cold day with the heat pump at 1,400 W, 5,465 W.
- Shower: air-conditioner, shower heater, hob held to 1,000 W and small loads, 4,715 W.
- Background: air-conditioner, element at 1,800 W, dryer, washer and small loads, 4,395 W.

The contactors are 25 A, 230 V, with 24 V DC coils. The hard-wired holds work with the Cerbo off. Node-RED drives the same coils through the Cerbo's two relays (6 A up to 30 V DC) and a small 24 V relay module (in E-12). The air-conditioner is never switched off by the load management. The MultiPlus carries 11 kW for 1 min, so Node-RED's 5 s delay is safe, and the inverter's own overload protection is the last line.

### Inverter-charger options

| Unit | At 25 °C | At 40 °C | Peak | Zero load (AES) | Charger | Mass | Price (AUD) | Against 5,465 W |
|---|---|---|---|---|---|---|---|---|
| MultiPlus-II 48/5000/70-50 | 4.0 kW | 3.7 kW | 9 kW | 18 W (12 W) | 70 A | 30 kg | 1,152 | Too small |
| MultiPlus-II 48/6k5/100-50 (chosen) | 6.0 kW | 5.7 kW | 11 kW for 1 min | 28 W (18 W) | 100 A | 29 kg | 1,333 | 91 % at 25 °C, 96 % at 40 °C |
| Quattro-II 48/5000/70-50/50 | 5 kVA class (not checked) | Not checked | Not checked | Not checked | 70 A | Not checked | 1,624 | Two AC inputs, too small |
| Two MultiPlus-II 48/5000 in parallel | 8.0 kW | 7.4 kW | 18 kW | 36 W (24 W) | 140 A | 60 kg | 2,304 | Fits, 31 kg heavier |
| MultiPlus-II 48/8000/110-100 | 6.4 kW | 5.5 kW | 15 kW | 29 W (19 W) | 110 A | 42 kg | 2,116 | 99 % at 40 °C, 13 kg heavier |
| MultiPlus-II 48/10000/140-100 | 8.0 kW | 7.0 kW | 18 kW | 38 W (27 W) | 140 A | 49 kg | 2,527 | Fits, 20 kg heavier |

Ratings are from Victron's datasheets ([main range](https://www.victronenergy.com/upload/documents/Datasheet-MultiPlus-II-inverter-charger-EN.pdf), [4k5, 6k5 and 10k](https://www.victronenergy.com/upload/documents/Datasheet-MultiPlus-II-inverter-charger-4k-4k5-6k5-10k-EN-.pdf)). Prices are Energy Connections listings ([6k5](https://energyconnections.net.au/products/victron-multiplus-ii-48-6k5-100-50-230v-inverter-charger), [48/8000](https://energyconnections.net.au/products/victron-multiplus-ii-48v-8000va-110-100-230v-inverter-charger)).

The 48/6k5 stays. It is the lightest and cheapest unit that carries the managed peak. The 96 % figure applies only on the all-electric cold day, when the inverter sits in a 20 °C cabin and is rated 6.0 kW. On the hot day it carries 5,055 W, 89 % of its 40 °C rating. Mount it on the board (LA-04) with 150 mm clear above and below for its fan (est.), on the living side, away from the wet room.

The charger never limits recharging. The input current limit does, set from the GX: 10 A or 15 A on shore power, 15.6 A for the two EU22i. PowerControl gives the loads what they need and charges with the rest.

## 5. Solar

### Array

The free roof is 4,108 x 2,168 mm, 8.91 m². Report 19 kept it free of hatches and roof units. The Sunman eArc SMF430F-12X12UW stays: 430 W on 2,054 x 1,084 mm, 193 W/m², 7.3 kg, bonded with no frame joints to fatigue (report 13 section 4), AUD 669 ([Solar4RVs](https://www.solar4rvs.com.au/products/sunman-earc-430w-flexible-solar-panel-1)). Semi-flexible panels with higher-efficiency cells exist, but they have no comparable hail rating or record on RV roofs.

String rule at 48 V: each string is at least two 430 W panels in series. Two give Vmp 84 V and Voc 99.6 V at 25 °C, about 110 V at -10 °C (est., -0.3 %/K on Voc), inside the MPPT 150's 150 V limit. On a 70 °C panel the string's Vmp falls to about 70 V (est., -0.38 %/K), still above the 62 V the controller needs at 56.8 V absorption. Three in series reach about 165 V when cold and need a 250 V controller. One panel alone cannot charge a 48 V bank.

| Share of the free roof | Area | By area | Practical layout | Controllers |
|---|---|---|---|---|
| 100 % | 8.91 m² | 1,720 W | 4 x 430 W, two strings of two (chosen) | 2 x SmartSolar MPPT 150/35 |
| 85 % | 7.57 m² | 1,460 W | 3 x 430 W in one string, 1,290 W. Add smaller eArc panels in a second string only if three or more of one model fit the leftover strip | 1 x SmartSolar MPPT 250/60, AUD 568 ([listing](https://www.solar4rvs.com.au/products/victron-smartsolar-mppt-250-60-mc4-12-24-48v-60a-b)), plus a 150/35 for any second string |
| 70 % | 6.23 m² | 1,200 W | 2 x 430 W in one string, 860 W, plus a second string of smaller eArc panels to reach about 1,200 W | 2 x SmartSolar MPPT 150/35 |

Each 2-panel string draws 16.5 A at 52 V on a 35 A controller, so the controllers never limit. Two controllers keep a shaded pair from pulling down the other, and either one alone still charges. AS/NZS 3001.2 asks for PV fuses where circulating current can flow between paralleled strings ([BMPRO](https://teambmpro.com/12v-guru-as-nzs-3001-2-electrical-installations-what-does-it-all-mean/)). With one string per controller there is none, so no string fuses are needed. The PV cable is double insulated and UV rated. Fit a DC isolator for each string at the board (design choice). If report 25's roof study changes the roof, use the 85 % or 70 % row.

### Yield

PVGIS 5.3, ERA5 data, horizontal, building-mounted (bonded panels run hot), 14 % system loss ([PVGIS API](https://re.jrc.ec.europa.eu/api/v5_3/PVcalc)). The design hot day uses report 19's sun (1,000 W/m² at noon, 12 h half-sine, 7.64 kWh/m²) at Alice Springs' January ratio of 0.704 kWh per kWp per kWh/m².

| Day | kWh/kWp | 100 % (1.72 kWp) | 85 % (1.46 kWp) | 70 % (1.20 kWp) |
|---|---|---|---|---|
| Design hot day | 5.38 | 9.3 | 7.9 | 6.5 |
| Alice Springs, January mean | 5.16 | 8.9 | 7.5 | 6.2 |
| Alice Springs, July mean | 3.24 | 5.6 | 4.7 | 3.9 |
| Broome, January mean (wet season) | 4.39 | 7.6 | 6.4 | 5.3 |
| Broome, July mean | 3.64 | 6.3 | 5.3 | 4.4 |
| Hobart, January mean | 4.86 | 8.4 | 7.1 | 5.8 |
| Hobart, June mean | 1.04 | 1.8 | 1.5 | 1.2 |

On the design hot day the roof covers 48 % of the 19.55 kWh. The bank then falls about 10 kWh a day, so a run of design hot days lasts about 2.2 days from full before the generator runs. In a Hobart June the roof covers 10 % of a heat-pump day (18.2 kWh) and 18 % of a diesel-heated day (10.2 kWh): about 1.4 and 2.7 days from full.

Portable ground panels, optional: four 200 W folding panels in series (about 800 W, 20 to 25 kg, est.) into a third SmartSolar MPPT 150/35 through a PV inlet on the kerb side. Tilted towards the sun they give about 4.5 kWh on a clear summer day and about 1.6 kWh on a Hobart winter day (est., 5.5 and 2.0 kWh/kWp). Carry them only for long winter stays, because they weigh as much as three roof panels.

## 6. Recharging

An all-electric design hot day takes 19.55 kWh from the bus, so 21.2 kWh has to go back in at the battery terminals (19.55 / 0.96 / 0.96). The household averages 815 W while it charges. The MultiPlus charger delivers about 93 % of its AC input to the battery (est.).

### Generator

| Option | Rated output | Mass | Fuel at rated load | Noise | Price (AUD) | Refill, loads off | Refill, household running | Fuel per refill |
|---|---|---|---|---|---|---|---|---|
| One Honda EU22i (today) | 1,800 W | 21.1 kg | 1.2 L/h (3.6 L tank lasts 3.0 h) | LwA 89 dB(A) | 1,799 | 12.7 h | 24.7 h | 30 L |
| Honda EU32i | 2,600 W | 26.5 kg | 1.4 L/h (4.7 L lasts 3.3 h) | LwA 91 dB(A), 58 dB(A) at 7 m | 3,799 | 8.8 h | 13.2 h | 19 L |
| Two Honda EU22i in parallel (chosen) | 3,600 W | 42.2 kg plus cable | 2.4 L/h | LwA about 92 dB(A) (est., two sources) | 3,550 for two plus about 150 for the cable (est.) | 6.3 h | 8.4 h | 20 L |

Sources: Honda Australia specifications for the [EU22i](https://powerequipment.honda.com.au/models/generators/eu22/specifications) and [EU32i](https://powerequipment.honda.com.au/models/generators/eu32/specifications), the EU32i's 2,600 W rating ([spec sheet](https://anythingmarketplace.com.au/wp-content/uploads/2026/09/Honda-EU32i-Spec-Sheet.pdf)) and noise at 7 m ([Ritz Marine](https://ritzmarine.com/product/honda-eu32i-portable-inverter-generator/)), and Generator Store's prices ([EU22i pair](https://generatorstore.com.au/products/honda-eu22i-inverter-generator-twin-combo-pack), [EU32i](https://generatorstore.com.au/products/honda-eu32i-3200-watt-inverter-generator)). Honda pairs two identical units with a parallel cable ([Honda](https://powerequipment.honda.com/generators/generator-parallel-capability)).

The pair puts a full hot day back into the battery in 6.3 h of running. With the household running at the same time it takes 8.4 h, 0.4 h over the 8 h target. Two EU32i (53 kg, AUD 7,750) would bring that to about 5.3 h, but they add 11 kg and AUD 4,050 for a case that never happens alone: on a day with any sun the roof does part of the work. On the design hot day the roof's 9.3 kWh leaves about 11.9 kWh for the generators, about 4.7 h. Keep the pair. The pair also keeps the EU22i already in the schedule, gives two one-person lifts of 21 kg, and still charges at 1.7 kW if one unit fails. Set the MultiPlus input limit to 15.6 A for the pair.

The drawbar box DX-01 must hold two EU22i (each 509 x 290 x 425 mm) plus the fuel, or the second unit rides in the ute. That is +21.1 kg ahead of the axle, about +14.5 kg on the ball (calculated: 21.1 kg x (4,197 - 1,310) / 4,197 mm, with the box centred at X 1,310 mm). The generators run outside the box.

### Shore power

Fit a 15 A appliance inlet. On a 15 A park outlet the MultiPlus takes 3.45 kW and refills a hot day in 6.6 h, or 8.9 h with the household running. On a 10 A outlet, through a compliant adaptor with its own RCD and 10 A breaker, set the input limit to 10 A: 9.9 h, or 16.0 h. The charger's 100 A never limits.

### Charging from the ute while driving

The 2017 79's alternator is 1,560 W, about 110 A at 14 V (Toyota BBGJ1007, report 16). SBC puts the 1VD-FTV's alternators at up to 150 A and about 90 A at idle ([SBC brochure](https://smartbatterycharger.ae/wp-content/uploads/2022/03/1VD-FTV_Brochure.pdf)). While towing on a hot night the ute itself uses about 40 to 50 A: engine management, the air-conditioner blower, lights, trailer lights and the brake controller (est.). A hot alternator gives about 85 to 90 % of its rating (est.). That leaves about 50 to 60 A to spare at cruise.

| Option | Charge power | kWh on a 5 h drive | Car-side mass | Price (AUD) | Record and service |
|---|---|---|---|---|---|
| Two Orion-Tr Smart 12/48-8 on the stock alternator (chosen, TC01 and TW06) | 720 W | 3.6 | 10.3 kg | 1,735 with fitting | Victron, Australian stock. Draws about 62 A at 13 V, at the edge of the spare current |
| Upgrade: Jaylec BKS-240LC 240 A alternator and four Orion-Tr Smart 12/48-8 | 1,440 W | 7.2 | About 14 kg | 1,735 + 795 + 928 = 3,458 | Jaylec Black Series, Australian, 240 A cold and 218 A hot ([listing](https://www.marks4wd.com/engine/alternators/), [AAAA magazine](https://issuu.com/aaaa710/docs/aaam_april_2023_ezine/53?e=58&o=1)). Listed for the VDJ LandCruiser |
| SBC-T4.5TD-250XP direct-fit 250 A alternator | As the Jaylec | As the Jaylec | About 8 kg alternator | Price not found | 185 to 220 A at idle, Denso parts, US maker with no Australian agent ([SBC data](https://smartbatterycharger.ae/wp-content/uploads/2022/03/1VD-FTV_TDS.pdf)) |
| M2K SBC hybrid kit: 12 V 240 A plus a 24 V 200 A second alternator | About 3.5 to 5 kW (est.) | 17 to 25 (est.) | Not found | Not found | Bolts on with no modification ([M2K](https://m2kinc.com/product/hybrid-12v-240a-24v-200a/)). Suits only a 24 V trailer |
| Nations 48 V 100 A alternator with a Wakespeed WS500 | Over 5.5 kW claimed | Up to 27 | Not found | Not found | Kits only for Transit, Sprinter and ProMaster vans ([Nations](https://www.nationsstarteralternator.com/Dodge-Ram-Promaster-48-Volt-Dual-Alternator-Kit-p/0142-51v-hpx100.htm)). No 1VD-FTV bracket |
| Integrel E-Power | 7 to 9 kW | - | - | - | A marine system on boat engines ([Integrel](https://integrelsolutions.com/faqs/)). No road-vehicle use found |

On a 5 h tow the chargers put in 3.6 kWh. The trailer meanwhile runs report 19's RESPA-CF2 at 144 W (0.81 kWh through the 24 V converters), the fridge and freezer (about 0.33 kWh) and standby (about 0.1 kWh), so the battery gains about 2.4 kWh (est.).

### Car build lines TC01 and TW06

Recommendation: two Orion-Tr Smart 12/48-8 on the stock alternator. Nothing on the engine changes, and both parts are Victron with Australian stock. The chargers sit together in a vented cover in the bike box front, not in the engine bay, because the Orion-Tr is IP43 and derates above 40 °C. The 12 V run from the battery is short and heavy, and the long run to the towbar is at 48 V, where 16 A loses about 8 W in the cable instead of about 70 W at 62 A and 12 V over 6 B&S (calculated). Both runs are sized now for the upgrade, so the upgrade later adds only the alternator and two chargers. This replaces report 23's AUD 3,500 placeholder for TC01 and its TW06 feed (6 B&S, 50 A fuse at the battery, AUD 250 est.).

TC01, chargers and their 12 V side (prices Solar4RVs listings unless marked, 20 Nov 2026):

| Part | Qty | AUD | Source |
|---|---|---|---|
| Victron Orion-Tr Smart 12/48-8 isolated charger, 1.8 kg each | 2 | 651.90 | [Solar4RVs](https://www.solar4rvs.com.au/products/victron-12v-to-48v-orion-tr-8a-380w-isolated-charger), 325.95 each. AUD 356 each at [Energy Connections](https://energyconnections.net.au/products/victron-orion-tr-smart-12-48-8a-380w-isolated-dc-dc-charger) |
| ANL holder and 100 A ANL fuse at the ute battery | 1 | 17.80 | [holder](https://www.solar4rvs.com.au/products/exotronic-anl-fuse-holder), [fuse](https://www.solar4rvs.com.au/products/exotronic-anl-fuse-100a) |
| 2 B&S (32 mm²) single-core cable, red and black, 3 m each | 6 m | 89.40 | [Solar4RVs](https://www.solar4rvs.com.au/products/2bs-red-single-core-automotive-cable-per-metre), 14.90 a metre |
| 4-way MIDI holder with cover and two 50 A MIDI fuses, one per charger input | 1 | 36.80 | [holder](https://www.solar4rvs.com.au/products/exotronic-4-way-midi-fuse-holder-with-cover), [fuse](https://www.solar4rvs.com.au/products/exotronic-midi-ami-ans-fuse-50a) |
| 6 B&S twin tails to the charger inputs | 2 m | 29.80 | [Solar4RVs](https://www.solar4rvs.com.au/products/6bs-twin-core-automotive-cable-per-metre) |
| 3 mm twin cable, ignition signal to both remote inputs | 5 m | 16.00 | [Solar4RVs](https://www.solar4rvs.com.au/products/3mm-twin-core-automotive-cable-per-metre) |
| Mounting plate and vented cover in the bike box front | 1 | 60 | Estimate |
| Lugs, glue-lined heat shrink, grommets, rubber-lined clips | 1 | 60 | Estimate |
| Auto electrician, 5 h at AUD 130 an hour, TW06 included | 1 | 650 | Estimate |
| TC01 total, 8.4 kg (3.6 maker, 2.1 calculated, 2.7 est.) | | 1,612 | |

TW06, revised, the 48 V feed to the towbar: two inline MIDI holders with 23 A fuses on the chargers' outputs (21.60), 7 m of 8 B&S twin cable (69.30 at 9.90 a metre), a grey Anderson SB50 in a flush-mount panel at the towbar (12.00) and clips (20, est.). AUD 123 and 1.9 kg. Sources: [8 B&S twin](https://www.solar4rvs.com.au/products/8bs-twin-core-automotive-cable-per-metre), [Anderson panel](https://www.solar4rvs.com.au/products/exotronic-flush-mount-50a-anderson-plug-panel), [inline MIDI holder](https://www.solar4rvs.com.au/products/exotronic-midi-in-line-single-ami-ans-fuse-holder), [23 A MIDI fuse](https://www.solar4rvs.com.au/products/exotronic-midi-ami-ans-fuse-23a-m6). The grey housing does not mate with the red 12 V ones, so a 12 V accessory cannot plug into 48 V.

Ute side in all: AUD 1,735 and 10.3 kg.

Setting up: wire both chargers' remote inputs to an ignition-switched feed, and set their engine-running detection to start above 13.8 V and stop below 13.3 V (est.), so they back off before the ute's own system sags. On the first hot night tow, log the ute's battery voltage with both running. If it stays under 13.3 V, run one charger until the upgrade.

Upgrade path (report 23's RF14): fit the Jaylec BKS-240LC Black Series 240 A alternator in place of the factory type (RF04), AUD 795 including GST (AUD 722.73 before tax at [Marks 4WD](https://www.marks4wd.com/engine/alternators/), 20 Nov 2026), then add two more Orion-Tr Smart 12/48-8 (651.90), a 150 A ANL fuse (7.90), two 50 A MIDI fuses (7.80) and 2 h of fitting (260, est.). Charging doubles to 1,440 W, 7.2 kWh on a 5 h drive, drawing about 130 A from an alternator that gives 218 A hot. The 2 B&S feed carries 130 A with a 0.4 V drop and the 8 B&S run carries 32 A with a 1.0 V drop, 2 % of 48 V (calculated), so neither changes. The ute side then weighs about 14 kg. Take the upgrade if travel days must refill more than about 3.6 kWh, or if the voltage log shows the stock alternator cannot carry two chargers.

## 7. Distribution and protection

### Single-line structure (for CT-601)

1. Battery box: five NG modules in parallel. Each positive runs through its own 125 A MEGA fuse in a 6-way holder at the bank busbar, on 25 mm² cable under 1 m long in a sleeve (clause 5.4.7.2). The negatives join on a negative busbar. The modules' BMS cables daisy-chain to the BMS. The sixth holder position is spare.
2. A manual battery isolator rated 300 A at 60 V DC (design choice), then the Lynx Smart BMS NG 500 A: contactor, shunt, pre-alarm, ATC and ATD outputs. Its 1.1 A AUX output feeds the Cerbo GX.
3. Lynx Distributor with four MEGA positions: the MultiPlus-II, the MPPT fuse block, the converter fuse block, and the ute charging feed.
4. MultiPlus-II 48/6k5. AC-in from the 15 A appliance inlet through a 16 A RCBO. AC-out-1 feeds the 230 V board, where every circuit has a 30 mA RCBO and the board is labelled as inverter-supplied. AC-out-2, live only on shore or generator power, stays spare.
5. Two SmartSolar MPPT 150/35, one per 2-panel string, each with a DC isolator.
6. Two Orion-Tr 48/24-16 in parallel (760 W at 40 °C) feed the 24 V fuse panel. Two Orion-Tr 48/12-30 in parallel (720 W at 40 °C) feed the 12 V fuse panel. Victron allows any number of these converters in parallel ([Victron](https://www.victronenergy.com/dc-dc-converters/orion-tr-dc-dc-converters-isolated)).
7. Ute link: the 12-pin plug (lights, brakes, the breakaway switch circuit) and a grey Anderson SB50 carrying 48 V from the chargers in the ute to the Lynx Distributor. Assume the Bosch TSC takes its 12 V from the ute's harness, as a TSC wiring specification shows ([spec](https://cdn.shopify.com/s/files/1/1726/5421/files/TSC_Spec_2016.pdf?10624359704334232082)). Cruisemaster confirms at purchase. The breakaway kit keeps its own battery, float-charged from the 12 V bus.

### DC buses

The 12 V bus carries report 19's LUNOS e2 pairs, RA 15-60 and 5/UNI-FT controller, the range hood, the CO2 sensor and pressure display, report 21's DauerShower pump and controls, Shurflo water pump, UV purifier, transfer pump, Thetford flush and HappiJac bed, the Truma Combi D 6 E, the XT Air compressor, the alarms and tracker, the breakaway charger and a 10 A external outlet. The 24 V bus carries the fridge, freezer, lights, USB-C outlets, the Starlink Mini, report 19's top-up fan and the RESPA-CF2.

| Check, from `energy.out` | Demand | Against the converter pair |
|---|---|---|
| 12 V, worst living case: shower pump 10 A, water pump, UV, hood, Combi starting at 8 A (est.), fans, alarms, flush | 408 W, 33 A | 56 % of 60 A. One converter (30 A) would not carry it |
| 12 V, the same with the XT Air compressor levelling (25 A, est.) | 708 W, 58 A | 97 % |
| 12 V, the same plus the external outlet at its 10 A fuse | 828 W, 68 A | 113 %, inside the 80 A 10 s rating only briefly. Level the trailer before showering |
| 24 V, worst parked case: fridge, freezer, lights, two laptops, phones, Starlink, top-up fan | 453 W, 19 A | 58 % of 32 A |
| 24 V, parked dust storm with the RESPA-CF2 starting (288 W) | 741 W, 31 A | 96 % for the start, 77 % running |
| 24 V, towing: fridge, freezer, Starlink, RESPA-CF2 starting | 488 W, 20 A | 63 % |

### Main cables and fuses

Calculated from the current, then rounded up. The installing electrician checks each against AS/NZS 3008.1.1 for the installed conditions.

| Run | Design current | Fuse | Cable |
|---|---|---|---|
| Each module to the bank busbar | 100 A (1C) | 125 A MEGA | 25 mm² |
| Bank busbar to the BMS | 150 A continuous, 260 A for 1 min at the 11 kW peak | Module fuses, BMS contactor | 70 mm² |
| Lynx Distributor to the MultiPlus-II | 144 A at 6 kW and 44 V | 200 A MEGA | 50 mm², 2 m each way, 0.2 V drop |
| Each MPPT 150/35 | 35 A | 40 A MIDI | 10 mm² |
| Each converter input | 9 A | 15 A | 4 mm² |
| 24 V pair to its fuse panel | 32 A | 40 A | 10 mm² |
| 12 V pair to its fuse panel | 60 A | 80 A | 16 mm² |
| Ute charging feed, drawbar Anderson to the Lynx Distributor | 16 A, 32 A after the upgrade | 40 A | 8 B&S twin |
| Each PV string | 10.7 A (Isc) | None, one string per controller | 6 mm² PV cable |

The DC side is two-wire, with no chassis return. Bond the MultiPlus case and the DC negative to the chassis at one point (design choice, to confirm with the electrician).

### 230 V circuits

AS/NZS 3001.2 requires the inverter's output to have RCD protection separate from the inlet's, labelled to say an inverter is installed, and the unit to be accessible with a visible status light ([BMPRO](https://teambmpro.com/12v-guru-as-nzs-3001-2-electrical-installations-what-does-it-all-mean/)). AS/NZS 4777.1 calls for RCDs on every final sub-circuit of an inverter's stand-alone output ([ERAC](https://www.erac.gov.au/wp-content/uploads/2021/11/Multiple_Mode_Inverters_Stand-alone_Operation_Oct-2021.pdf)). So every circuit gets a 30 mA RCBO, and a fault trips only its own circuit. The MultiPlus-II closes an internal relay that bonds neutral to earth when it inverts, so the RCDs work off-grid ([Victron community](https://community.victronenergy.com/t/multiplus-ii-5000va-grid-export-ac-coupled-inverter-ess-venusos-ac2-not-working/36111/5)). On shore power the relay opens and the site's earth applies. The chassis and every exposed metal part bond to the protective earth. A licensed electrician installs and certifies the 230 V work and the battery.

| Circuit | Load | Running current | RCBO | Control |
|---|---|---|---|---|
| C1 | Dometic CVI1525 hob | 10.0 A | 16 A | Current relay: above about 4.5 A it opens K4, any current opens S1 |
| C2 | Camec 053632 oven-microwave, its own circuit (report 21) | 6.3 A | 10 A | Contactor K2. Its current relay opens K4 and S1 |
| C3 | Kitchen bench outlets | User | 10 A | Node-RED total-power rule |
| C4 | DauerShower 2.0 heater, its own circuit (report 21) | 10.4 A | 16 A | Contactor K4. Its current relay opens K2 and S1 |
| C5 | Truma Combi D 6 E element | 3.9 A, or 7.8 A on high | 10 A | Contactor S1 |
| C6 | Camec washer | 1.2 A | 10 A | Contactor S1 |
| C7 | Haier heat-pump dryer | 4.3 A (est.) | 10 A | Contactor S1 |
| C8 | Mitsubishi split, outdoor unit feed | 7.1 A at most (report 19) | 10 A | Never shed |
| C9 | Desk and living outlets | User | 10 A | Node-RED total-power rule |
| C10 | Outdoor outlet, kerb side | User | 10 A | Node-RED total-power rule |

### Outlets and DC points by zone

| Zone | 230 V outlets | 24 V and USB points |
|---|---|---|
| Kitchen | 2 double outlets on the bench. Hob and oven on their own circuits | 1 USB-C PD 65 W |
| Desk under the bed | 2 double outlets (monitor and spare) | 2 USB-C PD 100 W for the laptops, 1 USB-A |
| Bed, night position | None | 2 USB-C PD 65 W, one each side. 2 reading lights |
| Living area | 1 double outlet | 2 USB-C PD 65 W |
| Wet room | None in the wet area | 24 V light. The RA 15-60 runs from the 12 V bus |
| Laundry | 2 single outlets, washer and dryer, on S1 | - |
| Electrical board | 1 single service outlet | Starlink Mini on a 24 V fused circuit (it takes 12 to 48 V DC, 60 W) |
| Outside, kerb side | 1 weatherproof double outlet, IP56 | 1 Anderson SB50 12 V outlet (10 A fuse), 1 USB-C |
| Totals | 6 double and 3 single 230 V outlets | 9 USB points, 1 external 12 V outlet |

Starlink's input rating is from [Starlink support](https://starlink.com/br/support/article/0b2d5227-1db6-0002-ecee-f49d3b516b49). The bank's 56.8 V charge voltage is above its 48 V limit, so it runs from the 24 V bus.

## 8. Mass and price

Every line is in `research/20-electrical.yaml`. Masses carry the repo's growth rule: maker figures at 0 %, estimates at 20 %.

| Line | Today (kg) | Report 20 (kg) | Basis | Price (AUD) |
|---|---|---|---|---|
| Batteries (UF-05) | 74.0 | 185.0 | Maker (Victron est.) | 14,555 |
| Battery box (UF-04) | 12.0 | 18.0 | Estimate, now inside | 1,200 |
| Battery fuses and busbars | in UF-04 | 1.5 | Estimate | 360 |
| Lynx Smart BMS NG | 1.9 | 1.9 | Maker | 994 |
| Lynx Distributor | 1.5 | 1.5 | Estimate | 293 |
| Inverter-charger | 30.0 | 29.0 | Maker | 1,333 |
| MPPTs | 2.5 | 2.5 | Maker | 510 |
| Charger from the ute | 1.8 in the trailer | 0, moved to the ute (TC01) | - | - |
| 24 V and 12 V converters, two pairs | 1.5 | 6.8 | Maker | 1,032 |
| Cerbo GX and display | 0.6 | 0.6 | Estimate | 616 |
| Main DC cables | in LA-04 wiring | 6.0 | Estimate | 450 |
| 230 V board: inlet, RCBOs, three contactors, three current relays, isolator, Anderson | not carried | 4.7 | Estimate | 1,480 |
| Board panel and wiring on it | 5.0 | 5.0 | Estimate | 150 |
| Fuses and holders on the board | 0.8 | in the lines above | - | - |
| Solar panels (RF-01) | 29.2 | 29.2 | Maker | 2,676 |
| Panel adhesive and cable (RF-02) | 2.0 | 2.0 | Estimate | 250 |
| Generators (GS-01) | 21.1 | 42.2 | Maker | 3,700 |
| Trailer total | 183.9 | 335.9 | 296.6 maker, 39.3 estimate | 29,599 |
| Growth allowance | 4.4 | 7.9 | 20 % of estimates | - |
| Ute side, TC01 and TW06 | - | 10.3 | 3.6 maker, 3.6 calculated, 3.1 estimate | 1,735 |

The trailer gains 152.0 kg, plus 3.5 kg of allowance. 111 kg of it is battery, 21.1 kg the second generator and 6 kg the larger box. The cabin's 230 V, 24 V and 12 V house wiring stays in BD-11 (60 kg, est.). Installation, testing and certification by a licensed electrician add about AUD 5,000 (est.). reports 19 and 21 carry their own appliances, fans and pumps.

Lighter variants that still meet H3:

| Variant | Saves | Cost of the saving |
|---|---|---|
| One Honda EU32i in place of two EU22i | 15.7 kg | A hot day takes 13.2 h to put back while living aboard, against 8.4 h, and AUD 99 more |
| One Honda EU22i only | 21.1 kg | 24.7 h while living aboard |

Four battery modules no longer meet H3, so there is no lighter battery.

## Open points

Each ends with the assumption the designer uses.

1. Cold day 07:00 to 17:00. Report 19 gives the cold night only. Assumption: the day rises to 13 °C at noon, and the heat pump's input (1.15 kWh) and the Combi's 12 V (0.10 kWh) over those hours are report 20's estimates from report 19's heat loss and COP. No H3 check uses them.
2. The DauerShower when its heater drops. The load management opens K4 when the hob passes 1 kW or the oven runs. Report 21 says that without 230 V the unit tops its loop up with 0.5 to 3 L/min of boiler water. Assumption: it does the same when its heater supply drops mid-shower, and the Combi's 10 L boiler carries the few minutes. If it stops instead, drop the hob rule and fit the MultiPlus-II 48/10000 (7.0 kW at 40 °C, +20 kg, AUD 1,194 more). It carries the shower and a full hob together, 6,015 W with the air-conditioner.
3. Battery box in the layout. Assumption: inside, at floor level, centred at X 4,200 mm plus or minus 300 mm, 900 mm (X) x 700 mm (Y) x 320 mm high outside (est.), out of the bed's footprint, lid on top, terminal side at least 300 mm from water and diesel lines. 204.5 kg with the fuses, its centre about 160 mm above the floor. Leave 175 mm along X beside it for a sixth module.
4. Battery box vents. BMPRO publishes vent areas per battery, which were not read. Assumption: two vents of at least 20 mm bore with insect mesh, one from the bottom of the box and one ducted from the top, both through the floor and away from the generator and the heater flue.
5. XT Air compressor current. Not published. Assumption: 25 A at 12 V for a few minutes when levelling. The 12 V pair carries it with everything else except the external outlet.
6. Combi D 6 E start current. Not published. Assumption: 8 A at 12 V for 2 min, from its 20 A burner fuse.
7. NG module mass. Victron marks 37 kg as an estimate. Assumption: 37 kg until weighed.
8. Spare alternator current. Assumption: 50 to 60 A at cruise, so two Orion-Tr 12/48-8 (62 A in) work with the 13.8 V start and 13.3 V stop thresholds. Log the voltage on the first hot night tow.
9. Jaylec BKS-240LC fitment. Marks 4WD lists it for the VDJ LandCruiser, without a model split. Assumption: it fits the 2017 VDJ79's 1VD-FTV. Confirm against the VIN before buying.
10. Generator stowage. Assumption: DX-01 grows to take two EU22i and the fuel, +21.1 kg and +14.5 kg on the ball. If it cannot, carry one EU32i (26.5 kg) and accept 13.2 h to put a hot day back while living aboard.
11. Generator 8 h target. The pair needs 8.4 h with the household running, 6.3 h with it off. Assumption: accept it, because a day with sun shortens the run to about 4.7 h.
12. Hot water mode. Assumption: H3 is checked all electric, with the Combi's element on 900 W. Diesel hot water saves 0.7 kWh a day and is the low-battery mode.
13. Inverter idle. Assumption: the full 28 W for 24 h in the electric cases. AES mode (18 W) would save 0.24 kWh a day, but it holds only at light load.
14. Fire protection. The quoted clauses of AS/NZS 3001.2 set no fire rating for the box. Assumption: 3 mm ceramic-fibre lining (in the 1.5 kg of E-10) and a heat detector on a Cerbo digital input.
15. 10 A outlets. Assumption: a compliant 10 A to 15 A adaptor with its own RCD and 10 A breaker, with the input limit set to 10 A.
16. Roof. Report 25 studies a raising roof. Assumption: the fixed roof's full array. If the roof changes, use the 85 % or 70 % row of section 5.
17. Battery isolator, chassis bonding, the TSC supply and the RCD layout. These are design choices here. Assumption: as section 7, confirmed by the licensed electrician against AS/NZS 3001.1, 3001.2 and 3000 before CT-601 is issued.

## Could not verify

- The Quattro-II 48/5000's continuous ratings and mass.
- The Enerdrive B-TEC 24 V 150 Ah's size (its 38.2 kg may be a shipping mass).
- An IEC 62619 certificate for Revolution Power's 48 V 100 Ah, and the CAN protocol it uses.
- The DIY JK BMS's heater output and its CAN link to a GX.
- The Cerbo GX's own consumption. Victron does not publish it.
- The price of the SBC 250 A alternator and of M2K's hybrid kits.
- The Bosch TSC's own supply. The specification found is a generic TSC sheet.
- The DauerShower's behaviour when its heater supply drops mid-shower.
- The full text of AS/NZS 3001.1 and 3001.2. The clauses here are quoted from BMPRO, Invicta and ERAC.
