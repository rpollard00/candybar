# Switching the shell from PETG to ABS: a research spike

Research date: 2026-11-11. All dimensions in millimetres unless a unit is given. All prices in USD,
without tax and without shipping.

This note explores one question from the owner: what would change if the printed cabinet shell
used ABS (or ASA) on a new enclosed printer instead of PETG on the Bambu A1. It is an exploration,
not a decision. The PETG plan stays the plan until the owner decides. The note follows
`docs/research/petg-finishing.md` (the "PETG note") and does not repeat it. Read sections 1.3, 2.0, 3
and 4 of the PETG note first.

The shell: about 495 to 535 wide x 580 deep x 575 high, many printed pieces, a 4 mm skin, bonded for
good on inside flanges with screws, then filled, sanded, primed and painted so that no seam shows.

Every product name is an example of a class. No product was bought or tested for this note.

## Terms

| Term | Meaning in this note |
| --- | --- |
| Bond, seam, groove, filler, ghost line, coupon | As in the PETG note. |
| Weld | A solvent joint: acetone (or a cement) softens both faces and they become one material. |
| Slurry | ABS dissolved in acetone to a paste. It fills gaps and dries to ABS. |
| Warp | The part curls up from the bed or bends after it is free, from uneven shrink. |
| Active chamber | The printer has a heater for the chamber air. A passive chamber gets heat from the bed only. |
| Stress cracking | Cracks that start where a solvent touches plastic that is under stress (press fits, inserts, screws, print stress). |

## Evidence grades

The same grades as the PETG note.

| Grade | Meaning |
| --- | --- |
| [a] | A maker's data sheet, guide, FAQ or product page (printer, filament, paint, adhesive maker), or a health body. |
| [b] | A published test with a stated method (a paper, or a maker's test with its method). |
| [c] | Reports from users: forums, blogs, reviews, videos. The count of independent reports is given. |
| [d] | Our reasoning or calculation, not from a source. The method is given. |

Source numbers in square brackets, for example [S3], point to the list in section 11. "Search
summary" means that only the search-engine summary of the page was read, not the full page.

---

## 1. Summary (one page)

**What ABS would gain.**

- **One material in the seam.** ABS welds to itself with acetone or ABS slurry. Two studies on printed
  ABS found acetone joints near the strength of a one-piece part, and the test pieces often broke
  beside the joint, not in it [b, S20, S21]. The PETG plan needs a different adhesive (MMA) and a
  filler of a different material in the groove.
- **Better-documented finishing products.** Polyester plastic putties and 1K plastic primers name ABS
  on their data sheets [a, S26, S27, S29, S30]. For PETG, almost no data sheet names the substrate
  (PETG note, 1.3).
- **Easier sanding.** Prusa says ABS sands "wet or dry" [a, S8]. PETG gums when dry-sanded (PETG note).
- **More heat margin.** HDT at 1.8 MPa: ABS 84 C, PETG HF 62 C (Bambu data sheets) [a, S4, S5]. The
  shell near the exhaust reaches 40 to 50 C.
- **The owner's styrene-model skills transfer in part.** Hobby lacquers grip by slightly dissolving
  the plastic [a, S31]. They do this on ABS. They do not do it on PETG.

**What ABS would cost.**

- **A new enclosed printer and venting.** Bambu says ABS and ASA need an enclosed printer and are
  "not compatible" with A-series printers; Bambu does not recommend enclosing the A1 [a, S1, S2].
- **Warp on large flat parts.** Even with a 65 C heated chamber, one user could not stop a full-plate
  flat ABS part from warping on an H2S [c, 1 report, S40]. Warp, not the bed, is likely to limit the
  size of flat pieces such as floor tiles [d].
- **Emissions.** ABS printing emits about 100 times more ultrafine particles than PETG (median about
  10^11 against 10^9 per hour, 447 runs) [b, S11] and more than ten times the VOCs, mostly styrene
  [b, S12]. IARC classes styrene as "probably carcinogenic to humans" (Group 2A) [a, S14]. The cabinet
  needs about 200 to 400 h of printing [d, section 8.1]. The printer must not stand in a living area
  [a, S1] and should vent outdoors [a, S15, S16].
- **New risk in finishing.** ABS is a "solvent sensitive" plastic [a, S29]. Lacquer thinners and
  enamel washes crack stressed ABS [a, S31; c, many reports, S33]. The PETG plan has no such risk.
- **Time and set-up.** A new machine, calibration, a vent, a hotter dryer, and new test coupons.

**Three set-up budgets** (section 8; prices read 2026-11-11, many are Black Friday prices):

| Budget | Printer | Total, priced items only |
| --- | --- | --- |
| Low | Qidi Q2 (270 x 270 x 256, active chamber 65 C) | about $974 |
| Middle | Bambu Lab H2S (340 x 320 x 340, active chamber 65 C) | about $1,591 |
| High | Prusa CORE One L+ with Advanced Filtration (300 x 300 x 330, chamber 60 C) | about $2,838 |

For comparison, the PETG plan needs only filament (about $200 for 20 kg) because the A1 exists.

**What would decide it.**

1. The PETG coupon test (PETG note, section 4). If the PETG seam shows no ghost line after the warm
   soak and two weeks, the main reason to switch goes away.
2. An ABS coupon printed on the A1 in a ventilated place. Bambu allows ABS on the A1 for "small-sized
   models with low infill densities" [a, S2]. A 120 mm coupon is small. This tests the ABS finishing
   system (weld, slurry, primer, hobby lacquer, stress cracking) before any printer is bought.
3. Where the printer can stand, with a vent to outdoors. If there is no such place, ABS is not a
   good fit for a home.
4. A warp test of the worst part (a floor tile) on the candidate printer, or published results of
   such a part. No published test with a size limit was found.

---

## 2. What ABS gains for this project (question 1)

### 2.1 Step-by-step comparison with the PETG system

| Step | PETG system (PETG note) | ABS system | Change |
| --- | --- | --- | --- |
| Structural bond | Plexus MA310 (MMA), slow; or a solvent cement that lists PETG | Acetone weld or ABS slurry on the flange, screws as clamps. Plexus also lists ABS (ITW list in the PETG note, S40 there) [a]. | Easier. Same material, no special adhesive. |
| Groove | V-groove, friction weld with PETG or polyester glazing putty | V-groove filled with ABS slurry in thin layers, or friction weld with ABS | Easier, but slurry shrinks as acetone leaves (2.2). Wait longer. |
| Level | Wet sanding; PETG gums when dry | ABS sands "wet or dry" [a, S8] | Easier. |
| Fill | Evercoat Metal Glaze (lists "rigid to semi-rigid plastics") | Polyester plastic putties that list ABS by name [a, S26, S27]; XTC-3D lists ABS [a, PETG note S23] | Easier. Better data. |
| Prime | 2K epoxy primer or 1K filler primer; PETG not named on any sheet | 1K plastic primers that list ABS [a, S28, S30]. A 1K promoter "for solvent sensitive plastics, such as PC, ABS" [a, S29]. | Easier for grip. New risk: solvent attack. |
| Colour | Hobby lacquer over primer only | Hobby lacquer grips ABS, but stressed ABS can crack (2.4) | Same rule: prime first. Reason changes. |
| Heat near exhaust | HDT 62 C (1.8 MPa) | HDT 84 C (1.8 MPa) | Better. |
| Smoothing | Not possible with acetone | Acetone vapour smoothing is possible [a, S8] | Not useful here (2.5). |

### 2.2 Bonding

**Strength [b].**

- Saraf et al. (2020) joined printed ABS with acetone over several overlaps and raster angles.
  "Acetone-bonded joints performed comparably to single-piece specimens" (as summarised in S21).
  Acetone vapour pre-treatment of the faces reduced strength [b, S20, abstract only].
- A 2025 paper tested ABS lap joints (ASTM D3163) bonded with acetone, ABS/acetone mixes (5, 10 and 20 g
  per 50 ml), CA and epoxy, with 4.6 mm adherends. "Stock break" (failure beside the joint) was
  "prominently observed" [b, S21, introduction and method only]. A citing page gives the ABS/acetone
  result as a "75 % improvement over the 8.4 MPa achieved by cyanoacrylate" [b, search summary]. The
  full results were not read.
- A related study used ABS slurry on printed PLA. Fresh slurry reached 8.69 MPa lap shear, "outperforming
  commercial cyanoacrylates". Slurry aged three years kept about 86 % of its strength [b, S22, abstract].

**Gap filling and working time.**

- Pure acetone evaporates fast. Users say it is hard to get a good bond with acetone alone, and that a
  slurry "sticks around longer" and fills gaps [c, 3 reports, S23].
- MatterHackers gives three mixes, each with 50 ml acetone: "juice" (4 g ABS, bed adhesion), "glue" (8 g,
  welding) and "slurry" (about 20 g, filler) [a, S24].
- The PETG plan's MMA fills gaps of 0.25 to 3.2 and has 15 to 18 min work time (PETG note). Slurry has
  no data sheet. Its gap limit and work time are not known. The coupon must find them [d].

**Does a welded seam still show later?**

- Slurry "shrinks and cracks" if it goes on thick; build it up in thin layers [c, S25]. An early
  report says the glue "shrinks a lot as it dries" and dries at the edges first [c, S25b].
- Model builders report that solvent trapped in a seam leaves over days and the seam then sinks
  and shows; they wait at least 24 h [c, S25c].
- No test of a welded ABS seam under paint over weeks was found. The risk is the same kind as in the
  PETG note (shrink after sanding), from a different cause [d]. Put a wait of at least one week between
  the last slurry and the final block sanding into the coupon test, and look again at 1 and 2 weeks [d].

### 2.3 Fillers, putties and sanding

- Two-part polyester putties for plastic car parts list ABS by name: C.A.R.FIT Plastic Putty (ABS, PA,
  PC, PP and others) and Mobihel Plastic Putty (PP, ABS, PC, PA, PUR, PPO) [a, S26, S27]. A spray
  plastic filler "adheres to all customary hard plastics in the car, such as PP, PUR, ABS" [a, S27b].
- The Bondo body filler data sheet still lists metals, SMC and FRP only (PETG note). It is not made for
  thermoplastics, ABS included.
- Hobby lacquer putty (Tamiya Putty Basic) is polystyrene in solvent and "reacts chemically" with
  polystyrene (PETG note, S39 there). On ABS it softens the face a little. The owner knows this
  behaviour from styrene kits. No maker data for ABS was found [d].
- Sanding: Prusa says ABS sands wet or dry [a, S8]. ABS dust is still a dust: wear a P2/P3 filter
  for dry sanding (PETG note, section 6).

### 2.4 Primer, paint and hobby lacquers on ABS

- **Grip.** Mr. Hobby says its solvent paints grip by slightly dissolving the plastic [a, S31]. ABS is
  soluble in ketones, so lacquers bite it [d from S24]. Car-paint makers list ABS for 1K primers and
  promoters [a, S28, S30].
- **Risk.** Mr. Hobby says thin ABS parts are "easily damaged by solvent" and offers a low-solvent
  water-based line for them [a, S31]. Its catalogue marks some lacquer lines with an ABS crack warning
  [a, S31b, search summary]. PPG calls ABS a "solvent sensitive" plastic [a, S29]. Gunpla builders
  report many cracked ABS parts from enamel washes and lacquer, mostly at press fits and pegs; one
  test video says "solvent plus stress" is the cause and that unstressed parts survived soaking
  [c, more than 5 reports, S33].
- **What this means for the shell [d].** A printed ABS shell has stress: print stress, screws, heat-set
  inserts, and stress near welded flanges. Strong solvents (lacquer thinner, enamel wash, acetone wipe)
  on bare ABS near these places can start cracks. Seal the shell with a primer in light coats with
  flash time, then use hobby lacquers over the primer. Keep acetone and thinners away from bosses with
  inserts. This is the same rule as the PETG note ("prime every face") for a different reason.
- One user reports cracks across an ABS part the day after acetone vapour smoothing [c, 1 report, S34].

### 2.5 Acetone smoothing

ABS can be vapour-smoothed with acetone [a, S8]. On this shell it has little value [d]: the whole shell
gets filler primer anyway; smoothing rounds edges and detail [a, S9]; it puts solvent into a stressed
4 mm skin (2.4). Do not use it on the shell.

### 2.6 Heat, stiffness and creep against PETG

| Property (Bambu data sheets, ISO methods) | Bambu ABS | Bambu PETG HF | Bambu ASA | Grade |
| --- | --- | --- | --- | --- |
| HDT 1.8 MPa | 84 C | 62 C | not read | [a] S4, S5 |
| HDT 0.45 MPa | 87 C | 69 C | 100 C | [a] S1, S5 |
| Young's modulus XY | 2200 MPa | 1810 MPa | not read | [a] S4, S5 |
| Bending modulus XY | 1880 MPa | 2050 MPa | not read | [a] S4, S5 |
| Impact strength Z (layer bond) | 7.4 kJ/m2 | 10.6 kJ/m2 | 4.9 kJ/m2 | [a] S1, S5 |
| Density | 1.05 g/cm3 | 1.28 g/cm3 | not read | [a] S4, S5 |
| Water absorption (25 C, 55 % RH) | 0.65 % | 0.40 % | not read | [a] S4, S5 |

- Stiffness: about equal. ABS is stiffer in tension, PETG HF in bending. A 4 mm ABS skin is not
  stiffer than a 4 mm PETG skin [d].
- Layer bond: lower in ABS and much lower in ASA (Z impact). Flanges that are loaded across layers
  are weaker [d].
- Creep: no creep data for printed ABS or PETG was found in this spike.
- Heat: ABS gives more margin at 40 to 50 C. The PETG note found no softening problem in the
  owner's earlier PETG case, so this gain is a margin, not a fix [d].
- Mass: for the same volume, ABS weighs about 18 % less than PETG HF (1.05 against 1.28) [d from S4, S5].

---

## 3. What ABS costs in printing (question 2)

### 3.1 Warp and cracks

- **Cause.** Bambu gives two causes: shrink on cooling, and internal stress because ABS has a high
  Tg relative to the room [a, S1]. Interlayer cracks come when cooling stress is greater than the
  layer bond; Bambu lists low chamber temperature and too much fan [a, S1].
- **Bambu's rules.** Glue on the plate; brim; raise the chamber temperature; avoid infill above 50 %
  and more than 6 walls, because both raise shrink stress [a, S1]. For "larger sizes and/or higher
  infill density" on ABS and ASA, Bambu suggests a 60 C chamber [a, S3].
- **The conflict with the shell [d].** The PETG note asks for enough walls that sanding cannot reach
  infill. A dense 4 mm skin is the kind of part Bambu says warps more. The design must solve this
  (section 8).
- **Users.**
  - Full-plate, flat-topped ABS part on an H2S, 65 C chamber, 110 C bed: still warped. Replies: a
    full-plate flat part is close to a "guarantee for warping"; try ABS-GF or CF; cut small grooves
    to break long flat faces [c, 1 report with 6 repliers, S40].
  - "Large flat parts with thick walls will warp in ABS" unless the chamber is very hot [c, 1 report,
    S41, search summary].
  - On a passive P1S: no warp "unless it is a large flat surface with very sharp corners"; brim or mouse
    ears fix that [c, S42, 1 report]. Preheat with the bed at 100 C until the chamber reaches about
    45 C is "very important" [c, 1 report, S42b].
  - A 60 C chamber printed an ABS helmet in one piece over two days on a Qidi X-Max 3 [c, 1 report, S43].
  - "The H2D has made ABS prints feasible for me" [c, 1 report, S44].
- **Summary [d].** An active chamber helps a lot, but large flat dense parts still warp. Curved,
  ribbed panels are less at risk than flat tiles.

### 3.2 Chamber temperature, passive against active

| Source | Statement | Grade |
| --- | --- | --- |
| Bambu (Studio guide) | ABS/ASA: chamber heating off by default; turn it on at 60 C for large or dense parts. Chamber heating makes "air filtration ... worse". | [a] S3 |
| Bambu (filament guide) | Without a heater: preheat the bed to the maximum for 15 min (X1C, P1S). | [a] S1 |
| Creality | K2 Plus chamber may not reach its target on 110 V when the room is below 15 C. | [a, via S48] |
| Users, P1S | Bed at 100 C moved to the top: "almost 60c" chamber; more with insulation. | [c, 1 report, S42c] |
| Users, A1 in a tent | With a PTC heater: 60 C in 15 min. Without: 40 C after 30 min, bed at 100 C. | [c, 1 report, S45] |
| Snapmaker | U1 top cover: "50 °C passive heating". | [a] S56 |

### 3.3 Shrink and tolerance

- A Binghamton study (Weiser et al. 2021) printed PLA, PETG and ABS on one printer and measured them.
  ABS shrank 0.59 % in X and 0.69 % in Y and grew 0.92 % in Z; PETG shrank 0.76 % and 0.54 % [b, via S10].
  So printed XY shrink of ABS and PETG was about the same in that study.
- Other figures: Prusa gives 1 to 2 % for ABS [a, S8]; molded ABS and ASA resins 0.4 to 0.7 %
  [a, via S10]. No published study gives printed ASA shrink by axis [S10].
- The difference that matters is warp (curl and bow), not the mean shrink [d].

### 3.4 Bed adhesion

- Bambu: glue is "required" for ABS and ASA; not compatible with the Low-Temp Engineering Plate
  [a, S1]. The Textured PEI plate needs no glue for ABS at 90 to 100 C [a, S52].
- Do not use acetone "ABS juice" on PEI. A Bambu forum user warns acetone attacks PEI [c, 1 report, S24b].

### 3.5 Design rules for ABS (from makers and users)

| Rule | Source | Grade |
| --- | --- | --- |
| Glue plus brim; "mouse ears" on corners | Bambu, users | [a] S1; [c] S40, S42 |
| Infill 50 % or less; 6 walls or fewer | Bambu | [a] S1 |
| Inner fillets at base-to-wall steps | Bambu (for ring artefacts) | [a] S1 |
| Break long flat faces with shallow grooves | User | [c] S40 |
| Use GF or CF filled grades for large flat parts | Bambu (ABS-GF reduces warp), users | [a] S47; [c] S40 |
| Draft shield if there is no enclosure | Prusa | [a] S8, S9 |
| Lower fan for large parts | Bambu, users | [a] S1; [c] S40 |
| Print few parts per plate, "by object" | Bambu (layer time vs layer bond) | [a] S1 |

No source gave a numeric maximum part size for ABS.

### 3.6 Emissions, filtration and where the printer can stand

**Published studies.**

- Azimi et al. 2016 (5 printers, up to 9 filaments, chamber tests): highest UFP rates with ABS,
  median 2 x 10^10 to 9 x 10^10 per minute; PLA about 10^8 per minute. Styrene from ABS and HIPS:
  about 12 to 113 µg/min. Enclosed printers did not reliably lower styrene [b, S12a].
- Zhang et al. 2023 (447 particle and 58 VOC runs, one standard method): ABS, nylon and HIPS had the
  highest particle medians (order 10^11 per hour); PLA, PETG and PVA 10^9 per hour. ASA particles were
  "comparable to the medians of PETG". "High emitting materials include ... ASA (VOC), ABS and HIPS
  (both)" [b, S11].
- A 2022 study (PTR-ToF-MS, Prusa MK2S in a sealed box): ABS gave by far the highest VOCs, mostly
  styrene; PETG and nylon were "more than an order of magnitude lower" [b, S12].

**Health bodies.**

- IARC: styrene is "probably carcinogenic to humans (Group 2A)" [a, S14].
- NIOSH: control at the source; ventilated enclosure or local exhaust to outdoors; HEPA for particles,
  and gas filters for VOCs. A filtered hood over a printer cut particle emissions by 97 to 99 %. Three air
  changes per hour was "not a sufficient control" for regular use [a, S15, S16].
- Bambu: print ABS and ASA in an enclosed printer, "avoid operating in living areas" and bedrooms;
  replace the carbon filter about every 1,440 h; wear a vapour mask for long jobs; increase ventilation
  or stop if people with asthma, pregnant women or children are present [a, S1].

**What this means [d].** About 200 to 400 h of ABS printing (section 8.1) is a long exposure. A printer
with H12 HEPA and carbon is good but not enough by itself: Bambu says chamber heating makes filtration
worse [a, S3]. Put the printer in a garage, workshop or other non-living room, with a duct to a window
and a fan that keeps the enclosure under slight suction. Keep the room above 15 C in winter
(Creality caveat, S48; Bambu working range 10 to 30 C [a, S6]).

---

## 4. ASA, and other materials in short (question 3)

### 4.1 ASA against ABS for this cabinet

| Point | ASA | ABS | Grade |
| --- | --- | --- | --- |
| Warp | "Warps less" than ABS (Prusa) | More | [a] S9 |
| Layer bond (Z impact, Bambu) | 4.9 kJ/m2 | 7.4 kJ/m2 | [a] S1 |
| HDT 0.45 MPa (Bambu) | 100 C | 87 C | [a] S1 |
| Particles | Comparable to PETG | About 100 x PETG | [b] S11 |
| VOC | Listed as a high VOC emitter | High | [b] S11 |
| Smell | "Doesn't smell as much" (Prusa) | More | [a] S9 |
| Solvent weld with acetone | Prusa: "glue/weld it with acetone". One reference site: acetone bond "does not work", use MEK. Users: acetone works but evaporates fast. | Works | [a] S9; [c] S35, S23 |
| UV resistance | Yes. Not needed: the cabinet is painted and indoors. | No | [a] S1 |
| Price per kg (Nov 2026) | Elegoo $16.99; Bambu $17.99 sale; Polymaker from $24.99 | Elegoo $18.99; Bambu $15.99 MSRP; PolyLite from $18.99 | [a] S60-S62 |

ASA trades a little less warp and fewer particles for weaker layers. The sources disagree on acetone
welding of ASA. If the owner chooses the styrene family, the ABS-or-ASA question should go to the
coupon: weld one ABS pair and one ASA pair with acetone and slurry [d].

### 4.2 Glass- or carbon-filled ABS or ASA

Bambu says ABS-GF reduces warp and gives a matte face that hides layer lines [a, S47]. The cost:
XY impact falls from 39.3 to 14.5 kJ/m2 and Z impact from 7.4 to 5.3 [a, S47]; a hardened nozzle is
needed [a, S53]. ASA-CF has a higher Z impact than ASA (9.4 against 4.9) [a, S47b]. Users suggest GF or CF
for full-plate parts [c, S40]. Use [d]: a candidate for the floor tiles and hidden flat parts, where warp
is worst and the face is not a show face. Solvent welding of filled grades was not checked.

### 4.3 Polycarbonate blends (PC/ABS)

Higher heat, but Mr. Hobby says it has no paints or primers for polycarbonate; peeling or cracking
of the film is "likely" [a, S31]. Bambu says PC is highly hygroscopic [a, S1]. Not a fit for a painted
show shell [d].

### 4.4 HIPS

HIPS is polystyrene, the plastic of styrene model kits. Polystyrene cements and putties are made for it
[a, S32; c, S32b]. But HIPS is among the highest emitters of both particles and VOCs [b, S11], and the
styrene rate is like ABS [b, S12a]. No large-part print or finishing data was found. Not recommended
for the shell [d].

---

## 5. Printers (question 4)

Prices are US store or large-retailer prices read on 2026-11-11 from the page or its search summary.
Many are Black Friday prices (Bambu: sale from 2026-10-27 to 2026-12-01 [a, S59]). "Typical" or "list"
is the regular price. User reports are counted; most are single reports.

### 5.1 Tier 1: lowest cost that does the job

| Model | Build volume | Chamber | Nozzle / bed max | Filtration | Price | Users, large ABS/ASA | Known faults | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qidi Q2 | 270 x 270 x 256 | Active, 65 C | 370 / 120 C | G3 + H12 HEPA + carbon | $499 (page also shows $449) | Not checked | Qidi early batches had faults fixed later by free parts (Plus4, below) [c] | [a] S63 |
| Qidi Q2C | 270 x 270 x 256 | Enclosed, no heater | 370 / 120 C | Optional | $349 | Not checked | Not checked | [a] S63 |
| Bambu Lab P2S | 256 x 256 x 256 | Passive only (no heater) | 300 / 110 C | Activated carbon | $449 sale ($549 typical) | Full-width parts warp at the edge [c, 1 report, S46] | Not checked | [a] S7, S59 |
| Bambu Lab P1S | 256 x 256 x 256 | Passive | Not read | Carbon | $349 sale | Fine unless large flat sharp corners [c, S42]; preheat needed [c, S42b] | Bed limited to 100 C [c] | [a] S59; [c] S42 |
| Elegoo Centauri Carbon 2 | 256 x 256 x 256 | Enclosed, passive | 350 / 110 C | Not checked | Combo $369 sale ($449 list) | Not checked | Not checked | [a] S64, search summary |
| Snapmaker U1 + top cover | 270 x 270 x 270 | Top cover: "50 °C passive heating" | 300 / 100 C | 3-stage in cover | $699 sale + cover $149 | ASA printed without the lid [c, 1 review, S56b] | Not fully enclosed without the cover [a] | [a] S56 |

The lowest-cost machine with an active chamber is the Qidi Q2. Its bed is only 14 mm larger than
the A1's. It removes the material limit, not the piece count.

### 5.2 Tier 2: active chamber, middle price

| Model | Build volume | Chamber | Nozzle / bed max | Filtration | Price | Users, large ABS/ASA | Known faults | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Bambu Lab X2D | 256 x 256 x 260 (main nozzle) | Active, 65 C | 300 / 120 C | G3 + H12 + carbon (secondary, S6c) | $589 sale ($649 typical); Combo $789 | Prints that curl on the P2S "can come out properly" [c, 1 review, S49] | Right nozzle loses part of the plate (235.5 wide) [c, S49] | [a] S7b, S59 |
| Creality K2 Pro Combo | 300 x 300 x 300 | Active, 60 C | 300 / 110 C | 1 filter | $749 (sale) | Not checked | Not checked | [a] S50, S51 |
| Flashforge Creator 5 Pro | 256 x 256 x 256 | Active, 65 C | 320 / 120 C | Yes, type not stated by Flashforge | $849 sale ($949) | Not checked | Not checked | [a] S54 |
| Qidi Plus 5 | 320 x 320 x 300 | Active, 65 C | 370 / 120 C | G3 + H12 + carbon | $749 | Not checked | Not checked | [a] S63 |

### 5.3 Tier 3: large format (300 to 350 and above)

| Model | Build volume | Chamber | Nozzle / bed max | Filtration | Price | Users, large ABS/ASA | Known faults | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Bambu Lab H2S | 340 x 320 x 340 | Active, 65 C | 350 / 120 C | G3 + H12 HEPA + carbon | $1,049 sale ($1,199 typical) | Full-plate flat ABS part warped at 65 C [c, 1 report, S40] | Not checked | [a] S6b, S59 |
| Bambu Lab H2D | 325 x 320 x 325 (one nozzle) | Active (max not read) | 350 / 120 C (H2D Pro page) | Not read | $1,399 sale ($1,549) | "Made ABS prints feasible" [c, 1, S44] | Not checked | [a] S6, S59 |
| Anycubic Kobra S1 Max | 350 x 350 x 350 | Active, 65 C | 350 / 120 C | Carbon filter | $699 ($899 list); Combo $899 | Not checked | Not checked | [a] S55 |
| Creality K2 Plus Combo | 350 x 350 x 350 | Active, 60 C | 350 / 120 C | 2 filters | $1,099 ($1,499 list) | Not checked | Chamber may not reach target on 110 V below 15 C room [a, via S48] | [a] S50, S51 |
| Qidi Max4 | 390 x 390 x 340 | Active, 65 C | 370 / 120 C | G3 + H12 + carbon | $1,049 | Not checked | Not checked | [a] S63 |
| Prusa CORE One L+ | 300 x 300 x 330 | 60 C, heated by convection from the bed | 290 / 120 C | ABS/ASA listed only with the Advanced Filtration System (HEPA + carbon) | $1,906.48; with filtration $1,980.56 | Not checked | Not checked | [a] S57 |
| Bambu Lab H2C / H3C | 330 x 320 x 325 class | Active, 65 C | 350 / 120 C | H3C: H11 HEPA + carbon; H2C not read | H2C Combo $1,899; H3C $2,499 | Not checked | Multi-material machines; no benefit for one-material shells [d] | [a] S6, S59 |
| Sovol M1D Advanced | 300 x 300 x 350 | Active, 60 C | Not read | Not read | From $1,499 (pre-order) | Not checked | Pre-order only | [a] S58 |
| Flashforge Guider 4 | 300 x 300 x 300 | Enclosed, no heater (secondary) | 320 / 110 C | HEPA 13 | $1,299 (secondary) | Not checked | Not checked | [c] S54b |

Historical fault, to show the risk of new designs: the first Qidi Plus4 shut down when the bed
passed about 250 of Z with the chamber heater on, because the bed blocked the heater outlet. Users
fixed it with a macro that turns the heater off above 260 [c, 1 report with replies, S43]. The Plus4
is now discontinued [a, S63].

### 5.4 Kit machines (short)

- **Voron 2.4** (300 or 350): kits from about $702 (Formbot, sale) to $939 to $1,434 (Siboor); LDO kit
  $1,299.99 (via a secondary source) [a, S65; c, S65b]. About 30 h to build [c, S65b]. Enclosure panels
  are part of the design; chamber heat comes from the bed unless a heater is added [d]. Kit quality
  varies by vendor [c, 2 reports, S65c].
- **Rat Rig V-Core 4.1** (300, 400, 500): open frame, "Enclosing panels are not included", from
  €908.10 sale (EU); US page $1,165.19 [a, S66]. Even the 500 size does not give one-piece
  full-width parts at 515 or 535 (section 6).

Kits suit an owner who wants to build a printer. This project wants a cabinet [d].

### 5.5 Machines left out

- Smaller than the A1 in at least one axis: Bambu A1 mini (180 cube); Prusa CORE One / One+
  (250 x 220 x 270); Anycubic Kobra S1 (250 x 250 x 250); Qidi Q1 Pro (245 x 245 x 240); Flashforge
  AD5X and Adventurer 5M Pro (220 cube); Sovol Zero (small, not measured here). Creality K1C was not checked.
- Open frame (no enclosure as sold): Bambu A2L (330 x 320 x 325; ABS not listed), Flashforge Creator 5,
  Sovol SV08 and SV08 Max (enclosure kit sold separately), Rat Rig V-Core 4.1.
- Not on Bambu's current buying-guide list: X1C, X1E [a, S6].

---

## 6. What a larger bed changes (question 5)

Method [d]: a piece must fit the bed with a brim of about 5 on each side. Usable length = bed - 10.
Pieces = the smallest whole number n with W / n <= usable. A 350 square bed fits at most a 495 diagonal,
so diagonal placement does not make a full-width part fit in one piece.

| Bed | Usable | Floor 495 x 580 | Full-width part at 495 | at 515 | at 535 |
| --- | --- | --- | --- | --- | --- |
| A1, 256 x 256 | 246 | 3 x 3 = 9 by this rule; 2 x 3 = 6 with a smaller brim (247.5 per piece) | 3 (2 only with no brim) | 3 | 3 |
| 270 x 270 (Q2) | 260 | 2 x 3 = 6 | 2 | 2 | 3 |
| 300 x 300 | 290 | 2 x 2 = 4 (290 deep exactly; tight) | 2 | 2 | 2 |
| 340 x 320 (H2S) | 330 / 310 | 2 x 2 = 4 (580 / 2 = 290 along 310) | 2 | 2 | 2 |
| 350 x 350 | 340 | 2 x 2 = 4 | 2 | 2 | 2 |
| 390 x 390 (Max4) | 380 | 2 x 2 = 4 | 2 | 2 | 2 |
| 500 x 500 (open kits) | 490 | 2 x 2 = 4 | 2 (1 only with a brim under 2.5) | 2 | 2 |

What changes [d]:

- 256 to 300: the floor goes from 6 tiles to 4. Every full-width part becomes 2 pieces at any width
  from 495 to 535. This removes the 3-piece case and one seam per full-width part.
- 300 to 350: no change in piece count for this cabinet. It gives margin for brims and for keys.
- One-piece full-width parts need a bed of about 545 or more (535 plus a brim). Even a 500 bed gives
  one piece only at 495 with almost no brim. No enclosed machine in this list comes close.

Does warp, not the bed, then limit piece size in ABS? The evidence says probably yes for flat parts:
a full-plate flat ABS part warped on an H2S at 65 C [c, S40], and makers and users treat large flat
dense parts as the worst case [a, S1; c, S41]. A 290 x 268 floor tile is such a part. Curved shell
panels with flanges and ribs are less at risk [d]. No published test with a size limit was found.
Until a test on the chosen printer proves otherwise, plan flat ABS pieces no larger than about 250
in any direction, and let the larger bed buy margin, not bigger tiles [d].

---

## 7. The lowest-cost route: a tent for the existing A1 (question 6)

**What Bambu says.**

- A1 FAQ: the open frame and lower chamber temperature give "reduced interlayer strength", more warp
  and "larger warping amplitudes for large-sized models". ABS and ASA are not recommended "for printing
  models that require high interlayer strength with large sizes", but "can be used ... for printing
  small-sized models with low infill densities" [a, S2].
- "We don't recommend enclosing the A1" [a, S2]. ABS and ASA are "not compatible with ... A models"
  and not compatible with the AMS lite [a, S1].
- A Bambu forum moderator: an A1 in a heated enclosure risks heat creep, and the mainboard and power
  supply in the base "can overheat" [a/c, S45b].

**What users report.**

- Small ABS parts on an open A1 printed well [c, 2 reports, S45c].
- An A1 in a tent with a PTC heater reached 60 C [c, 1 report, S45].
- Heat creep and extrusion faults after heating an enclosure to 35 to 40 C [c, 1 report, S45b].
- No report of a large ABS shell part (200 or more) on an A1 was found.

**Risks [d].** Mainboard heat; heat creep with the A1 hotend; a moving bed with tall parts in a hot
tent; no filtration; Bambu does not support it; the brief already says "Do not enclose the A1 just to
force an ABS/ASA route".

**Cost.** Creality tent $79.99 [a, S67] plus a duct fan $89.99 [a, S68], plus a heater (not priced):
about $170.

**Use [d].** Not for the shell. Good for one thing: printing the small ABS and ASA coupons (section 10)
in a ventilated place, with no tent, to test the finishing system before a printer is bought.

---

## 8. Budget (question 7)

### 8.1 Filament mass estimate [d]

Method: volume x fill fraction x density, then an allowance for failures and tests.

| Item | Basis | ABS mass |
| --- | --- | --- |
| Skin | 1.5 to 1.8 m2 x 4 mm = 6.0 to 7.2 L; 70 to 100 % solid; 1.05 g/cm3 | 4.4 to 7.6 kg |
| Flanges, ribs, bosses, keys | Assumed 1.0 to 2.0 kg | 1.0 to 2.0 kg |
| Thick floor | 0.29 m2 x 6 to 10 mm, 50 to 70 % solid | 0.9 to 2.1 kg |
| Supports, brims, draft shields | Assumed | 0.5 to 1.0 kg |
| Subtotal | | 6.8 to 12.7 kg |
| Coupons, tests, failed prints | +25 to 40 % for ABS | **about 9 to 18 kg; plan 15 kg** |

For PETG the same volume weighs 1.28 / 1.05 = 1.22 times more: about 8.3 to 15.5 kg before failures,
and about 10 to 19 kg with a +15 to 25 % allowance [d]. ASA density was not read; take it as ABS.

**Print time [d].** 12 kg of ABS = about 11,400 cm3. At an average of 8 to 15 mm3/s for show-quality
parts, this is about 210 to 400 h.

### 8.2 Filament prices (per kg, read 2026-11-11)

| Material | Maker and price | Source |
| --- | --- | --- |
| ABS | Bambu: MSRP $15.99/roll, $10.39/roll for 10+ rolls | [a] S60 |
| ABS | Elegoo: $18.99/kg; 5 kg $75.99; 10 kg $119.99 ($12.00/kg) | [a] S61 |
| ABS | Polymaker PolyLite ABS: from $18.99/kg | [a] S62 |
| ASA | Bambu: $17.99 sale ($29.99 typical) | [a] S60 |
| ASA | Elegoo: $16.99/kg; 10 kg $109.99 ($11.00/kg) | [a] S61 |
| ASA | Polymaker ASA: from $24.99/kg | [a] S62 |
| PETG | Bambu PETG HF: MSRP $15.99, $10.39 for 10+ (discontinued; new PETG replaces it) | [a] S60 |
| PETG | Elegoo PETG Pro $13.99/kg; Rapid PETG 20 kg $199.99 ($10.00/kg) | [a] S61 |

### 8.3 Low budget: Qidi Q2

| Item | Choice | Price |
| --- | --- | --- |
| Printer | Qidi Q2, active 65 C chamber, H12 + carbon | $499.00 |
| Filament | Elegoo ABS 10 kg + 5 kg | $195.98 |
| Plate and adhesion | Bambu liquid glue $14.99 + glue stick $3.99 (spare Qidi plate not priced) | $18.98 |
| Venting | AC Infinity Cloudline S4 duct fan (duct and window panel not priced) | $89.99 |
| Nozzles, wear parts | Qidi spare nozzles not priced | - |
| Dryer | Sunlu FilaDryer S4 (max 70 C; Bambu asks 75 to 85 C for ABS in an oven) | $116.99 |
| Solvents, cement, safety | Tamiya Cement for ABS $12.99; 3M 60926 cartridges (pair) $39.76; acetone, gloves and a half mask not priced | $52.75 |
| **Total, priced items** | | **$973.69** |

### 8.4 Middle budget: Bambu Lab H2S

| Item | Choice | Price |
| --- | --- | --- |
| Printer | Bambu H2S, active 65 C, G3 + H12 + carbon (sale price; $1,199 typical) | $1,049.00 |
| Filament | Bambu ABS, 15 rolls at the 10+ price | $155.85 |
| Plate and adhesion | Bambu Engineering Plate for H2D/H2S $59.99 + 2 liquid glue $29.98 | $89.97 |
| Venting | AC Infinity Cloudline S4 (duct and window panel not priced) | $89.99 |
| Nozzles, wear parts | 2 x Bambu Hotend H2/P2S/X2D at $17.99 | $35.98 |
| Dryer | Sunlu FilaDryer S4 | $116.99 |
| Solvents, cement, safety | As low budget | $52.75 |
| **Total, priced items** | | **$1,590.53** |

### 8.5 High budget: Prusa CORE One L+ with Advanced Filtration

| Item | Choice | Price |
| --- | --- | --- |
| Printer | Prusa CORE One L+ Advanced Filtration bundle (assembled, HEPA + carbon) | $1,980.56 |
| Filament | Polymaker ASA, 18 kg (ASA for less warp; or ABS) | $449.82 |
| Plate and adhesion | Bambu liquid glue (spare Prusa sheet not priced) | $14.99 |
| Venting | AC Infinity Cloudline S4 | $89.99 |
| Nozzles, wear parts | Prusa nozzles not priced | - |
| Dryer | Sunlu FilaDryer E2 (to 110 C; meets the 75 to 85 C ABS/ASA drying) | $249.99 |
| Solvents, cement, safety | As low budget | $52.75 |
| **Total, priced items** | | **$2,838.10** |

Notes on all three budgets:

- Prices are from 2026-11-11 and many are Black Friday prices; the regular price is higher.
- Tax and shipping are not included.
- Unpriced items (duct, window panel, acetone, half mask, nitrile gloves, spare plates and nozzles
  for non-Bambu printers) add to each total. The owner may already have a half mask and gloves from
  airbrush work.
- Alternative printers at about the same total: Low: Bambu P2S ($449, passive) or Elegoo CC2 ($369,
  passive). Middle: Anycubic Kobra S1 Max ($699, 350 cube, active 65 C) or Qidi Plus 5 ($749). High:
  Bambu H2D ($1,399).

Sources for the three tables: printers S57, S59, S63; filament S60 to S62; plates and glue S69d;
hotends S53; fan S68; dryers S69; cartridges S69b; cement S69c.

### 8.6 What the A1 still does after a switch

- All PLA, PETG and TPU parts: internal brackets, trays, the compute mount, jigs, test fits and
  drilling guides.
- Small ABS and ASA coupons and test pieces, in a ventilated place [a, S2].
- A second machine for parallel prints of non-show parts.

---

## 9. What would change in the design (question 8)

| Area | Change with ABS or ASA | Grade |
| --- | --- | --- |
| Shrink | Calibrate shrink per filament on a 100 block (X, Y, Z). The one study found ABS and PETG equal in XY (0.64 and 0.65 %). ABS grew in Z. | [b] S10; [d] |
| Joint clearance | For acetone welds the faces must touch; pure acetone fills no gap. Slurry fills small gaps; its limit is unknown. Keep the key fit from the PETG fit test, then re-test in ABS. | [c] S23; [d] |
| Welded seams | The flange becomes a weld. Keep screws as clamps while the weld cures. Keep acetone away from heat-set inserts and press fits (stress cracking). | [a] S29, S31; [d] |
| Groove | Keep the V-groove. Fill with slurry in thin layers. Wait at least one week before the final block sanding (to be proved on the coupon). | [c] S25, S25c; [d] |
| Wall and skin | Bambu warns that more than 6 walls and infill above 50 % raise warp. A dense 4 mm skin conflicts with this. Option: 3 to 4 walls each side with gyroid infill in the middle, and only enough wall at the groove that sanding cannot reach infill. | [a] S1; [d] |
| Ribs | Use ribs to keep flat tiles flat; give inner fillets at rib roots; avoid thick solid ribs. | [a] S1; [d] |
| Flat faces | Break long flat faces with shallow grooves on the inside; round all outside corners of flat parts. | [c] S40; [d] |
| Piece size | Keep flat pieces about 250 or less in any direction until a warp test on the chosen printer proves more. Use the larger bed for margin and for fewer 3-piece parts. | [d] |
| Filled grades | Consider ABS-GF or ASA-CF for floor tiles and hidden flat parts. | [a] S47; [c] S40 |
| Heat | HDT 84 C (1.8 MPa) gives more margin near the exhaust. No change in the vent design. | [a] S4 |
| Layer direction | Z impact is lower (ABS 7.4, ASA 4.9 against PETG HF 10.6). Orient loaded flanges so that load is not across layers. | [a] S1, S5; [d] |

---

## 10. Comparison table and the evidence that would decide

| Factor | PETG on the A1 (present plan) | ABS or ASA on a new enclosed machine |
| --- | --- | --- |
| Finish quality | Unknown until the coupon. Risk: ghost line from a filler of a different material; poor primer grip. | Unknown until a coupon. Gain: one material in the seam, sheets that name ABS. Risk: slurry shrink, stress cracking from solvents. |
| Finish effort | Higher in sanding (gums); scuff and prime every face. | Lower in sanding; same priming rule; longer waits for slurry. |
| Bond | MMA (gap filling) or solvent cement; data on sheet PETG only. | Acetone or slurry weld; tests on printed ABS show joints near part strength [b]. |
| Risk of failed prints | Low; PETG on the A1 is a supported use. | Higher on flat parts even with an active chamber [c]. |
| Set-up cost | About $200 of filament. | About $974 to $2,838 (priced items), plus unpriced items. |
| Time to first part | Now. | Order, delivery, set-up, vent, calibration, new coupons: weeks [d]. |
| Health and venting | PETG: particles about 10^9 per hour, low VOC [b]. Ordinary ventilation for printing; solvents only in finishing. | ABS: about 100 x the particles and more than 10 x the VOC (styrene) [b]; must vent outdoors, not in a living area [a]. ASA: fewer particles, still high VOC [b]. |
| Print area | 256: floor 6 tiles, full-width parts 2 or 3 pieces. | 300 or more: floor 4 tiles, full-width parts 2 pieces; flat-part size limited by warp. |

**Evidence that would decide, in order [d].**

1. **The PETG coupon test** (PETG note, section 4). If coupon A or D passes tests 2, 3 and 5 (flex, warm
   soak, seam look at 1 and 2 weeks), PETG meets the goal and the switch is not needed for finish.
2. **A small ABS/ASA coupon set on the A1**, open frame, in a ventilated place, at the same time:
   two coupons welded with acetone, two with slurry (one ABS, one ASA each), plus two plaques. Put
   one coupon through the hobby-lacquer test over primer near a heat-set insert (stress cracking).
   Use the same tests and pass rules as the PETG note. Cost: two rolls and a bottle of acetone.
3. **A place for the printer** with a duct to outdoors and a room above 15 C. No place, no ABS.
4. **A warp test** of the worst part (a floor tile about 290 x 268, or 250 x 250) on the candidate
   printer, from a review, a print service or a store demo. This decides between "bigger bed" and
   "same piece size, better material".
5. If the ABS coupons clearly beat the PETG coupons, and items 3 and 4 are met, then choose the
   budget. If both pass, the PETG plan wins on cost, time and health.

---

## 11. The reference cabinet maker (Rob Dunn, Multi Game System)

What he has said in public, as found:

- Feb 2024, on the first printed Astro City-style bartop: "This was all printed out of ABS filament on
  my fdm 3D printers. Lots of post work and paint to make it look like this." [c, S70]
- Jun 2025, a reel titled "How I glue my 3D Printed ABS plastic parts." The caption does not name the
  method; the video was not viewed [c, S71].
- Sep 2025, a reel titled "What I use to fill defects & voids in my bigger 3D prints", tagged
  #bodyfiller [c, S72].
- His profile shows a mini CRT replica "3D printed using my #bambulab A1" [c, S73, search summary].
  No post found names the printer used for the ABS cabinets.
- His studio page lists CAD, 3D printing, woodworking, UV printing and spray painting [c, S74].
  His 2015 cabinets were MDF with Apoxie Sculpt and an acrylic lacquer finish [c, S75].
- Nothing was found about cut acrylic plates, his primer, or his paint.

So he confirms ABS and body filler, but gives no printer, chamber, glue or primer detail in the
captions that could be read.

---

## 12. Sources

All sources were read on 2026-11-11.

### Sources read

| No. | URL | What it is |
| --- | --- | --- |
| S1 | https://wiki.bambulab.com/en/filament/abs_asa_pc | Bambu ABS/ASA/PC guide: properties table, A-series not compatible, glue, drying, warp and crack causes, health. [a] |
| S2 | https://wiki.bambulab.com/en/a1/manual/faq | Bambu A1 FAQ: ABS/ASA only small low-infill parts; do not enclose the A1. [a] |
| S3 | https://wiki.bambulab.com/en/software/bambu-studio/chamber-temperature | Bambu chamber temperature guide: 60 C for large ABS/ASA; filtration worse with heating. [a] |
| S4 | https://store.bblcdn.com/s7/default/23b4cf2b83d5470bb96d19970b5f3ae8/Bambu_ABS_Technical_Data_Sheet_V3.pdf | Bambu ABS data sheet V3 (search summary of full table). [a] |
| S5 | https://store.bblcdn.com/3a230e260a3a47c2b0db0156e07eef91.pdf | Bambu PETG HF data sheet V1.0 (read). [a] |
| S6 | https://bambulab.com/en/support/buying-guide | Bambu buying guide: current lineup, H3C specs and space needs. [a] |
| S6b | https://bambulab.com/en-us/h2s/tech-specs | Bambu H2S specs: 340 x 320 x 340, 65 C, H12. Also https://bambulab.com/en-us/h2d-pro/tech-specs (H2D Pro). [a] |
| S6c | https://3dprinting.com/3dprinters/bambu-lab-3d-printer-comparison/ | Secondary comparison of the Bambu lineup: specs, filtration, prices (checked Sept and Nov 2026). [c] |
| S7 | https://bambulab.com/en-us/p2s/specs | Bambu P2S specs: no chamber heater, 110 C bed, carbon filter. [a] |
| S7b | https://bambulab.com/en-us/x2d/specs | Bambu X2D specs: 65 C active chamber, 120 C bed. [a] |
| S8 | https://help.prusa3d.com/article/abs_2058 | Prusa ABS guide: warp, enclosure, shrink 1 to 2 %, sanding, acetone. [a] |
| S9 | https://help.prusa3d.com/article/asa_1809 | Prusa ASA guide: warps less, acetone weld, smell. [a] |
| S10 | https://3dcalculators.com/blog/abs-shrinkage | Summary of the Binghamton (Weiser 2021) printed shrink study and resin figures; also /blog/asa-shrinkage. [c, secondary to [b]] |
| S11 | https://www.sciencedirect.com/science/article/pii/S0160412023005895 | Zhang et al. 2023, Environment International: 447 particle and 58 VOC runs. [b] |
| S12 | https://ncbi.nlm.nih.gov/pmc/articles/PMC9229569/ | 2022 study: VOC from ABS, ASA, nylon, PETG by PTR-ToF-MS. [b] |
| S12a | https://pubs.acs.org/doi/10.1021/acs.est.5b04983 | Azimi et al. 2016, ES&T: UFP and VOC from 5 printers. [b] |
| S14 | https://www.ncbi.nlm.nih.gov/books/NBK551037/ | IARC Monographs vol. 121, evaluation: styrene Group 2A. [a] |
| S15 | https://www.cdc.gov/niosh/docs/2024-103/pdfs/2024-103.pdf | NIOSH 2024 guide, safe 3D printing (search summary). [a] |
| S16 | https://www.cdc.gov/niosh/bulletin/2018/3d-printing.html | NIOSH science bulletin: controls for printer emissions. [a] |
| S20 | https://www.sciencedirect.com/science/article/abs/pii/S1755581720300857 | Saraf et al. 2020: acetone joining of printed ABS (abstract). [b] |
| S21 | https://www.sciencedirect.com/science/article/abs/pii/S0143749625002933 | 2025 paper: adhesives and ABS/acetone on printed ABS lap joints (intro and method via search summary). [b] |
| S22 | https://ouci.dntb.gov.ua/en/works/7XaZjkGZ/ | Abstract: ABS slurry adhesive on printed PLA, 8.69 MPa, aging. [b] |
| S23 | https://www.reddit.com/r/prusa3d/comments/14jp4k6/use_just_acetone_or_create_a_asa_slurry_for/ | Users: acetone alone evaporates; slurry fills (search summary; also threads 14m9cxw, ic2s0z). [c] |
| S24 | https://www.matterhackers.com/news/how-to-make-abs-juice-glue-and-slurry | ABS juice, glue and slurry recipes. [a] |
| S24b | https://forum.bambulab.com/t/nobodys-home/56992?page=3 | User warning: acetone attacks PEI (search summary). [c] |
| S25 | https://3dx.info/abs-post-processing-methods/ | ABS post-processing: slurry shrinks, thin layers. [c] |
| S25b | https://hackaday.com/2011/12/16/welding-and-casting-abs/ | Early report: ABS glue shrinks as it dries (search summary). [c] |
| S25c | https://fusionscalehobbies.com/blogs/news/best-glue-for-plastic-models | Model guide: trapped solvent makes seams show; wait 24 h (search summary). [c] |
| S26 | https://carfitrepair.com/wp-content/uploads/2023/05/car-fit-plastic-putty-technical-data-sheet.pdf | C.A.R.FIT Plastic Putty data sheet: substrates include ABS. [a] |
| S27 | https://mobicolor.bg/wp-content/uploads/2017/06/400905-MOBIHEL-PLASTIC-PUTTY.pdf | Mobihel Plastic Putty: PP, ABS, PC, PA, PUR, PPO (search summary). [a] |
| S27b | https://www.service.european-aerosols.com/en/tm-1634.html | Plastic filler spray: adheres to PP, PUR, ABS (search summary). [a] |
| S28 | https://conceptpaints.com.au/sites/default/files/content/Plastic%20Primer%20Aerosol%20TDS.pdf | Concept 1K plastic primer: substrates include ABS. [a] |
| S29 | https://buyat.ppg.com/Refinish_SSA/Common/ShowPdf.aspx?AppId=2&BrandId=2&LanguageId=3&IntDialCode=44&PdfId=16374&ProductCode=1.823.1500 | PPG 1K adhesion promoter for "solvent sensitive plastics, such as PC, ABS" (search summary). [a] |
| S30 | https://www.mipa-paints.com/fileadmin/product/gb/pi/lm/Mipa_1K-Primer_N_75_Spray_EN.pdf | Mipa 1K-Primer N 75: adheres to ABS, PC, PS and others (search summary). [a] |
| S31 | https://www.mr-hobby.com/ja/products/detail/110 | Mr. Hobby Acrysion page: low solvent for thin ABS parts easily damaged by solvent; also FAQ https://www.mr-hobby.com/en/qa (no paints for PC). [a] |
| S31b | https://www.mr-hobby.com/uploads/catalogs/01JKD5G4EHDEPZ097VHX17M7NX.pdf | Mr. Hobby catalogue 2024-2025: "If ABS crack" mark (search summary). [a] |
| S32 | https://www.hobbyco.com.au/blogs/blog/tamiya-cement-guide-which-plastic-model-glue-should-you-use | Retailer guide: Tamiya cements for polystyrene; Cement for ABS. [c] |
| S32b | https://www.reddit.com/r/3Dprinting/comments/cwaej1/gluing_pla_and_tamiya_extra_thin_cement/ | User: Tamiya cement "might work on HIPS" (search summary). [c] |
| S33 | https://www.youtube.com/watch?v=kPUQSVhB11U | Gunpla test video: panel liner cracks stressed parts; plus Reddit r/Gunpla threads 10mciwv, 10b5c8p, 17g020b, 1mf31y8 (search summaries). [c] |
| S34 | https://www.reddit.com/r/3Dprinting/comments/yip2av/abs_prints_cracking_after_acetone_smoothing/ | User: ABS cracked after acetone vapour smoothing (search summary). [c] |
| S35 | https://additive.tools/materials/asa | Reference site: acetone bond not effective on ASA, MEK suggested. [c] |
| S40 | https://forum.bambulab.com/t/h2s-i-cannot-prevent-my-prints-from-warping/214871 | Forum thread: full-plate ABS warp on H2S at 65 C; advice. [c] |
| S41 | https://www.reddit.com/r/QIDI/comments/1f0wkhg/abs_warps_even_with_seemingly_proper_printing/ | User: large flat thick ABS parts warp (search summary). [c] |
| S42 | https://www.reddit.com/r/BambuLab/comments/1b3wgnl/p1s_and_abs_can_the_p1s_really_do_abs_well/ | User: P1S ABS fine except large flat sharp corners (search summary). [c] |
| S42b | https://www.reddit.com/r/BambuLab/comments/15u87ys/abs_on_my_p1s_finally_dialed_in/ | User: preheat to 45 C chamber (search summary). [c] |
| S42c | https://www.reddit.com/r/3Dprinting/comments/1thny5j/is_a_heated_chamber_really_that_important_for/ | User: bed preheat gives almost 60 C (search summary). [c] |
| S43 | https://www.reddit.com/r/QIDI/comments/1g2dkb4/psa_you_cannot_print_heated_chamber_models_at/ | Thread: Plus4 heater outlet blocked above Z 250; X-Max 3 ABS helmet at 60 C. [c] |
| S44 | https://www.reddit.com/r/BambuLab/comments/1lao663/the_h2d_has_made_abs_prints_feasible_for_me/ | User: H2D made ABS feasible (search summary). [c] |
| S45 | https://www.reddit.com/r/BambuLabA1/comments/1s4nms6/asaabspa_on_a1/ | User: A1 in a tent with a PTC heater (search summary). [c] |
| S45b | https://forum.bambulab.com/t/enclosure-heater-discovery/192750 | Forum: heat creep with a heated enclosure; A1 mainboard and PSU overheating warning. [c] |
| S45c | https://www.reddit.com/r/BambuLab/comments/1e0v00s/printing_abs_and_asa_with_the_a1_series/ | Users: small ABS parts on an open A1 (search summary; also 18nidpu). [c] |
| S46 | https://forum.bambulab.com/t/p2s-warping-issue-from-first-print/212662 | User: P2S warp on full-width prints (search summary). [c] |
| S47 | https://wiki.bambulab.com/en/filament/absgf_pa6gf | Bambu ABS-GF guide and properties. [a] |
| S47b | https://wiki.bambulab.com/en/filament/asacf_pahtcf | Bambu ASA-CF properties (search summary). [a] |
| S48 | https://www.3dmag.com/3d-printers-comparison/creality-k2-vs-k2-plus/ | Comparison citing Creality: chamber target not reached on 110 V below 15 C. [c, quoting [a]] |
| S49 | https://www.fauxhammer.com/de/reviews/bambu-x2d-review-great-value-smart-features-and-one-big-problem/ | X2D review: right-nozzle exclusion zone. [c] |
| S50 | https://store.creality.com/eu/blogs/buying-guides/creality-k2-vs-k2-pro-vs-k2-plus | Creality K2 series specs. [a] |
| S51 | https://store.creality.com/products/creality-k2-plus-combo-3d-printer | Creality US store: K2 Plus Combo $1,099; K2 Pro Combo $749 from https://store.creality.com/products/k2-pro-combo-3d-printer (search summary). [a] |
| S52 | https://us.store.bambulab.com/products/bambu-dual-texture-pei-plate | Bambu plate table: ABS on textured PEI without glue. [a] |
| S53 | https://us.store.bambulab.com/products/bambu-hotend-h2-p2s | Bambu Hotend H2/P2S/X2D from $17.99; nozzle and filament table. [a] |
| S54 | https://www.flashforge.com/products/flashforge-creator-5-pro | Flashforge Creator 5 Pro: 256 cube, 65 C, $849 (search summary); comparison https://www.flashforge.com/blogs/news/flashforge-3d-printer-model-comparison. [a] |
| S54b | https://filascope.com/printers/flashforge-guider-4 | Guider 4 specs and price (secondary). [c] |
| S55 | https://store.anycubic.com/products/kobra-s1-max | Anycubic Kobra S1 Max: 350 cube, 65 C, $699 (search summary); carbon filter on https://www.anycubic.com/en/kobra-s1-max-combo. [a] |
| S56 | https://us.snapmaker.com/products/snapmaker-u1-3d-printer | Snapmaker U1: 270 cube, $699; top cover https://us.snapmaker.com/products/top-cover-for-snapmaker-u1 $149, 50 C passive. [a] |
| S56b | https://www.tomshardware.com/3d-printing/snapmaker-u1-review | Review: ASA printed on the U1 without the lid. [c] |
| S57 | https://www.prusa3d.com/product/prusa-core-one-l-advanced-filtration-bundle-2/ | Prusa CORE One L+ Advanced Filtration bundle $1,980.56; specs from https://www.prusa3d.com/p/core-one-l/ and https://www.prusa3d.com/product/prusa-core-one-l-2/. [a] |
| S58 | https://www.sovol3d.com/blogs/news/black-friday-3d-printer-buying-guide-which-sovol-printer-is-right-for-you | Sovol lineup and prices; M1D Advanced 60 C. [a] |
| S59 | https://us.store.bambulab.com/collections/h2-series | Bambu US Black Friday price list (2026-10-27 to 2026-12-01) (search summary); also https://us.store.bambulab.com/collections/3d-printer. [a] |
| S60 | https://us.store.bambulab.com/products/abs-filament | Bambu ABS price; ASA https://us.store.bambulab.com/products/asa-filament; PETG HF https://us.store.bambulab.com/products/petg-hf (search summaries). [a] |
| S61 | https://us.elegoo.com/collections/asa-filaments-for-fdm-3d-printers | Elegoo ABS, ASA prices and bulk; PETG https://us.elegoo.com/collections/filaments and https://us.elegoo.com/products/rapid-petg-filament-20kg (search summaries). [a] |
| S62 | https://shop.polymaker.com/products/asa | Polymaker ASA from $24.99; PolyLite ABS https://shop.polymaker.com/products/polylite-abs from $18.99 (search summaries). [a] |
| S63 | https://qidi3d.com/blogs/news/qidi-3d-printer-comparison | Qidi lineup: Q2C, Q2, Plus 4 (discontinued), Plus 5, Max4; specs and prices (Sept 2026). [a] |
| S64 | https://us.elegoo.com/products/centauri-carbon-2-combo | Elegoo CC2 Combo $369 sale, $449 list (search summary; page fetch refused, HTTP 429). [a] |
| S65 | https://www.formbot3d.com/collections/voron-24 | Formbot Voron 2.4 kit price; Siboor https://www.siboor.com/product/siboor-voron2-4-upgrade-dragon-corexy-3d-printer-350mm-fdm-diy-full-set-wifi-control/. [a] |
| S65b | https://3dprintgearlab.com/guides/voron-3d-printer/ | Secondary: LDO kit prices, build time. [c] |
| S65c | https://www.reddit.com/r/VORONDesign/comments/1b2ravb/cant_decide_on_what_kit_to_buy/ | Users on kit quality (search summary). [c] |
| S66 | https://ratrig.com/products/rat-rig-v-core-4-1 | Rat Rig V-Core 4.1: open frame, panels not included; US page https://ratrig.com/products/rat-rig-v-core-4-us. [a] |
| S67 | https://us.store.creality.com/products/3d-printer-multifunction-enclosure | Creality tent enclosure $79.99. [a] |
| S68 | https://acinfinity.com/inline-fan-systems/ | AC Infinity Cloudline S4 $89.99 (search summary). [a] |
| S69 | https://store.sunlu.com/collections/sunlu-filament-dryer | Sunlu S4 $116.99 (70 C) and E2 $249.99 (110 C). [a] |
| S69b | https://www.bayshoresafety.com/product-page/3m-60926-multi-gas-vapor-cartridge-filter-p100/ | 3M 60926 cartridge pair $39.76. [a, retailer] |
| S69c | https://www.ebay.com/itm/405491330568 | Tamiya Cement for ABS 87137, $12.99. [a, retailer] |
| S69d | https://us.store.bambulab.com/products/bambu-engineering-plate | Bambu Engineering Plate; H2D/H2S size $59.99 on https://us.store.bambulab.com/pages/promotions/BuildPlateBulkSale; liquid glue $14.99, glue stick $3.99. [a] |
| S70 | https://www.instagram.com/p/C3GgWXQxsAf/ | Rob Dunn, Feb 2024: printed in ABS, lots of post work and paint (search summary). [c] |
| S71 | https://www.instagram.com/reel/DLPw8JHsSgV/ | Rob Dunn, Jun 2025: "How I glue my 3D Printed ABS plastic parts" (caption only). [c] |
| S72 | https://www.instagram.com/reel/DO1OjoxjX89/ | Rob Dunn, Sep 2025: filling defects, #bodyfiller (caption only). [c] |
| S73 | https://www.instagram.com/robertdunnart/ | Rob Dunn profile: mini CRT printed on a Bambu A1 (search summary). [c] |
| S74 | https://multigamesystem.wixsite.com/home/about | Multi Game System about page (search summary). [c] |
| S75 | https://hyperspin-fe.com/forums/topic/10897-candy-cabinet-inspired-bartops-by-multi-game-system/ | 2015 forum post: MDF cabinets with Apoxie Sculpt; also https://medium.com/attract-mode/the-miniaturized-astro-city-weve-all-been-waiting-for-f6e47ce0047b (acrylic lacquer). [c] |

Note on the source numbers: S13, S17 to S19 and S36 to S39 are not used.

### Sources that were not accessible or read only in part

| Source | Result |
| --- | --- |
| bambulab.com spec and store pages | Direct fetch refused (HTTP 403 or 402). Read through a page extractor or search summaries. |
| Bambu US store printer prices | Read from search summaries of store pages dated 2026-10-28 and later. Not confirmed on a live cart. |
| Qidi Q2 price | One Qidi page shows $499 and $449. |
| Creality K2 Pro price | Search summary of the store page only. |
| Elegoo CC2 page | HTTP 429. Search summary only; filtration not confirmed. |
| Polymaker product pages | HTTP 429. Search summaries only. |
| ScienceDirect papers S11, S20, S21 | Fetch refused; abstracts and summaries only. The S21 strength value is from a citing page. |
| Reddit threads | Direct fetch blocked; S43 read in full through an extractor; others by search summary. |
| Rob Dunn videos | Not viewed. Captions only. Facebook not opened (log-in). |
| Creep data, coefficient of thermal expansion for printed ABS and ASA | Not found in the data sheets read. |
| Bambu E1 purifier US price | Not found (Canada store: CAD 269). |
| Spare plates and nozzles for Qidi and Prusa | Not priced. |
