# Finishing PETG: bond, fill, prime and paint

Research date: 2026-11-11. All dimensions in millimetres unless a unit is given.

This note answers one question from the owner: which fillers, adhesives and paints work on
printed PETG, so that the bonded shell shows no seam. It extends the brief section "CAD printing
and finish" in `docs/Arcade_Project_Current_Design_2026-11-09.md`. It does not repeat it.

The shell is PETG, printed on the Bambu A1, with a 4 mm skin. Pieces bond for good on inside
flanges with screws. Each outer seam gets a small V-groove. The whole shell is then filled,
sanded, primed and painted. Some parts (the black bezel, the speaker forms, the rear door) are
painted alone and fastened after paint. The material stays PETG. This note does not argue for a
change of material.

Every product name is an example of a class. No product was bought or tested for this note.

## Terms

| Term | Meaning in this note |
| --- | --- |
| Bond | The structural adhesive joint on the inside flange. |
| Seam | The line on the outer face where two pieces meet. |
| Groove | The V cut along the seam on the outer face, for the filler. |
| Filler | Any product that is put on for appearance only: putty, coating or filler primer. |
| Key | The scratch pattern that sanding gives, which a coating grips. |
| Ghost line | A seam or a sanding mark that shows again through the paint days or weeks later. |
| Coupon | The curved two-piece test part that the brief asks for. |

## Evidence grades

| Grade | Meaning |
| --- | --- |
| [a] | A maker's data sheet, guide or FAQ: an adhesive, paint or filler maker, a PETG sheet maker or a filament maker. |
| [b] | A published test with a stated method (a paper, or a maker's test table with its method). |
| [c] | Reports from users: forums, blogs, prop builders. The count of independent reports is given. |
| [d] | Our reasoning or calculation, not from a source. The method is given. |

Source numbers in square brackets, for example [S3], point to the list in section 7.

Most finishing guides are written for PLA or ABS. PETG differs from both. Section 2.0 gives the
differences first, because they change most of the answers.

---

## 1. Summary

### 1.1 First candidate system

| Step | Class | Example products | Reason |
| --- | --- | --- | --- |
| 1. Bond | Two-part methacrylate (MMA), slow grade | Plexus MA310 (15 to 18 min work time) | Two PETG sheet makers list Plexus MA300/MA310 for copolyester [a]. It fills gaps of 0.25 to 3.2 and stretches 20 to 40 % [a]. The work time covers a 500 seam. |
| 2. Weld the groove (optional, coupon decides) | Same PETG filament, melted in | Friction weld with a rotary tool, or a 3D pen | The outer skin becomes one material. No filler line with a different stiffness or expansion sits in the seam [c, 5 reports; Polymaker guide [a]]. |
| 3. Level | Sanding, wet, by hand and block | P180 then P240 wet, slow, fresh paper | PETG gums when dry-sanded [a, 2 sheet makers]. Wet sanding gives a smoother face [a]. |
| 4. Fill the groove and the defects | Two-part polyester glazing putty that lists plastics | Evercoat Metal Glaze; Evercoat Poly-Flex as the flexible option | The only polyester fillers found whose data sheets list "rigid to semi-rigid plastics" [a]. Max 3 sanded thickness [a]. |
| 5. Seal and prime | Two-part epoxy primer, isocyanate free (amine activator) | SprayMax 2K Epoxy Primer (aerosol) | Tough film; Eastman says tough, flexible films hold better on copolyester than rigid, brittle films [a]. Evercoat lists 2K epoxy as a topcoat over its putty [a]. No PETG data: the coupon must prove it. |
| 6. Build | One-part high-build filler primer | Dupli-Color Filler Primer, Rust-Oleum Filler Primer; Mr. Surfacer 500/1000 for small parts | Fills P240 to P320 marks. Sands easily. Spray-putty and filler primers passed a tape test on bare PETG in one user test [c]. |
| 7. Spot putty | One-part lacquer putty, thin, over primer only | Bondo Glazing & Spot Putty; Tamiya Putty Basic | For pinholes in primer only. Bondo lists primed surfaces, not bare plastic [a]. Thick coats crack [a]. |
| 8. Colour | One-part acrylic lacquer or enamel aerosol, or airbrushed hobby lacquer | Dupli-Color lacquer; Mr. Color / Tamiya LP by airbrush | Goes over the sealed primer, not over bare PETG. The owner's Gunpla airbrush work applies here. |
| 9. Clear (optional) | One-part acrylic lacquer clear or water-based clear | Dupli-Color 1K Clear; Mr. Super Clear; Mr. Hobby Premium Topcoat | No isocyanate. The brief excludes isocyanate 2K clear [brief; HSE [a]]. |

Wait times that the system needs: polyester putty at least 24 h before the final block sanding;
filler primer at least 48 h before its final sanding; colour at least 7 days before the shell
goes near the warm exhaust. Section 2.3 gives the sources.

### 1.2 Second candidate system

| Step | Change from the first candidate | Reason |
| --- | --- | --- |
| 1. Bond | Solvent cement that lists PETG, by capillary into the clamped flange, screws as clamps. Example: Weld-On 4 (Vivak lap-shear data), SCIGRIP 16 (user reports). | One PETG sheet maker measured 1,800 to 2,100 psi (12 to 14 MPa) lap shear after one week with Weld-On 3 and 4 [b]. No gap filling. Cements of this family can contain methylene chloride (section 6). |
| 4. Fill | Epoxy coating that lists PETG over the seam area. Example: Smooth-On XTC-3D. | The XTC-3D bulletin names PETG [a]. No solvent. It self-levels into layer lines. |
| 5. Prime | One-part filler primer direct on scuffed PETG, no epoxy primer. | Fewer products, no two-part aerosol. User tests pass [c], but one published test of a two-part plastic paint on unsanded PETG failed (class 3 cross-cut) [b]. |

### 1.3 Findings that change the plan

1. **Polyester body filler is not made for thermoplastics.** The Bondo body filler data sheet
   lists steel, galvanised steel, aluminium, SMC and FRP only [a, S16]. Prop builders still use
   it on PETG [c, many reports; Prusa guide [a]], but it cracks over seams that flex [c, 2
   reports]. Use a polyester *glazing* putty that lists plastics (Evercoat Metal Glaze,
   Poly-Flex) for the groove, and keep it thin.
2. **The 3M DP8005 and DP8010 plastic adhesives are a poor fit.** Neither data sheet lists PETG.
   DP8005 has a work life of 2.5 to 3 min and a Tg of 33 C [a]. DP8010 has a Tg of 61 C, and its
   strength on aluminium falls from 1,800 psi at 23 C to 1,000 psi at 49 C [a]. Both are made for
   polyolefins, which PETG is not. A general MMA (Plexus MA310) is the better candidate.
3. **Bare PETG resists the solvents that make hobby paints and many primers grip.** Mr. Hobby
   says its paints "slightly dissolve polystyrol" to grip, and asks for a primer surfacer on
   solvent-resistant materials [a]. Eastman says some solvent-based paints made for PC or acrylic
   "may not be sufficiently active" on copolyester [a]. A published test of a two-part plastic
   paint on degreased, unsanded PETG gave cross-cut class 3 and adhesion failure at the PETG
   face [b]. Scuff every face. Prime every face. Never put colour direct on bare PETG.
4. **Most adhesion promoters are for polyolefins.** SEM Plastic Adhesion Promoter lists
   "olefin-based plastics" only [a]. The Rust-Oleum plastic primer lists PP, PS, PVC, fibreglass
   and vinyl, not PETG [a]. Neither is proof of a benefit on PETG. The coupon must test one.
5. **PETG is softer than every filler that sands well.** PETG gums and fuzzes [a, c]. A hard
   filler (CA, epoxy putty, body filler) stands proud after sanding and leaves a ridge. Block-sand
   across the seam, and finish the filler at P180 to P240, not at P80 [c].

### 1.4 What stays unknown until the coupon

- Whether Plexus MA310 bonds printed PETG (not sheet) with failure in the PETG and not at the
  face. No published test on printed PETG was found.
- Whether SprayMax 2K epoxy primer and Evercoat Metal Glaze hold on scuffed printed PETG. Their
  data sheets do not name PETG.
- Whether an adhesion promoter adds anything on PETG.
- Whether a groove filled with polyester putty shows a ghost line after warm soak and two weeks.
- Whether friction welding the groove distorts a 4 mm wall.

---

## 2. Answers to the seven questions

### 2.0 Where PETG differs from PLA and ABS

| Property | PETG | What it changes | Grade |
| --- | --- | --- | --- |
| Sanding | Gums with dry sanding; wet sanding gives a smooth face | Wet-sand, slow, fresh paper. Guides for PLA under-state the time. One prop shop gives about one hour on PETG for a part that takes 20 min on PLA. | [a] S1, S2; [c] S30, S31 |
| Solvents | Resists IPA, alcohol, hexane, petrol. Not resistant to acetone, MEK, toluene, ethyl acetate, methylene chloride, THF | Acetone smoothing (ABS) does not work. Strong solvents can whiten or craze stressed PETG. Lacquer paints do not "bite" as they do on ABS or styrene. | [a] S1 |
| Solvent welding | Possible with methylene chloride, MEK blends, Weld-On 3 and 4 on sheet | Users report MEK does not soften their filament. Filament grades differ. | [b] S1; [c] S27 |
| Surface energy | "Moderate to low", lower than PLA (one filament maker) | Abrasion and a solvent wipe matter more than on PLA. | [a] S9 |
| Heat | HDT 62 C at 1.8 MPa and 69 C at 0.45 MPa (Bambu PETG HF); 68 / 71 C (PETG Basic); Vicat 69 to 70 C | Higher than PLA (about 55 to 60 C). Lower than ABS. Do not force-cure coatings at 60 C on the shell. | [a] S7, S8 |
| Thermal expansion | 3.8 x 10^-5 in/in/F, which is 68 x 10^-6 per K (Vivak sheet) | See 2.3. | [a] S1 |
| Toughness | Bends before it breaks | A rigid, brittle film on PETG cracks when the part flexes. Choose tough coatings. | [a] S3 |

### 2.1 Surface preparation

**Sanding.**

- Vivak (a PETG sheet maker): "Gumming can result from dry sanding. Wet sanding produces a smooth
  finish." [a, S1]. Prusa: PETG sands "both dry and wet" [a, S4]. Two prop-finishing guides say
  PETG fuzzes and needs fresh paper and wet sanding [c, S30, S31]. Agreement: 4 sources.
- Grits: Polymaker starts at P220 for most materials and warns that coarser grits on power tools
  risk heat [a, S5]. Evercoat sands its putty at P180 then P220 to P320 [a, S14]. Car-body
  practice: finish filler work at P180 to P220 before primer; P80 marks come back through primer
  [c, S36, S37]. Use P120 only to knock down a ridge, then P180, P240 wet, P320 wet before primer.
- Tools: use a hard block across the seam, and a soft pad on curves. A random-orbit sander at low
  speed is acceptable on flat faces. Stop when the paper loads. Polymaker warns about heat from
  power sanders and rotary tools [a, S5]. Heat gums PETG and raises the fibres again [d].
- Do not sand through the 4 mm skin into infill near the seam. Prusa shows that sanding through to
  infill needs extra filler [a, S6].

**Cleaning.**

- Use IPA, or a 50:50 IPA and water mix. Eastman and Vivak both give this mix [a, S1, S3]. PETG
  resists IPA [a, S1]. Do not use acetone or lacquer thinner as a wipe; Vivak lists both classes
  as attacking PETG [a, S1].
- Wash with water and a mild detergent first if the part has finger grease or glue-stick residue.
  Mr. Hobby gives the same advice for oil and mould release, and says to rinse the detergent off
  [a, S22].

**Key, promoter, flame.**

- Scuffing gives the key. Vivak: "Light sanding of factory polished surfaces will aid in
  adhesion" [a, S1]. Eastman: fine-grit sanding "may improve bond strength" [a, S3]. The one
  published coating test on printed PETG used a degrease only, no abrasion, and got class 3
  [b, S10]. A conservation study on printed PLA and ABS found that solvent and abrasion
  preparation gave the best paint adhesion [b, S12, abstract only].
- Promoters: SEM lists olefins only [a, S20]. Dupli-Color says its promoter helps "all surfaces,
  including plastic" but gives no substrate list [a, S21]. One user uses a promoter on PETG with
  automotive paint and reports good results, also on boats [c, S28]. Golden (a paint maker) found
  that its acrylics held well on PETG with no primer, and that most primers it tried *slightly
  reduced* adhesion of its acrylics on prints [a/b, S11]. The sources disagree. Put one promoter
  in the coupon.
- Flame: Evercoat gives flame treatment for olefin plastics only [a, S15]. A filament maker
  mentions flame or plasma for PETG bonding, with no data [a, S9]. Vivak warns that flame
  polishing can cause long-term edge cracking [a, S1]. Do not flame the shell. A 4 mm wall
  distorts at about 70 C [d from S7].

### 2.2 Fillers on PETG, by class

| Class | Example | Maker data on plastics | Thickness | Shrink | Sands vs PETG | Solvent or heat risk to PETG | Over a flexing seam | Grade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Two-part polyester body filler | Bondo Body Filler, 3M Lightweight | Lists steel, galvanised steel, aluminium, SMC, FRP. Not thermoplastics. Service to 82 C. | Bulk; shape sand 8 to 12 min | Shrinks in the first hours [c] | Harder than PETG; leaves a ridge if not blocked | Contains styrene monomer [a]. No PETG data for styrene. | Cracks if the seam hinges [c, 2 reports] | [a] S16, S17; [c] S25, S26 |
| Two-part polyester glazing putty | Evercoat Metal Glaze; Poly-Flex | Metal Glaze: "Most Rigid to Semi-Rigid Plastics". Poly-Flex adds "Flexible Plastics". Metal Glaze Ultra: thermoset plastics only. | Max 3 sanded | Low; "pinhole-free" | Sands easier than body filler; Poly-Flex is softer | Styrene class. No PETG data. | Poly-Flex is made for bumpers that flex | [a] S13, S14 |
| One-part lacquer spot putty | Bondo Glazing & Spot Putty | Lists metal, fibreglass, wood, "sanded and primed or painted surfaces". Not bare plastic. | Thin coats only; "Thick applications are subject to cracking" | Shrinks as the solvent leaves | Sands easily, wet or dry, P320 to P400 | Contains xylene, acetone, MIBK, glycol ether, nitrocellulose [a]. Acetone is on Vivak's attack list. | Brittle | [a] S18, S19 |
| Epoxy putty | Milliput, Apoxie Sculpt | No maker data on PETG found. | Thick; sculpts | Very low (no solvent) | Hard; hard to feather | None from solvent. Small exotherm in thin layers [d]. | Rigid. One user: it "can be scratched off" a print [c]. | [c] S29 |
| Epoxy coating | Smooth-On XTC-3D | "It works with PLA, ABS, PetG" | Under 0.4 per coat, self-levels | Low | Sands; harder than PETG | "High exotherm" in mass; mild heat 60 C cures in 15 min. Keep it at room temperature on PETG. | Rigid | [a] S23 |
| UV resin as filler | Printer resin, UV glue | No maker data. Vivak: UV curing lamps "attack" Vivak in screen printing. | Thin | Some | Hard | Users report PETG parts that weakened after contact with uncured resin (3 brands, one user) | Brittle | [a] S1; [c] S33 |
| CA with a powder | Thin CA plus baking soda or talc | Loctite: CA on PET gave bonds stronger than the PET in most grades. | Small spots | Low | Much harder than PETG; ridge | "May stress crack some plastics" (Loctite, general) | Brittle; poor peel | [a] S24; [c] S25 |
| High-build filler primer, one-part | Dupli-Color Filler Primer, Rust-Oleum Filler Primer | Dupli-Color: lightly sand glossy faces; sand after 30 min | 2 light + 1 wet coat | Shrinks over about 2 days [c] | Sands easily | Aerosol solvents; light coats with flash time avoid trapped solvent [c] | Brittle in thick build | [a] S21; [c] S28, S34, S35 |
| High-build filler primer, two-part | SprayMax 2K Epoxy Primer Filler | Lists metals, FRP, "polyester surfaces", old paint. Not thermoplastics. Amine activator, no isocyanate. | Primer-filler | Low | Sands; tough | Pot life about 3 days at 20 C | Tougher than 1K [d] | [a] S19b |
| Acrylic spackle, wood filler | Lightweight spackle | Polymaker: easy, but "Prone to dents/scratches" | Thin | Shrinks (water) | Very soft | None | Poor | [a] S5; [c] S25 |
| Hobby filler primer | Mr. Surfacer 500/1000, Mr. Primer Surfacer | Mr. Hobby: on solvent-resistant materials use a primer or primer surfacer first | Brush or airbrush; thin | Shrinks as solvent leaves | Sands easily | Lacquer solvent with acetone [c]. It does not bite PETG as it bites styrene. | Thin films only | [a] S22; [c] S38 |
| Hobby lacquer putty | Tamiya Putty Basic, Mr. Dissolved Putty | Tamiya putty is polystyrene in solvent; it "reacts chemically with plastic (polystyrene)" | Thin | High | Easy | On PETG it grips only by key [d] | Brittle | [c] S39 |

**Conclusions on fillers.**

- No filler data sheet names PETG except the XTC-3D bulletin [a]. The Evercoat polyester
  glazing putties name "rigid to semi-rigid plastics" [a]. These are the best-supported classes.
- A tape test by one user found that a spray-putty primer and a plastic primer filler held on
  unsanded PETG; the coating came off only with the plastic under a knife [c, S32]. Golden
  found that acrylic paints held well on PETG with no primer [a/b, S11]. A two-part industrial
  plastic paint on degreased, unsanded PETG gave class 3 [b, S10]. The sources disagree; the
  surface preparation and the products differ. Section 4 tests the question.
- Hard fillers leave ridges against the softer PETG. Put filler only in the groove and in
  defects. Do not skim the whole shell with body filler. Use filler primer for layer lines.

### 2.3 Seams

**Why seams come back.**

1. Shrink of the filler or primer after sanding. Car-body painters report that most primer
   shrink is over in about 2 days, that body fillers shrink in the first hours, and that coarse
   marks (P80) under primer come back as the coatings cure [c, S34, S35, S36]. A 2K-surfacer
   guide gives 8 to 24 h before blocking at 21 C, and warns of ghost scratches weeks later if
   sanded early [c, S37].
2. A seam that moves. If the joint hinges, the filler cracks along it. One user bonded and filled
   a seam three times and it cracked each time after primer; the replies said the seam flexes and
   should be welded on the inside first [c, S25].
3. Different expansion and stiffness in the groove [d]. PETG expands 68 x 10^-6 per K [a, S1]. A
   500 panel that goes from 20 to 45 C grows 500 x 68e-6 x 25 = 0.85. Both sides of a seam grow
   the same amount. A thin filler strip moves with them. A thick, stiff filler strip does not, and
   its edges crack or show.
4. Solvent left in the seam. Solvent cements and lacquer putties that are sealed in under primer
   can soften the primer later. Vivak warns that solvent pooling in a joint causes whitening and
   stress crazing [a, S1].

**What to do.**

- **Make the bond stiff first.** The inside flange, adhesive along the full length, and the
  screws carry the load. The brief already says filler is not for strength. A methacrylate with
  20 to 40 % elongation and a 3.2 gap limit fills uneven flange contact [a, S40].
- **Groove shape [d].** A V with an included angle of about 90 degrees, 1.0 to 1.5 deep and 2 to 3
  wide at the face. Stop the groove above the bond line, so that sanding cannot open the bond.
  Keep the filler under the Evercoat limit of 3 sanded thickness [a, S14]. Users report that a
  chamfer or V gives the filler or weld a place to go and gives a cleaner result [c, 3 reports,
  S25, S41].
- **Weld the groove with PETG (coupon decides).** Friction welding with filament in a rotary tool,
  a 3D pen, or a soldering iron with filler strip. Polymaker gives the friction-weld method: tool
  at 70 to 80 degrees, the weld "sits proud" and is ground flush [a, S42]. Users report it works
  well on PETG and makes one piece [c, 4 reports, S25, S27, S43]. A Georgia Tech lab measured
  friction welds at about the same tensile strength as super glue on printed parts (6.74 vs
  6.91 MPa), both far below a one-piece part (22.19 MPa) [b, S44, material not stated in the
  summary]. A weld is therefore for appearance and stiffness of the skin, not for the main load.
  A welded groove has no filler line of a different material. It needs only a skim of putty for
  pinholes.
- **Fill.** Polyester glazing putty that lists plastics (Metal Glaze or Poly-Flex). Firm pressure,
  thin coats, sand at P180 then P220 to P320 [a, S13, S14]. Use Poly-Flex if the coupon flex test
  cracks Metal Glaze.
- **Wait.** Polyester putty: final block sanding after at least 24 h (sand time is 20 to 30 min,
  but shrink goes on for hours [c, S35]). Filler primer: final sanding after at least 48 h [c,
  S34]. Colour: at least 7 days before the warm soak or assembly. Rust-Oleum gives "maximum
  adhesion" of its plastic primer after 5 to 7 days [a, S19c]; SEM says adhesion "improves with
  time" [a, S20]. Look at the seam under raking light after 1 and 2 weeks (section 4).
- **Place seams well.** Users hide seams in inside corners or in a designed groove [c, S41]. The
  brief puts seams away from the palm rest and joystick areas.

### 2.4 Adhesives for the structural bond, PETG to PETG

| Class | Example | Maker data on PETG or copolyester | Published test | Gap | Work time | Heat | Cost found | Grade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Structural methacrylate, general | Plexus MA300, MA310 | Spartech (PETG sheet maker) lists Plexus MA300 and MA310 for its copolyester [a]. ITW's own list: ABS, acrylic, PBT, PC, PVC, TPU; not PETG [a]. | None on printed PETG found | 0.25 to 3.2 (MA310) | MA300: 3 to 6 min. MA310: 15 to 18 min at 24 C, 8 to 9 min at 32 C. | Exotherm in large masses; keep within the gap limit [a] | MA310 50 ml cartridge USD 29 to 35 (2 retailers), plus a 50 ml 1:1 gun and mixers | [a] S2, S40, S45 |
| Plastic adhesive for polyolefins | 3M DP8010, DP8005 | Not listed. Made for PP, PE, TPO. DP8010 on ABS 1,250 psi (substrate failure), PC 760 psi (adhesive failure) [a]. | 3M tables | 0.13 to 0.5 bond line | DP8010: 8 min work, 10 min open. DP8005: 2.5 to 3 min. | DP8010 Tg 61 C; 1,000 psi at 49 C vs 1,800 at 23 C (aluminium). DP8005 Tg 33 C. | Not priced | [a] S46, S47 |
| Two-part epoxy | 3M DP100, Loctite E-series, slow hardware epoxies | Eastman and Spartech list 3M DP100 and Loctite Hysol E-05CL for copolyester [a] | Loctite on PET: epoxies 150 to 650 psi, CA over 2,000 psi [b]. On printed ASA, epoxy failed at the face at a quarter of the CA load [b]. | Good | DP100: fast. Slow epoxies: 30 to 45 min. | Varies | Not priced | [a] S2, S3; [b] S24, S48 |
| Solvent cement | Weld-On 3, 4, 16; SCIGRIP 16; 3D Gloop PET | Vivak and Spartech list Weld-On 3 and 4 [a]. Weld-On 16 TDS lists acrylic, styrene, butyrate, PVC, ABS, PC, not PETG [a]; a data-sheet aggregator says it bonds PETG [a, secondary]. | Vivak lap shear, one week: Weld-On 3 1,800 psi, Weld-On 4 2,100 psi, MEK 1,500 psi [b] | None. Needs close fit. Capillary flow about 6 [a]. | Weld-On 16: 5 to 6 min | Solvent bonds reduce impact strength at the edge [a]. Whitening, crazing [a]. | Not priced | [a] S1, S2, S49, S50; [c] S27, S51 (3 reports that 16 works on PETG) |
| Two-part polyurethane, clear | Weld-On 55, 58 | Weld-On 55 lists PETG; 58 lists PETG [a]. Eastman lists 55 and 58 for Spectar to itself [a]. | None found | Some | 55: 5 to 6 min | Isocyanate component likely (not checked); not sprayed | Not priced | [a] S3, S52 |
| Cyanoacrylate | Loctite 401, 406; medium or gel CA | Eastman, Spartech list CA [a]. Loctite on PET: 401 over 3,200 psi on smooth PET; roughening lowered CA strength; 770 primer effect "could not be determined" because PET broke first [b]. | Loctite tables [b] | Poor; gel to about 0.5 [c] | Seconds | "Poor peel strength", "Low temperature resistance" [a] | Low | [a] S24; [b] S24 |
| Polyurethane, foaming | Original Gorilla Glue | None | None | Foams | Long | Pushes parts apart [a, filament maker] | Low | [a] S9 |
| Urethane "plastic bonder" | J-B Weld PlasticBonder | "thermoplastics", no list | None | Fills | Sets 15 min | Unknown | Low | [a] S53 |

**Conclusions on adhesives.**

- The best-supported structural bond is a general MMA (Plexus MA300/MA310) or a solvent cement.
  Two PETG sheet makers recommend these classes by name [a]. The only numbers on PETG are the
  Vivak solvent-cement lap shears on sheet [b]. Nothing was found on printed PETG with an MMA.
- MA310 suits a 300 to 500 seam: 15 to 18 min work time [a]. A flange 10 wide with a 0.5 bond line
  uses about 2 ml per 400 of seam [d]. One 50 ml cartridge bonds several seams, after mixer waste.
- Solvent cements need a close fit; FDM flanges are not flat to the 0.1 level, and the cement does
  not fill gaps [a, S49]. They are fast (5 to 6 min). They are the second candidate, not the first.
- Printing settings change PETG lap-joint strength [b, S54, S55, abstracts only]. Test with the
  real flange, the real filament and the real orientation.
- Do not use DP8005 near the exhaust: Tg 33 C [a].

### 2.5 Primer and paint

**Primers on PETG.**

- Plastic primer (Rust-Oleum Specialty Plastic Primer): modified alkyd, acetone and aromatic
  solvents, lists PP, PS, PVC, fibreglass, vinyl; topcoat after 1 h; maximum adhesion after 5 to
  7 days [a, S19c]. PETG is not named. Acetone and aromatics are on the Vivak attack list [a, S1].
  Use it only if the coupon passes.
- 2K epoxy primer (SprayMax): amine activator, no isocyanate; substrates are metals, FRP,
  polyester surfaces and old paint, all "cleaned and sanded"; pot life about 3 days [a, S19b].
  It is a good seal over polyester putty. PETG adhesion: unknown. Eastman's guidance favours tough
  films on copolyester [a, S3].
- 1K filler primer: holds on bare PETG in user tests [c, S28, S32]. Sand wet at P400 to P600.
- Hobby primer surfacer (Mr. Surfacer, Mr. Primer Surfacer): Mr. Hobby asks for a primer surfacer
  on solvent-resistant materials [a, S22]. Use on small parts (bezel, speaker forms) if the coupon
  passes.

**Paint systems reported to work.** One user paints PETG with automotive acrylic (aerosol or
airbrush) over promoter and filler primer, and clears with 1K or 2K; the parts survive on boats
[c, S28]. Golden reports good adhesion of artist acrylics on PETG, also on a flexed bookmark
[a/b, S11]. Prop guides use filler primer, then aerosol acrylic or enamel [c, S30, S31]. All
three put colour over primer or test direct on bare PETG; none over a filler-free seam on a
large part.

**Clear coat without isocyanate.** One-part acrylic lacquer clear (Dupli-Color), hobby lacquer
clear (Mr. Super Clear), or water-based acrylic or polyurethane clear. HSE says "water-based"
does not mean isocyanate free [a, S56]; read the SDS of every 2K product. Dupli-Color enamels have
a recoat window: recoat within 1 to 2 h or wait 5 days, or the paint can wrinkle; lacquers have
no window [a, S21b].

**Cure times found.** Dupli-Color lacquer: touch 1 h, handle 3 h [a, S21b]. Rust-Oleum plastic
primer: maximum adhesion 5 to 7 days [a, S19c]. XTC-3D: tack free about 2 h, cure about 4 h [a,
S23]. Evercoat putty: sand 20 to 30 min [a, S13, S14].

**Warmth at 40 to 50 C.** The shell near the exhaust reaches 40 to 50 C at the surface (owner's
estimate). PETG softens at 62 to 71 C (HDT) [a, S7, S8]. Bondo body filler service range goes to
82 C [a, S16]. DP8010 loses about 45 % of its strength at 49 C [a, S46]; DP8005 is above its Tg [a,
S47]. No data was found for paint films at 50 C on PETG. Risks [d]: soft fresh paint can print
through or mark; trapped solvent can blister; a stiff filler and PETG expand differently. The
coupon warm soak (section 4) checks all three. The owner's earlier PETG case for the same board
runs warm and does not soften. That supports the PETG, not the coatings.

### 2.6 Print settings that reduce the finishing work

The sources here are few. Most rows are our reasoning [d], to be checked on the coupon prints.

| Setting | Proposal | Reason | Grade |
| --- | --- | --- | --- |
| Dry filament | Dry before every shell print | Wet PETG gives bubbles and voids; Bambu calls PETG "highly hygroscopic" | [a] S7, S57 |
| Layer height on curved show faces | 0.12 to 0.16 | Step height on a slope scales with layer height. Smaller steps need less filler primer. The brief's 0.16 to 0.20 is a starting point only. | [d] |
| Wall order | Inner then outer (Bambu default), or outer first where the face must be exact | Outer-first gives a truer outer face but weaker overhangs. Test on the coupon. | [d] |
| Seam position | Put the Z seam on the flange side, in an inside corner, or in the V-groove | Users hide the seam in a groove or an inside corner | [c] S41 |
| Textured PEI plate as a show face | Use it where a satin finish is acceptable and only primer goes on (rear door, bezel back) | The textured face is even and has no layer lines. Under gloss it still needs filler primer. No source tested paint over it. | [d] |
| Walls | Enough walls that P120 cannot reach infill at the seam | Prusa: sanding into infill needs extra filler | [a] S6 |
| Fan and temperature | Keep the profile that gives good layer bond; no change for finish | Weak layer bond gives a fuzzy, weak skin under sanding | [c] S58 |
| Ironing on flat top faces | Try on the deck top only | Fewer top lines to fill | [d] |
| Printing parameters vs bond strength | Print the coupon flange with the real settings | Papers show print parameters change PETG lap-joint strength | [b] S54, S55 |

### 2.7 Failures reported on PETG

| Failure | Cause given | Source | Grade |
| --- | --- | --- | --- |
| Paint or coating lifts at the PETG face (adhesion failure) | Degrease only, no abrasion; two-part industrial plastic paint; cross-cut class 3 | S10 | [b] |
| Body filler and filler primer crack along a seam after paint | The seam flexes; weld the inside first | S25 | [c] |
| Filler and filler primer crack within 24 h on several prints | Cause not known (cold was suspected) | S26, summary only | [c] |
| Sand marks show through primer later | Filler finished with P80; primer shrinks as it cures | S34, S35, S36 | [c] |
| Joint whitening and stress crazing at a solvent joint | Solvent pooled in the joint | S1 | [a] |
| PETG weakens after contact with uncured UV resin | Not known | S33, summary only | [c] |
| Glues that hold PLA fail on PETG; MEK does not soften the filament | Lower surface energy; solvent resistance | S9, S27 | [a], [c] |
| Hobby paint does not grip | Material resists the paint solvent; oil or release agent | S22 | [a] |
| Paint wrinkles or lifts on recoat | Enamel recoated inside its cure window | S21b | [a] |

---

## 3. What to avoid on PETG

| Avoid | Reason |
| --- | --- |
| Colour or clear direct on bare PETG | Poor grip of solvent paints on copolyester [a, S3, S22]; class 3 cross-cut on unsanded PETG [b, S10]. |
| Unsanded faces under any coating | All makers ask for a light sanding [a, S1, S3, S21]. |
| Acetone, MEK or lacquer thinner as a cleaner | On the Vivak attack list [a, S1]; risk of crazing at stressed areas. Use IPA. |
| Solvent smoothing (acetone vapour, methylene chloride) | Does not work with acetone on PETG; methylene chloride is a laboratory solvent (Prusa) [a, S4]; the brief excludes it. |
| Isocyanate 2K clear and 2K urethane filler primer at home | Occupational asthma; HSE asks for a booth and air-fed breathing apparatus [a, S56]; the brief excludes it. |
| 3M DP8005 near warm areas | Tg 33 C [a, S47]. |
| Thick body filler over the whole shell | Harder than PETG; ridges; cracks on flex [c, S25]; not made for thermoplastics [a, S16]. |
| Thick one-part spot putty | "Thick applications are subject to cracking" [a, S18]; shrinks as solvent leaves. |
| UV resin as a filler on PETG | User reports of weakened PETG [c, S33]; UV lamps attack PETG sheet in screen printing [a, S1]. |
| Original foaming polyurethane glue | Foams and pushes parts apart [a, S9]. |
| Force-curing coatings at 60 C or more on the shell | PETG HDT 62 to 71 C [a, S7, S8]. XTC-3D's 60 C cure is too close. |
| Flame treatment or flame polishing | For olefins only [a, S15]; can cause edge cracking [a, S1]; distortion risk. |
| Coarse final sanding of filler (P80) | Marks come back through primer [c, S34, S36]. |
| Enamel recoat inside its window | Wrinkles or lifts [a, S21b]. |
| Filler in a service joint or on threads and locators | The brief says so. Mask them. |

---

## 4. Coupon test plan

### 4.1 Coupon

- Shape: a curved two-piece part, 120 long, 4 mm skin, curvature like the shell side. Split it
  across the middle with the real inside flange, the real screws and the real groove.
- Material and print: the real PETG, the real profile, the real orientation of the shell piece it
  stands for. One coupon is printed with its outer face on the textured plate.
- Count: 4 coupons and 4 flat plaques. Print them all before the weekend.
- Mark each coupon and plaque with its code on the inside.

### 4.2 Matrix

Coupons test the bond and the seam. The filler and primer are the same on A to C, so only the
adhesive changes.

| Coupon | Bond | Groove | Filler | Primer | Colour and clear |
| --- | --- | --- | --- | --- | --- |
| A | Plexus MA310 | V, unwelded | Evercoat Metal Glaze | 2K epoxy primer, then 1K filler primer | 1K acrylic lacquer, 1K clear on half |
| B | Solvent cement (Weld-On 4 or SCIGRIP 16) | V, unwelded | Evercoat Metal Glaze | as A | as A |
| C | Slow two-part epoxy (30 min or more) | V, unwelded | Evercoat Metal Glaze | as A | as A |
| D | Plexus MA310 | V, friction-welded with the same PETG | Skim of Poly-Flex for pinholes | as A | as A |

Plaques (about 60 x 120, flat, from the real profile) test the primer on bare PETG. Each plaque
has two halves: one half scuffed P320 wet and IPA-wiped, one half IPA-wiped only.

| Plaque | First coat on PETG | Then |
| --- | --- | --- |
| P1 | 2K epoxy primer (SprayMax) | 1K lacquer colour |
| P2 | 1K filler primer (Dupli-Color or Rust-Oleum) | 1K lacquer colour |
| P3 | Plastic adhesion promoter (Dupli-Color), then 1K filler primer | 1K lacquer colour |
| P4 | Mr. Surfacer 1000 by airbrush (for the bezel and small parts) | Mr. Color or Tamiya LP |

Optional extra if time permits: a strip of XTC-3D on the back of plaque P2, and a strip of
Bondo body filler on the back of plaque P1, for the fingernail and knock tests only.

### 4.3 Weekend schedule

| Time | Work |
| --- | --- |
| Saturday 09:00 | Wash, IPA-wipe and scuff the flanges (P180). Bond A, B, C, D. Screws in. |
| Saturday 13:00 | Friction-weld D. Cut and clean grooves. Scuff the plaques. |
| Saturday 15:00 | Fill A, B, C (Metal Glaze) and D (Poly-Flex skim). |
| Sunday 09:00 | Block-sand the filler (P180, P240 wet). Prime coupons and P1 with 2K epoxy primer. Prime P2, P3, P4. |
| Sunday 15:00 | 1K filler primer on the coupons. |
| Tuesday or later (48 h) | Sand filler primer P400 to P600 wet. Colour. Clear on half of each coupon. |
| Colour + 7 days | Tests 1 to 4. |
| Colour + 7 and + 14 days | Test 5. |

### 4.4 Tests and pass criteria

| No. | Test | Method | Pass |
| --- | --- | --- | --- |
| 1 | Tape adhesion, cross-hatch | ASTM D3359 / ISO 2409 style. Six cuts each way through the film to the PETG, 2 apart for primer and paint; X-cut (two cuts at 30 to 45 degrees) where the build is thick, such as over the groove. Firm pressure with a strong tape, pull back fast at 180 degrees. Test on each plaque half and on each coupon next to the seam. | Scuffed halves: no squares removed, only small flakes at cut corners (ASTM 4B or better, ISO 0 to 1). X-cut: no lift along the cuts beyond 1. Any failure *at the PETG face* is a fail for that primer. |
| 2 | Flex across the seam | Support the coupon ends 100 apart, seam in the middle. Press the middle by hand or with a clamp to 2 deflection, 20 times. With t = 4 this is a surface strain of about 6 t d / L^2 = 6 x 4 x 2 / 100^2 = 0.5 % [d]. Look under raking light; repeat test 1 at the seam. | No crack line, no lift, no change of the seam under raking light. |
| 3 | Warm soak | 50 C for 24 h in a filament dryer or a box with a heater and a thermometer. Cool to room temperature. | No blister, no softening, no print of the dryer rack, no seam line. Tests 1 and 4 pass again after the soak. |
| 4 | Fingernail and knock | Scratch along the edge of the filler and across the seam with a fingernail. Tap along the seam with a coin; compare with a solid area. | No lift at a filler edge. No dull or hollow sound at the seam. |
| 5 | Seam look | Raking light from a low angle and a reflection of a straight edge in the gloss, at 1 and 2 weeks after colour, and after test 3. Photograph each time from the same place. | No seam or groove outline visible at 1 m. No change between the photographs. |
| 6 | Bond, destructive (after test 5) | Break coupons A to D across the bond by hand or in a vice. | Failure in the PETG (cohesive or substrate), not a clean peel at the adhesive face. |

**Decision rules.**

- Adhesive: choose the one with substrate or cohesive failure in test 6 and no seam change in
  tests 2, 3 and 5. If A and B both pass, choose A (gap filling).
- Groove: if D shows less seam change than A, weld all outer grooves.
- Primer: choose the first coat that passes test 1 on the scuffed half and after test 3. If the
  unscuffed half also passes, keep scuffing anyway.
- Filler: if Metal Glaze cracks in test 2, change to Poly-Flex and repeat test 2 on a new coupon.

---

## 5. Shopping list by class

| Class | Example | Status |
| --- | --- | --- |
| Wet-or-dry abrasive paper P120 to P600, sanding blocks (hard and soft), scuff pads | Any automotive brand | Certain |
| IPA (99 %), lint-free cloths, tack cloth, mild detergent | Any | Certain |
| Nitrile gloves, eye protection, respirator with organic-vapour cartridges and particle filters (A2P3 or equivalent) | Any | Certain |
| Masking tape for automotive paint | 3M or similar | Certain |
| Structural methacrylate, slow, 50 ml 1:1 cartridge, gun, static mixers | Plexus MA310 | Coupon must prove adhesion on printed PETG |
| Solvent cement for PETG and a needle bottle | Weld-On 4, SCIGRIP 16 | Coupon test only; check the SDS for methylene chloride |
| Slow two-part epoxy | Any 30 min or slower | Coupon test only (the data predict a weaker bond) |
| Polyester glazing putty that lists plastics, cream hardener | Evercoat Metal Glaze; Evercoat Poly-Flex | Coupon must prove adhesion and flex |
| Spare filament and a rotary tool collet for friction welding, or a 3D pen | Same PETG | Coupon decides whether to weld |
| 2K epoxy primer aerosol, isocyanate free | SprayMax 2K Epoxy Primer | Coupon must prove adhesion on PETG |
| 1K filler primer aerosol | Dupli-Color Filler Primer, Rust-Oleum Filler Primer | Likely; coupon confirms |
| One-part spot putty (over primer only) | Bondo Glazing & Spot Putty; Tamiya Putty Basic | Certain for pinholes in primer |
| Plastic adhesion promoter | Dupli-Color Adhesion Promoter | Coupon test only |
| Colour: 1K acrylic lacquer aerosol, or hobby lacquer for the airbrush | Dupli-Color lacquer; Mr. Color, Tamiya LP; Mr. Surfacer 1000 | Colour choice is open; coupon confirms the system |
| Clear: 1K acrylic lacquer or water-based clear | Dupli-Color 1K Clear; Mr. Super Clear; Mr. Hobby Premium Topcoat | Optional; coupon confirms |
| Filament dryer or a warm box with a thermometer | Existing dryer, if any | For the warm soak |

---

## 6. Safety notes

- Ventilate every step with solvents, aerosols or two-part products. Spray outdoors or in a spray
  booth with extraction. Follow each product's SDS.
- Polyester fillers and putties contain styrene monomer [a, S17] and a peroxide hardener. Use
  gloves and ventilation. Do not mix large puddles; mixed filler heats up.
- Methacrylate adhesives (MA310) have a strong odour and are flammable. Large masses get hot
  ("exothermic reaction") [a, S40]. Keep beads within the gap limit and mix only what is used.
- Isocyanates: do not spray isocyanate 2K products at home. HSE asks for a booth and air-fed
  breathing apparatus, and says filtering masks are not suitable [a, S56]. Read the SDS of every
  2K aerosol before purchase; "water-based" does not mean isocyanate free [a, S56].
- Methylene chloride (in some solvent cements and 3D Gloop-type products): the US EPA restricted
  it in 2024 [a, S59]. Prefer a DCM-free cement, use a needle bottle, and ventilate.
- Epoxy and amine hardeners sensitise skin. Use nitrile gloves.
- Sanding dust from fillers and primers: wet-sand where possible; wear a P2/P3 particle filter for
  dry sanding; vacuum, do not sweep.

---

## 7. Sources

### Sources read

| No. | URL | What it is |
| --- | --- | --- |
| S1 | https://static.treatstock.com/static/fxd/wikiMaterials/PETG/files/vivak-petg-fabrication-guide.pdf | Plaskolite Vivak PETG sheet fabrication guide: sanding, solvent bonding with lap-shear table, chemical resistance, properties. [a], [b] |
| S2 | https://spartech.com/media/documents/SPA221050-UltraTuf-Ultros-Copolyester-Guide.pdf | Spartech copolyester sheet guide: adhesive list (Weld-On, Plexus MA300/MA310, 3M DP100, Loctite). [a] |
| S3 | https://www.professionalplastics.com/professionalplastics/Spectar-Fabricating.pdf | Eastman Spectar copolyester fabrication guide: adhesives, preparation, spray painting. [a] |
| S4 | https://help.prusa3d.com/article/petg_2059 | Prusa knowledge base, PETG: sanding, dissolving. [a] |
| S5 | https://wiki.polymaker.com/printing-tips/post-processing/sanding | Polymaker wiki, sanding and fillers. [a] |
| S6 | https://blog.prusa3d.com/postprocessing-of-3d-prints-step-by-step_29270/ | Prusa blog: finishing a PETG helmet with body filler and filler primer. [a] |
| S7 | https://store.bblcdn.com/3a230e260a3a47c2b0db0156e07eef91.pdf | Bambu PETG HF data sheet (HDT values read from a retailer copy, S7b). [a] |
| S7b | https://www.smith3d.com/shop/materials/petg/bambu-lab-petg-hf-filament-1kg-1-75mm-fast-printing-petg-high-flow-rfid-durable-filament-low-warping-petg-ams-compatible/ | Retailer page that quotes the PETG HF data sheet values. [a, secondary] |
| S8 | https://store.bblcdn.com/s1/default/cb94589bf7994fdcbfa833badefae9cd/Bambu_PETG_Basic_Technical_Data_Sheet.pdf | Bambu PETG Basic data sheet: Vicat, HDT (search summary). [a] |
| S9 | https://sigmafilament.com/best-glue-for-pla-petg/ | Filament maker's glue guide for PLA and PETG. [a] |
| S10 | https://www.confer.cz/metal/2025/download/5141-study-of-mutual-adhesion-of-coating-system-and-polymer-materials-printed-by-fdm-3d-printing-technology.pdf | METAL 2025 paper: 2K plastic coating on printed PLA, PETG, ASA; ISO 4624 and ISO 2409. [b] |
| S11 | https://goldenartistcolors.com/resources/hand-painting-3d-prints-with-acrylics | Golden Artist Colors: acrylics and primers on PLA, PETG, ABS; cross-hatch. [a/b] |
| S12 | https://mok.scholasticahq.com/article/31753-comparing-the-efficacy-of-four-methods-of-preparing-3d-printed-polymer-surfaces-to-take-paint-and-their-effect-on-an-acrylic-paint-layer | Conservation paper on surface preparation of printed PLA and ABS for paint (abstract only). [b] |
| S13 | https://www.evercoat.com/wp-content/uploads/2024/04/TDS_100416_METAL-GLAZE-4.2024.pdf | Evercoat Metal Glaze data sheet: substrates, max thickness, topcoats. [a] |
| S14 | https://www.evercoat.com/wp-content/uploads/2022/08/TDS_100411_POLY_FLEX_GLAZING_PUTTY_2_2015_EN.pdf | Evercoat Poly-Flex data sheet: flexible and rigid plastics. [a] |
| S14b | https://www.evercoat.com/wp-content/uploads/2022/08/TDS_100425_METAL-GLAZE-ULTRA-10.2022-1.pdf | Evercoat Metal Glaze Ultra: thermoset plastics only. [a] |
| S15 | https://www.evercoat.com/wp-content/uploads/2023/05/TECH-TIP-Poly-Flex-Flame-Treatment.pdf | Evercoat tech tip: flame treatment for olefins. [a] |
| S16 | https://multimedia.3m.com/mws/media/2666792O/3m-bondo-234D-ultimate-easy-sanding-body-filler-tds-ceemea.pdf | 3M Bondo Ultimate body filler data sheet: substrates, service temperature. [a] |
| S17 | https://multimedia.3m.com/mws/media/761617O/3m-lightweight-body-filler-tds-05800-05801-05804.pdf | 3M lightweight body filler: polyester with styrene monomer (search summary). [a] |
| S18 | https://multimedia.3m.com/mws/media/2394072O/bondo-glazing-and-spot-putty.pdf | Bondo Glazing & Spot Putty data sheet. [a] |
| S19 | https://multimedia.3m.com/mws/mediawebserver?mwsId=SSSSSuUn_zu8lZNUM8tv48mxmv70k17zHvu9lxtD7SSSSSS-- | Bondo Glazing & Spot Putty SDS: composition (search summary; direct fetch refused). [a] |
| S19b | https://download.kwasny.com/datasheets/TMB-3680033_(US)EN.pdf | SprayMax 2K Epoxy Primer data sheet: amine activator, substrates, pot life. [a] |
| S19c | https://www.rustoleum.com/-/media/DigitalEncyclopedia/Documents/RustoleumUSA/TDS/English/CBG/Specialty/SPC-26_Specialty_Plastic_Primer_Spray_TDS_1.ashx | Rust-Oleum Specialty Plastic Primer data sheet (search summary). [a] |
| S20 | https://semproducts.com/public/content/techsheets/TDS_plastic_adhesion_promoter.pdf | SEM Plastic Adhesion Promoter data sheet: olefins only. [a] |
| S21 | https://www.duplicolor.com/en/products/primer/dupli-color-multi-purpose-filler-primer | Dupli-Color filler primer and adhesion promoter pages. [a] |
| S21b | https://www.duplicolor.com/en/faq | Dupli-Color FAQ (recoat window) and lacquer page. [a] |
| S22 | https://www.mr-hobby.com/en/qa | Mr. Hobby FAQ: paints dissolve polystyrene; primer surfacer on solvent-resistant materials. [a] |
| S23 | https://www.smooth-on.com/tb/files/XTC3D_TB.pdf | Smooth-On XTC-3D technical bulletin: PETG named, exotherm, cure. [a] |
| S24 | http://dm.henkel-dam.com/is/content/henkel/LT-2197_Plastic%20Guide_v6%20LRpdf | Loctite Design Guide for Bonding Plastics, vol. 6: PET table and method; CA properties. [a], [b] |
| S25 | https://www.reddit.com/r/3Dprinting/comments/og8ivn/ive_bondoed_and_sanded_this_seam_at_least_3_times/ | User thread: filled seam cracks after primer; replies on welding. [c] |
| S26 | https://www.reddit.com/r/3Dprinting/comments/ymbokl/what_is_causing_my_bondo_and_filler_primer_to/ | User thread: filler and primer crack (search summary). [c] |
| S27 | https://www.reddit.com/r/3Dprinting/comments/12qrfzv/just_to_let_yall_know_mek_does_not_melt_pteg/ | User thread: MEK, CA, friction welding, soldering iron on PETG. [c] |
| S28 | https://www.reddit.com/r/3Dprinting/comments/oopl90/painting_tips_for_petg/ | User thread: automotive paint on PETG with promoter and filler primer. [c] |
| S29 | https://www.reddit.com/r/3Dprinting/comments/8eeosn/best_way_to_fill_up_gaps_in_3d_printed_parts/ | User thread: Milliput on prints (search summary). [c] |
| S30 | https://propbuilds.com/blogs/news/how-to-finish-3d-printed-props | Prop guide: PETG fuzzes; wet sand; scuff before primer. [c] |
| S31 | https://www.forgely3d.com/blogs/news/best-filament-for-cosplay-pla-petg-tpu-guide | Prop shop guide: PETG sanding time vs PLA. [c] |
| S32 | http://lukethier.blogspot.com/2016/11/what-paints-stick-to-petg-and-cross.html | User cross-hatch test of two primers on unprepared PETG. [c] |
| S33 | https://www.reddit.com/r/3Dprinting/comments/12u7ovs/petg_and_uv_resin_interaction/ | User report: PETG weakened by uncured resin (search summary). [c] |
| S34 | http://www.spiuserforum.com/index.php?threads/scared-of-primer-shrinkage.6670/ | Car-paint forum: primer shrink mostly over in 2 days (search summary). [c] |
| S35 | https://www.spiuserforum.com/index.php?threads%2F2k-primer-shrinkage.5707%2F= | Car-paint forum: filler, glaze and primer shrink; finish at P180 to P220. [c] |
| S36 | https://www.bodyshopbusiness.com/proper-paint-prep-foundational-integrity/ | Trade article: sand-scratch swelling, flash time between primer coats. [c] |
| S37 | https://blog.equalle.com/posts/2026/02/20/how-long-to-wait-before-sanding-2k-primer-surfacer-primer-sanding/ | Abrasive maker's blog: wait before sanding surfacer; ghost scratches later. [c] |
| S38 | https://forum.finescale.com/t/can-i-use-acrylic-over-a-lacquer-primer/260605 | Model forum: Mr. Surfacer is acrylic in an acetone-rich solvent (search summary). [c] |
| S39 | https://www.hobbyco.com.au/products/putty-basic-type | Retailer description of Tamiya Putty Basic (search summary). [c] |
| S40 | https://itwperformancepolymers.com/wp-content/uploads/Plexus-MA310-TDS.pdf | Plexus MA310 data sheet: gap, elongation, work time by temperature, exotherm. [a] |
| S41 | https://www.reddit.com/r/3Dprinting/comments/x9z7k4/any_tipsideas_on_how_i_could_make_this_seam/ | User threads: V-groove for weld or filler; seams in inside corners (search summaries). [c] |
| S42 | https://polymaker.com/friction-welding/ | Polymaker friction welding guide. [a] |
| S43 | https://www.reddit.com/r/3Dprinting/comments/8uexok/joining_petg/ | User thread: friction welding PETG (search summary). [c] |
| S44 | https://matrixlab.gatech.edu/ramblin-reck-model/part-fusion/ | Georgia Tech MATRIX Lab: tensile tests of glued, friction-welded and melted joints. [b] |
| S45 | https://www.chemical-concepts.com/product/plexusr-ma310-adhesive-50-ml/ | Retailer: MA310 50 ml price and gun; also https://www.ellsworth.com/products/adhesives/acrylic/itw-performance-polymers-plexus-m310-methacrylate-adhesive-cream-50-ml-cartridge/ |
| S46 | https://multimedia.3m.com/mws/media/1235404O/dp8010-technical-data-sheet.pdf | 3M DP8010 data sheet: substrates, Tg, strength vs temperature, work life. [a] |
| S47 | https://multimedia.3m.com/mws/media/2365892O/3m-scotch-weld-structural-plastic-adhesive-dp8005-black.pdf | 3M DP8005 data sheet: work life, Tg (search summary). [a] |
| S48 | https://doi.org/10.1016/j.ijadhadh.2020.102602 | Yap et al. 2020: epoxy vs CA lap shear on printed ASA and nylon. [b] |
| S49 | https://assemblyadhesives.com/wp-content/uploads/2020/documentation/acrylics/ips_weld-on_4_TDS_0120.pdf | Weld-On 4 data sheet: capillary flow, crazing note. [a] |
| S50 | https://assemblyadhesives.com/TDS/ips_weld-on_16_TDS_1124.pdf | Weld-On 16 data sheet: substrate list, work time. [a]; aggregator: https://www.gluespec.com/Materials/adhesive/scigrip-weld-on/16 |
| S51 | https://www.reddit.com/r/3Dprinting/comments/14541jq/petg_glue_found_one_that_worked_ok_for_me/ | User reports: SCIGRIP 16 on PETG (search summaries; also threads 651ixr, zolqwl). [c] |
| S52 | https://assemblyadhesives.com/products/polycarbonate/weld-on-55/ | Weld-On 55 and 58 pages: PETG listed. [a] |
| S53 | https://www.jbweld.com/product/plastic-bonder-syringe | J-B Weld PlasticBonder page. [a] |
| S54 | https://www.sciencedirect.com/science/article/abs/pii/S2214785322031546 | Vamshinath 2022: print parameters vs PETG lap joints (abstract). [b] |
| S55 | https://doi.org/10.1016/j.tafmec.2021.103087 | Kanani et al. 2021: fracture of bonded printed PETG lap joints (abstract). [b] |
| S56 | https://www.hse.gov.uk/mvr/bodyshop/isocyanates.htm | HSE: 2-pack isocyanate paints; also https://www.hse.gov.uk/Pubns/indg473.pdf |
| S57 | https://wiki.bambulab.com/en/filament/petg | Bambu Lab wiki: PETG usage guide. [a] |
| S58 | https://www.reddit.com/r/FixMyPrint/comments/qetwhm/petg_layer_adhesion_is_bad/ | User thread: PETG temperature and cooling vs layer bond (search summary). [c] |
| S59 | https://www.epa.gov/assessing-and-managing-chemicals-under-tsca/risk-management-methylene-chloride | US EPA: methylene chloride risk management and 2024 rule. [a] |
| S60 | https://wiki.polymaker.com/printing-tips/post-processing/glueing | Polymaker wiki, glueing: PET Gloop, Devcon Plastic Welder. [a] |

Note on S60: Polymaker calls Devcon Plastic Welder "a two-part epoxy". Devcon sells Plastic
Welder as a methacrylate; Eastman lists "Plastic Welder II" for Spectar [a, S3]. The class was
not checked further.

### Sources that were not accessible or read only in part

| Source | Result |
| --- | --- |
| Reddit threads ymbokl, 1of7u1r, zolqwl, 12u7ovs | Page fetch timed out. Search-result summary only. |
| https://www.youtube.com/watch?v=Y8XrdfqtMjY ("Top PETG Adhesives Tested") | No description or transcript returned. Not used. |
| MoK paper S12 | Abstract only. Method and polymers not read. |
| Plexus MA300 and MA310 strength-vs-temperature graph | A graph in the PDF; values not extracted. Read it from S40 before the bond is fixed. |
| Bondo spot putty SDS (direct link) | HTTP 403. A second 3M SDS link gave the composition in a search summary. |
| Papers S54, S55 | Behind a paywall. Abstracts only; the adhesive in S55 was not named in the summary. |
| Facebook group post on PETG primers | Log-in wall. Not opened. |
