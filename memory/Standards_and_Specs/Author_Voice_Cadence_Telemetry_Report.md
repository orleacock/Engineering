---
title: "Deep Author Voice, Tone & Cadence Telemetry Report (Pass 2)"
entity: "Alchemical-3D"
compartment: "private"
last_synced: "2026-11-06"
---

# 📊 Deep Author Voice, Tone & Cadence Telemetry Report (Pass 2)

- **Corpus Inbox**: `/home/orin/Projects/Alchemical3D/Homunculus/addons/author-voice-cadence/corpus_inbox`
- **Active Domain Scope**: `maker` *(includes Alchemical-3D Blog/R&D, Maker Suppliers/Webstore Companies, and Open-Source Printer/Firmware Orgs; excludes gaming servers, private DMs, and internal business/admin channels)*
- **Qualifying Threshold**: `>= 60` prose words per post (after chronological stitching & code/URL stripping)
- **Total Qualifying Maker Posts**: `2,947` posts (`315,076` prose words)
  - **Sub-Register 1 — Alchemical-3D Blog & Announcements (`Tier 1A`)**: `340` posts (`57,813` words)
  - **Sub-Register 2 — Alchemical-3D R&D & Subsystem Engineering (`Tier 1B`)**: `755` posts (`77,972` words)
  - **Sub-Register 3 — Maker Suppliers, Companies & Open-Source Orgs (`Tier 2A + 2B`)**: `1,852` posts (`179,291` words)

---

## 0. Maker Orgs, Supplier Companies & Domain Filtering Breakdown

### 0.1 Domain Tier Summary

| Ecosystem Tier | Status | Channels | Raw Messages | Stitched Posts | Raw Words |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Tier 1A: Alchemical-3D Blog & Announcements (`2.4x`) | ✅ Included | `5` | `877` | `649` | `66,836` |
| Tier 1B: Alchemical-3D R&D & Subsystem Engineering (`1.55x`) | ✅ Included | `22` | `18,011` | `16,355` | `340,675` |
| Tier 2A: Maker Suppliers & Hardware Webstore Companies (`1.15x`) | ✅ Included | `82` | `24,654` | `23,349` | `440,922` |
| Tier 2B: Open-Source Hardware/Firmware Orgs & Maker Channels (`1.0x`) | ✅ Included | `75` | `30,351` | `27,829` | `556,670` |
| Tier 3: General Linux / Sysadmin Communities | 🚫 Excluded | `12` | `5,149` | `4,789` | `100,942` |
| Filtered Out: Gaming Clans & Casual Social Servers | 🚫 Excluded | `207` | `25,775` | `23,842` | `414,538` |
| Filtered Out: Private DMs, Group DMs & Internal Admin/Business | 🚫 Excluded | `657` | `136,688` | `126,978` | `1,819,665` |

### 0.2 Included Maker Orgs, Hardware Suppliers & Project Communities

| Organization / Company | Ecosystem Role | Channels | Raw Msgs | Long Posts (`>=60w`) | Long-Form Words | Total Raw Words |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Alchemical 3D** | Primary Maker Org (Blog, R&D & Community) | `39` | `31,309` | `1,581` | `182,171` | `634,533` |
| **Fabreeko** | Maker Supplier / Webstore Company | `38` | `17,107` | `507` | `47,660` | `306,430` |
| **VORONDesign** | Open-Source Hardware / Firmware Org | `31` | `5,816` | `336` | `32,633` | `121,532` |
| **Kore Gaming** | Dedicated #3d-printing Channel (Mixed Server) | `1` | `10,517` | `224` | `22,781` | `167,400` |
| **West3D Printing** | Maker Supplier / Webstore Company | `8` | `5,494` | `116` | `11,292` | `93,244` |
| **KB-3D** | Maker Supplier / Webstore Company | `8` | `1,069` | `80` | `7,567` | `24,435` |
| **ANNEX Engineering** | Open-Source Hardware / Firmware Org | `6` | `512` | `35` | `3,708` | `11,362` |
| **3D Printscape** | Open-Source Hardware / Firmware Org | `11` | `983` | `36` | `3,488` | `20,817` |
| **prusa3d** | Open-Source Hardware / Firmware Org | `6` | `291` | `27` | `3,139` | `7,408` |
| **Monolith** | Open-Source Hardware / Firmware Org | `2` | `173` | `11` | `1,158` | `4,114` |
| **Advanced3dPrinting** | Maker Supplier / Webstore Company | `6` | `239` | `10` | `914` | `4,714` |
| **klipper** | Open-Source Hardware / Firmware Org | `3` | `16` | `6` | `796` | `941` |
| **HevORT** | Open-Source Hardware / Firmware Org | `1` | `96` | `5` | `728` | `2,451` |
| **LDO Motors** | Maker Supplier / Webstore Company | `3` | `81` | `6` | `488` | `1,850` |
| **Kalico** | Open-Source Hardware / Firmware Org | `3` | `24` | `3` | `216` | `860` |
| **Nevermore Activated Carbon Filters** | Open-Source Hardware / Firmware Org | `1` | `65` | `1` | `161` | `1,008` |
| **3D-Fuel** | Maker Supplier / Webstore Company | `3` | `22` | `1` | `114` | `447` |
| **Rack Robotics** | Open-Source Hardware / Firmware Org | `1` | `5` | `1` | `68` | `146` |
| **Zero G** | Open-Source Hardware / Firmware Org | `4` | `5` | `1` | `67` | `168` |
| **Mr.Sanchez & Tyson Server** | Dedicated #3d-printing Channel (Mixed Server) | `1` | `25` | `0` | `0` | `430` |
| **3DO Community** | Maker Supplier / Webstore Company | `1` | `23` | `0` | `0` | `422` |
| **Bondtech** | Maker Supplier / Webstore Company | `2` | `12` | `0` | `0` | `212` |
| **Armchair Heavy Industries** | Open-Source Hardware / Firmware Org | `1` | `4` | `0` | `0` | `78` |
| **X.R. Bunker LLC** | Maker Supplier / Webstore Company | `2` | `3` | `0` | `0` | `63` |
| **Fluidd** | Open-Source Hardware / Firmware Org | `1` | `1` | `0` | `0` | `20` |
| **mammoth-3D** | Maker Supplier / Webstore Company | `1` | `1` | `0` | `0` | `18` |

---

## 1. Multi-Scale Sentence Cadence & Burstiness Across Sub-Registers

### 1.1 Core Length & Beat-to-Beat Variation

| Metric | Alchemical Blog (`1A`) | Alchemical R&D (`1B`) | Suppliers & Orgs (`2A+2B`) | All Maker Combined |
| :--- | :---: | :---: | :---: | :---: |
| **Mean Sentence Length** | `19.8` w | `24.1` w | `20.7` w | `21.3` w |
| **Median Sentence Length** | `19.0` w | `23.0` w | `19.0` w | `20.0` w |
| **Core Working Band (IQR 25–75%)** | `13–26` w | `15–32` w | `12–27` w | `13–28` w |
| **10th–90th Percentile Range** | `8–33` w | `10–40` w | `8–36` w | `8–36` w |
| **Sentence Length Std Dev** | `10.0` w | `12.1` w | `11.0` w | `11.2` w |
| **Beat-to-Beat Swing (`|S_i+1 - S_i|`)** | `9.5` w | `11.1` w | `9.8` w | `10.0` w |
| **3+ Sent Paragraph Arc (1st -> Mid -> Last)** | `19.6 -> 20.3 -> 19.8` w | — | — | `19.2 -> 18.0 -> 17.8` w |

### 1.2 Five-Band Sentence Length Distribution (`%` of Sentences)

| Sentence Length Band | Functional Role in Cadence | Blog (`1A`) | R&D (`1B`) | Suppliers/Orgs (`2A+2B`) | All Maker |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Punchy Beats (`3–9` words)** | Brisk openers, verdicts, dry kickers | `14.1%` | `9.9%` | `13.9%` | `13.0%` |
| **Crisp Declaratives (`10–17` words)** | Direct actions & status statements | `30.9%` | `22.7%` | `30.3%` | `28.8%` |
| **Core Cadence (`18–27` words)** | Primary clause-linked explanations | `35.3%` | `32.3%` | `31.9%` | `32.7%` |
| **Deep Causal (`28–39` words)** | Multi-clause physics / trade-off chains | `15.8%` | `24.8%` | `17.7%` | `18.9%` |
| **Extended Walkthroughs (`40+` words)** | Unbroken conversational chains | `4.0%` | `10.3%` | `6.2%` | `6.6%` |

---

## 2. Paragraph Chunking & Multi-Paragraph Discourse Structure

### 2.1 Sentences per Paragraph Distribution

| Paragraph Size | Blog (`1A`) | R&D (`1B`) | Suppliers/Orgs (`2A+2B`) | All Maker |
| :--- | :---: | :---: | :---: | :---: |
| **1-Sentence Punch / Callout Block** | `32.0%` | `56.8%` | `44.5%` | `45.8%` |
| **2-Sentence Pair (Setup + Payoff)** | `25.0%` | `26.2%` | `30.2%` | `28.3%` |
| **3-Sentence Core Block** | `20.7%` | `11.2%` | `15.1%` | `14.9%` |
| **4-Sentence Block** | `10.8%` | `3.4%` | `6.2%` | `6.2%` |
| **5+ Sentence Dense Block** | `11.4%` | `2.5%` | `4.1%` | `4.8%` |

### 2.2 Post Opening & Closing Rhetorical Moves (Blog `1A` vs. All Maker)

**How Posts Open (Paragraph 1):**
- **Direct Technical Premise / Action Statement**: Blog `87.1%` (`296`) | All Maker `88.9%` (`2621`)
- **Problem / Frustration Catalyst ('I didn't like how...', 'Right now X is struggling...')**: Blog `2.4%` (`8`) | All Maker `5.0%` (`147`)
- **Rhetorical / Framing Question ('Why put it up top...?', 'How are we going to...?')**: Blog `0.3%` (`1`) | All Maker `3.8%` (`112`)
- **Progress / Bench Status Hook ('Just an update...', 'Today was spent...')**: Blog `8.5%` (`29`) | All Maker `1.6%` (`48`)
- **Visual-First Walkthrough ('As you can see...', 'In this image...')**: Blog `1.8%` (`6`) | All Maker `0.6%` (`19`)

**How Posts Close (Final Paragraph):**
- **Practical Engineering Verdict / Takeaway**: Blog `70.9%` (`241`) | All Maker `86.7%` (`2554`)
- **Wry Parenthetical or Trailing Ellipsis Kicker**: Blog `8.2%` (`28`) | All Maker `4.6%` (`137`)
- **Forward Roadmap Teaser ('Keep an eye out...', 'more will come on that...')**: Blog `15.9%` (`54`) | All Maker `4.3%` (`128`)
- **Conversational Tag / Check Question ('...doesn't it?')**: Blog `1.2%` (`4`) | All Maker `2.2%` (`65`)
- **Community Feedback Invite / Sign-Off**: Blog `3.8%` (`13`) | All Maker `2.1%` (`63`)

---

## 3. Clause-Linking Architecture & Causal Connectors (per 1,000 Words)

### 3.1 Internal Comma-Pivots & Signature `'though'` Placement

| Syntactic Connector | Blog (`1A`) `/1k` | R&D (`1B`) `/1k` | Suppliers/Orgs `/1k` | Total Maker Count |
| :--- | :---: | :---: | :---: | :---: |
| `, which` | `0.59` | `0.64` | `0.90` | `245` |
| `, while` | `0.54` | `0.23` | `0.13` | `72` |
| `, so` | `1.30` | `1.92` | `1.97` | `578` |
| `, as` | `1.40` | `0.80` | `0.86` | `298` |
| `, since` | `0.14` | `0.45` | `0.23` | `84` |
| `, especially` | `0.10` | `0.12` | `0.21` | `53` |
| `, however` | `0.24` | `0.23` | `0.26` | `78` |
| `, meaning / allowing` | `0.09` | `0.09` | `0.11` | `31` |
| `clause-final 'though'` | `1.31` | `1.36` | `1.87` | `518` |
| `mid-clause 'though'` | `0.76` | `1.28` | `1.23` | `364` |

### 3.2 Physical / Engineering Cause-and-Effect Connectors

| Causal / Functional Connector | Blog (`1A`) `/1k` | R&D (`1B`) `/1k` | Suppliers/Orgs `/1k` | Total Maker Count |
| :--- | :---: | :---: | :---: | :---: |
| `because` | `0.28` | `0.82` | `0.91` | `244` |
| `since (causal/temporal)` | `0.80` | `1.27` | `0.91` | `309` |
| `due to` | `0.74` | `0.73` | `0.70` | `226` |
| `instead of / instead` | `0.69` | `0.72` | `0.52` | `189` |
| `allow(s) / allowing` | `0.86` | `0.64` | `0.30` | `153` |
| `enable(s) / enabling` | `0.19` | `0.05` | `0.07` | `27` |
| `this/which means` | `0.40` | `0.23` | `0.19` | `75` |
| `in order to` | `0.09` | `0.05` | `0.03` | `15` |
| `thus / therefore` | `0.09` | `0.12` | `0.07` | `27` |

---

## 4. Persona Balance, Conviction Boosters & Engineering Candor

### 4.1 Voice Persona Pronouns (per 1,000 Words)

| Persona Stance | Blog (`1A`) `/1k` | R&D (`1B`) `/1k` | Suppliers/Orgs `/1k` | Role in Author Voice |
| :--- | :---: | :---: | :---: | :--- |
| **1st-Person Builder (`I / my / me`)** | `16.8` | `30.9` | `37.5` | Hands-on bench testing, CAD decisions & personal experience |
| **1st-Person Org (`we / our / us`)** | `12.5` | `15.7` | `5.4` | Alchemical-3D project direction, release roadmap & shared effort |
| **2nd-Person Maker (`you / your`)** | `13.0` | `11.4` | `12.9` | Direct shop-floor coaching, assembly cues & reader walkthroughs |

### 4.2 Top Conviction Boosters vs. Pragmatic Engineering Hedges

- **Top Conviction / Emphasis Words**: `really` (876), `very` (575), `pretty` (258), `always` (186), `super` (176), `never` (162), `quite` (155), `definitely` (142), `completely` (101), `greatly` (84), `tons` (77), `obviously` (65), `absolutely` (58), `literally` (57)
- **Top Pragmatic Candor / Qualifier Words**: `probably` (230), `basically` (169), `likely` (120), `honestly` (119), `personally` (79), `mostly` (73), `currently` (67), `unfortunately` (61), `technically` (52), `hopefully` (43), `essentially` (43), `originally` (34), `potentially` (25), `apparently` (17)
- **Top Single-Word ALL-CAPS Emphasis Tokens**: `NOT` (23), `THE` (9), `SMD` (8), `AIO` (8), `UHF` (8), `YOU` (7), `ANY` (7), `ADXL` (7), `MUST` (7), `NOTE` (7), `WILL` (6), `FDE` (6), `PIP` (6), `THIS` (6), `ESP` (6)

---

## 5. Head-to-Head Contraction Habits & Punctuation Profile

### 5.1 Uncontracted vs. Contracted Habits (All Maker Corpus)

| Expression Pair | Uncontracted Count | Contracted Count | Uncontracted Share (`%`) | Stylistic Takeaway |
| :--- | :---: | :---: | :---: | :--- |
| **do not vs. don't** | `385` | `285` | `57.5%` | Balanced natural mix |
| **does not vs. doesn't** | `72` | `140` | `34.0%` | Prefers conversational contraction |
| **cannot/can not vs. can't** | `191` | `5` | `97.4%` | Prefers full uncontracted form for deliberate emphasis |
| **will not vs. won't** | `130` | `119` | `52.2%` | Balanced natural mix |
| **is not vs. isn't** | `143` | `97` | `59.6%` | Balanced natural mix |
| **are not vs. aren't** | `68` | `57` | `54.4%` | Balanced natural mix |
| **I am vs. I'm** | `786` | `70` | `91.8%` | Prefers full uncontracted form for deliberate emphasis |
| **I have vs. I've** | `756` | `85` | `89.9%` | Prefers full uncontracted form for deliberate emphasis |
| **I will vs. I'll** | `437` | `18` | `96.0%` | Prefers full uncontracted form for deliberate emphasis |
| **it is vs. it's** | `124` | `475` | `20.7%` | Prefers conversational contraction |

### 5.2 Punctuation & Emphasis Density (per 1,000 Words)

| Feature | Blog (`1A`) `/1k` | R&D (`1B`) `/1k` | Suppliers/Orgs `/1k` | All Maker Count |
| :--- | :---: | :---: | :---: | :---: |
| Conversational Contractions (`it's`, `don't`, `I've`) | `3.86` | `1.78` | `4.52` | `1,172` |
| Dramatic / Trailing Ellipses (`...`) | `3.08` | `0.24` | `0.94` | `366` |
| Parenthetical Asides `(...)` | `1.94` | `1.62` | `1.46` | `499` |
| Em-Dashes / Spaced Pivots (`—` / ` - `) | `3.53` | `0.49` | `0.17` | `273` |
| ALL-CAPS Emphasis Words (`NEVER`, `GREATLY`, `ONE`) | `2.61` | `2.10` | `1.81` | `639` |
| Markdown Bold Spans (`**...**`) | `0.76` | `0.00` | `0.02` | `47` |
| Markdown Italic Spans (`*...*`) | `0.10` | `0.00` | `0.02` | `10` |
| Explanatory Colons (`:`) | `0.66` | `0.26` | `0.64` | `173` |
| Semicolons (`;`) | `0.16` | `0.04` | `0.04` | `20` |
| Rhetorical / Direct Questions (`?`) | `0.66` | `1.92` | `1.43` | `445` |
| Exclamation Marks (`!`) | `8.54` | `0.81` | `1.32` | `793` |
| Raw Double-Space After Sentence End (`.  `) | `29.41` | `16.84` | `23.43` | `7,214` |

---

## 6. Empirical Anti-AI Lexicon Audit & Authentic Author Idioms

### 6.1 Generic LLM Cliché Count Across `315k+` Author Maker Words

- **`use / uses / using / used` vs. `utilize / utilizing`**: **`1,326`** vs. **`14`**
- **`delve / delving`**: `0` occurrences
- **`tapestry`**: `0` occurrences
- **`seamlessly`**: `0` occurrences
- **`testament to`**: `0` occurrences
- **`meticulously`**: `4` occurrences
- **`furthermore`**: `1` occurrences
- **`moreover`**: `0` occurrences
- **`in conclusion / in summary`**: `0` occurrences
- **`game-changer / revolutionary`**: `3` occurrences
- **`elevate (non-Z-axis)`**: `6` occurrences
- **`holistic / synergy`**: `1` occurrences
- **`it is important to note`**: `0` occurrences

### 6.2 Authentic Recurring Author Phrases & Idioms

| Signature Phrase / Collocation | Total Maker Occurrences | Rate (`/10k` words) |
| :--- | :---: | :---: |
| **keep in mind (though)** | `82` | `2.60` |
| **play(ing) with (prototyping)** | `78` | `2.48` |
| **make sure (instructional)** | `78` | `2.48` |
| **for the time being / for now** | `65` | `2.06` |
| **this is why** | `60` | `1.90` |
| **in the mean time / meantime** | `49` | `1.56` |
| **at some point** | `44` | `1.40` |
| **as you can see** | `42` | `1.33` |
| **more (will come / to come)** | `19` | `0.60` |
| **be sure to** | `17` | `0.54` |
| **in regards to** | `12` | `0.38` |
| **down the road** | `10` | `0.32` |
| **at the cost of** | `8` | `0.25` |
| **on the fly** | `5` | `0.16` |
| **every little bit (helps)** | `2` | `0.06` |
| **in my testing / experience** | `2` | `0.06` |
| **out of the box** | `1` | `0.03` |
| **needless to say** | `1` | `0.03` |

---

## 7. Stratified Candidate Verbatim Exemplars (Across All 5 Categories)

### 7.1 Category 1: Project Introductions, Hooks & Design Philosophy (Mode A)

#### Candidate 1 — `Alchemical 3D / #🗞printer-design-blog (2022-08-02)` (`118` words, score `26.4`)
> Today was spent mostly assisting people with minor issues and creating template parts for the build in OnShape, as well as collecting drawings from various open source projects to save me time.   Specifically things like the motherboards, power supplies, fans etc.  While this does not add up to much of an exciting update for the printer project, the amount of time this will save across the project is enormous.   As stated its not much of an update but in this image you will see the system coming together to form the 3 point Z axis.   We have a very special system planned for this axis and cannot wait to show it off as the design comes together though!

#### Candidate 2 — `Alchemical 3D / #🗞printer-design-blog (2022-10-16)` (`100` words, score `21.1`)
> As many of you know from other discussions, a major renovation to the air filtration system is underway.   We wanted to make this entire system simpler, reclaim sub deck space for expansion electronics, as well as make servicing even more simple, event further increasing total performance.   I just wanted to stop in here and share some of the progress here.   This is the new carbon filtration carriage that drops into the system.   It removes all of the headache of changing your carbon and GREATLY increases total throughput of the system.   Keep an eye out for major updates to the model!

#### Candidate 3 — `Alchemical 3D / #🗞printer-design-blog (2025-04-22)` (`85` words, score `21.1`)
> I didn't like how chunky all the various camera mounting options looked, wanted something very low profile, almost streamlined into the system where cables would be near invisible.    This is just a quick initial concept for the design.   Going to print it out real quick to test and see if it needs improvement.   Trying to keep everything as simple as possible, if it works out, I will just need to make a second small mount for the 3DO camera board somewhere else in the system.

#### Candidate 4 — `Alchemical 3D / #light-sensor-questions (2022-08-12)` (`86` words, score `17.1`)
> I was about to begin development of a toolhead for my printer and have postponed this until the sensing project is further along, will be working on other parts of the system for now and delay as long as possible.   This will allow people to build the system and use other toolheads until we can put something out in regards to this, and include its assembly in mine.  Its likely, I will end up having to finish my toolhead then rework it later for the project

#### Candidate 5 — `Alchemical 3D / #🗞printer-design-blog (2022-08-03)` (`114` words, score `15.8`)
> I just wanted to also step in here today and talk about goals for this project a bit.  As was mentioned previously there are many features this printer will include which are not going to be talked about until later in the project.  This is to provide us sufficient time to finish design and implementation prior to identifying what that feature truly is.   That being said, you may see some of these features during the periodic updates here.   In many cases though, it may not even be discussed as to what that part does or why even if imaged in updates here, you might just happen to catch a glance of it is all.

#### Candidate 6 — `Alchemical 3D / #🗞printer-design-blog (2022-08-08)` (`109` words, score `15.8`)
> Been very very busy working on the printer when its possible to find time over weekend.   I am still refining the air system after finding a few issues with the design.  Mainly realizing it was uglier than sin at first!   It just finished another pass of tweaks and updates.  The new format means I need to do a touch of rework on the Z transmissions, but this is fine as I kinda wanted to make them nicer anyhow, and support larger steppers if someone is crazy enough to put a solid steel bed on or something, they can use 48mm steppers instead of 42mm like the rest of us.

### 7.2 Category 2: Physical / Mechanical / Thermal 'Why' (Modes A & B)

#### Candidate 1 — `Alchemical 3D / #🗞printer-design-blog (2022-08-04)` (`115` words, score `23.0`)
> Just to revisit the core functionality of this a moment, you can see how the tube will extend through a linear rod bearing and clamp.   This will allow the bed to rotate on each of its support axis for leveling, and also passively allow the system to relieve stress that thermal expansion creates in the Z-axis bed platform, something many printers do not do at all.  The mounting bracket at the carriage will obviously be seeing revisions to incorporate the belt drive, but the bed side of each support will remain as is currently, only receiving minor tweaks and a major cosmetic pass, it looks pretty plain right now in the concept stage doesn't it?

#### Candidate 2 — `Alchemical 3D / #🗞printer-design-blog (2022-08-10)` (`82` words, score `23.0`)
> I present you one of the early prototypes of this system.   You slide the bearing into the housing then use a screw in a side hole to secure it.   This is a little different than what your likely envisioning as it instead uses the screw like teeth instead of a pressure point.    
> The need is here to debate using normal screws and leave the heads visible, or to use grub screws buried in the part itself, thus hiding it completely from sight.

#### Candidate 3 — `Alchemical 3D / #🗞printer-design-blog (2023-04-09)` (`80` words, score `23.0`)
> This is a little project I've been working on for the printer.  In many locations, instead of using traditional screws, it will instead incorporate a small 5mm rod that either snaps into place, or otherwise sandwiches between parts to secure pulleys.  This allows me to reduce the number of heat sets and bolts required, while also greatly reducing the number of exposed screw heads.   This one here for example is one style being tested to hold the AB belt pulley.

#### Candidate 4 — `Alchemical 3D / #🗞printer-design-blog (2023-08-31)` (`95` words, score `23.0`)
> This is really good news though, as it means we can change engineering attention to the moisture removal from chamber.  A subject I personally have wanted to spend more time with.  Right now, our materials doing this job are so overly absorbant, its struggling to get the water to the evaporation field and just holding onto it all insid the chamber!  This is a huge issue as the same water it moved, just re-evaporates into the chamber eventually while Retort is turned off.  Needless to say, this is an unacceptable result that must be addressed.

#### Candidate 5 — `Alchemical 3D / #🗞printer-design-blog (2024-11-17)` (`81` words, score `23.0`)
> The parts will clamp the rods at the rear, very close to the linear assembly.   The rods will carry the linear bearings and hand off support to a GE5C bearing assembly for flexibility.   This will preserve the flexibility of the system avoiding accidental part strain, while also preserving its ability to combat thermal expansion and resonance.   This also enabled the system to easily switch between a 4 point, or 3 point bed, more will come on that in the future though.

#### Candidate 6 — `Alchemical 3D / #🖨printer-design-discussion (2022-10-25)` (`91` words, score `18.6`)
> These bumpers serve two major purposes, one is part of our greater engineering philosophy of resonance compensation, and the other is to negate thermal expansion issues of having multiple metals fixed on the same plain.  While there are various solutions out there for this on misc printers, nobody has really designed a system that automatically compensates for this, ours does.    Additionally, the mounts for our bed ride upon 45mm LM8U bearings and 8MM rods, this completely negates all thermal expansion and assists in general motion compensation using an auto-centering motion philosophy.

### 7.3 Category 3: Hands-On Build, Calibration & Troubleshooting Guidance (Mode B)

#### Candidate 1 — `Alchemical 3D / #🗞printer-design-blog (2022-08-05)` (`131` words, score `97.2`)
> The next thing you see mentioned often online is when people get a linear rail, the immediately replace the bearings and it "slides so much better now".  You see people recommend this as well often, and its not good...  First, you should **NEVER** need to replace your bearings on a product out of the box, if you do, **stop buying from them**.   Next, linear rails are precision pieces of hardware, the factory hand matches the carriages to the rials and bearings, changing this more often than not can actually ruin your rails ability to produce quality movement.  I can only imagine how many rails out there came to the buyer perfectly fine, but the bearings were swapped because they were told to do it and misguided by the loose rail concept.

#### Candidate 2 — `Alchemical 3D / #🗞printer-design-blog (2022-08-14)` (`145` words, score `70.8`)
> Why put it up top with excessive screws and extra work when you want to tension a belt, when you can place the entire assembly under the printers deck?  Not only place it under the deck... But provide a single screw visible from the top of the chamber to easily adjust the tension without flipping your printer over.  The entire system will be adjusted from an easy access screw on the bed, stick your allen wrench in and torque until satisfied with your tension.  We might even give this tension block its own knob so you have tool-less adjustments.  The best part about this system though, your going to be able to put a piece of silicone tube on that screw going through the bed, so whether you use a regular screw, or maybe a knob for tool-less operation, it will never ever go anywhere!

#### Candidate 3 — `Alchemical 3D / #🗞printer-design-blog (2022-08-27)` (`250` words, score `54.2`)
> As you probably are now wondering, how are we going to tension XY if both pulleys in front are fixed idlers?  The latest revision of the pre-alpha printer XY gantry will be using a system on the rear of the chamber to tension the belts.   This has quite a few benefits but unfortunately means you have to reach a bit further in to adjust the system.   However, due to the mechanical advantages we are providing the system with this, the likelihood these need to be adjusted over time is greatly reduced.    Its hard to describe in text how this mechanical system has been derived, but the closest way if you can imagine is a mix between an extruder tension system and a screw based gear meshing retainer.  Like most systems, you will just turn a screw to increase tension, however this one provides a greater mechanical advantage to afford longer term retention and better aesthetics (when done that is).   Originally a concept similar to this was planned in the system, but we moved away from it in favor of the front pulley tension, since things have again been modified, we wanted to go back to the original plan.  This also allows us to keep the theme of adjustments being located near each respective stepper for each respective axis.  While the system is not added in these photos either, work has begun on the resonance isolation subsystems for these steppers, you will likely see this implemented in the next major update.

#### Candidate 4 — `Alchemical 3D / #🗞printer-design-blog (2022-08-17)` (`95` words, score `49.0`)
> For me, my favorite part of this system will be the ability to adjust it on the fly, literally all aspects of general tuning will be right there for access.  If you want to tune any belt in this system, its in an obvious and easy spot, no more rooting around blind corners to get to an adjustment, just a simple plain allen wrench and an obvious screw facing you.   When you have a full printer assembled and you need to get to a tension screw, it can be hell, but not with this one!

#### Candidate 5 — `VORONDesign / #ender_conversion_chat (2022-05-27)` (`132` words, score `25.4`)
> When you manually travel the axis, always use a finger pushing down slightly on the same side of the bed you wish it to travel, this helps simulate belt tension that direction which on linear rails can be the difference between finding a hiccup or missing it.   IE: If you are pushing back wards, put one finger on the bed in the back and use that to push towards back, vice versa for the front.  I learned this on my first attempt with linear rails on the Ender, I had a bad rail but you couldnt tell unless you did it just like this, there was a burr that it was running right over until it did a change direction right on it, the belt tension would cause the carriage to hang.

#### Candidate 6 — `VORONDesign / #afterburner_and_stealthburner_questions (2022-06-21)` (`136` words, score `18.6`)
> Im pretty sure I had to replace all of my connectors for everything in the Hartk PCB, except for my Revo-Voron thermistor and heater, which both plugged in using the Molex connectors.  IF your using the Hartk PCB, the white ones are JST-PH and the black ones are Micro Molex.   I recommend buying a couple spares too, cause its easy to break things or get a pin stuck in these when doing them that you cannot get out without tooling.  Molex connectors are tough to take down without the tool I have noticed.  You will need these connectors if building the Stealthburner with that PCB.   &    I also highly recommend you get this kit  to replace any other connectors you need back to motherboard for quick disconnects.   These molex connectors are very robust for mid cabling disconnects.

### 7.4 Category 4: Engineering Trade-Offs, Iteration Logs & What Failed (Mode A)

#### Candidate 1 — `Alchemical 3D / #🗞printer-design-blog (2024-01-25)` (`88` words, score `25.0`)
> Before I left you all last time I had just started the testing on alternative motion materials.   I am happy to say the testing that has been done, has gone much smoother than expected.   At least in dealing with the materials on the limited scale I am.   I have full confidence that these pullstruded rods can handle this job, but that does not mean testing will end there, more options are on the way for testing!  I am especially excited to play with the Igus Drylin series rods.

#### Candidate 2 — `Alchemical 3D / #🗞printer-design-blog (2022-08-03)` (`104` words, score `18.7`)
> Initial prototypes of the new systems are actually printing right now, marking some of the first pieces to go from concept to testing.   One of our major focus points here at AP is going to be providing an optimal product that achieves above market standard performance, for lower cost than other options.   Your going to see many posts through the development blog just like this, where systems were tested and failed, leading us to other solutions.   I feel this is important during an open development such as this.   Future builders can then see and understand why choices were made leading to that ultimate product.

#### Candidate 3 — `Alchemical 3D / #🔔announcements (2022-08-09)` (`157` words, score `18.7`)
> As we stated previously, cross compatibility of hardware is quite important for the build, so BETA testing is not necessarily spending the full cost of a printer just to be testing it.   If your like many of us, you can probably just build a printer from spare parts floating around your house, this is our goal here, we want to see people do just that and make this system work.   Keep in mind though, our lower enclosure as of now is specific to the frame.   At some point in the future we will design a more modular version of it with sliding size capabilities, but at the cost of aesthetics in relative to the original.  If you wish to test with another printer frame, we can make some temporary legs to set the printer frame on in the mean time, since the lower skirt also acts as support allowing ventilation and steppers to hide beneath the deck.

#### Candidate 4 — `3D Printscape / #bdsensor-eddy-coil-leveler (2026-03-29)` (`108` words, score `16.8`)
> First, thanks for the detailed responses, and yes there is definitely an issue in its raw form for the Kalico.   I had to edit the BDsensor.PY to include this information to bypass the initial limitation.   Please note the information following "try::  I also had to add a loopback for the information later in the config "return epos" but less important.    Keep in mind these edits were done to a slightly aged version of your BDSensor.py (final revision of 2025).   I plan to update the latest version to ensure compatibility at some point.   However these may transfer 1:1 to the latest config, I just havent tried.

#### Candidate 5 — `Monolith / #Unknown channel (2025-03-20)` (`104` words, score `10.4`)
> I might copy my stuff over to a log here.   I have several build logs running on this thing already as requested by suppliers in their discords and my own.   Really looking forward to testing Monolith, if I like the printed version enough, it will move to the CNC version for comparison results.   The results scale my contribution to mister Wayne here.   Just gotta get done with the build in the midst of everything else happening.    It does feel really good to be building a printer again though and not trying to solve every little physics or design challenge on my own for once.

### 7.5 Category 5: Signature Analogies, Parentheticals & Dry Maker Humor

#### Candidate 1 — `Alchemical 3D / #🗞printer-design-blog (2026-05-26)` (`98` words, score `34.6`)
> Also some new generic breadboards are being assembled for the MOSFET testing onslaught that is about to start.  The goal is to select from paper specs the MOSFETs to try, and then physically test them to compare results to simulation.  Since MOSFETs are not really a bianary solution (on or off) and more of a dynamic (this is what I will let through), the selection is absolutely critical for system specs.   Poor gate reaction to the logic voltage, and your Retort wont run anywhere near full power, thus unable to hit target ranges.  This means... spreadsheets... more spreadsheets....

#### Candidate 2 — `Alchemical 3D / #🗞printer-design-blog (2022-12-30)` (`204` words, score `33.1`)
> You cannot have a 3D printer without proper feet as well!  As I tested these square feet for printers (btw they are awesome) it became painfully clear that there is no adhesive or tape I own which will hold this magical rubber on to an object, and there is no hole through them without adding it to secure them...   So a new alternative method of mounting and holding them on was created.  Using the tapered angles of the "pyramid" shaped feet, a bracket was made that they simply slide into place.   This allows the feet to be easily removed in case of servicing the skirt area of the printer, as well as providing a very strong holding force on them compared to something like VHB tape.  If you for some reason have issues sourcing these feet, or maybe you do not like them, you can always source the same old bolt on style feet we all know and use instead like other printers use.  If you do decide to try these feet though on a 3D printer, be sure to order the softer variant, in my testing I have found the stiff versions to be a bit to much for the duty at hand.

#### Candidate 3 — `Alchemical 3D / #🗞printer-design-blog (2023-07-09)` (`88` words, score `27.4`)
> The best part about Retort in general though, is what happens when you look deeper in our electronics... we have mentioned this before but not gone too deep down the rabbit hole with the public.   Retort is an open source MODULAR system that is capable of not just managing one spool of filament, but will be an expandable (at minimal cost relative to first build) solution to dry additional rolls of filament.  The PCB teaser linked above has to do with just this feature... more to come soon...

#### Candidate 4 — `Alchemical 3D / #🗞printer-design-blog (2022-08-18)` (`97` words, score `18.7`)
> However!!!  That does not mean today was without progress at all.... We managed to finish the torquing system for the rear Z gantry portion, so its now in line with the rest of the system having easy access and a strong transmission to hold that precious build plate payload.   We have begun work on the rear motor mounts for the X/Y motion system as well (pictured here).  **Please keep in mind these photos are very early and by no means refined or final yet** (Do you trust me yet to get it right before moving on?).

#### Candidate 5 — `Alchemical 3D / #🗞printer-design-blog (2023-08-11)` (`94` words, score `18.7`)
> We will go ahead and throw in a fun image of all the hardware coming in and being made for Retort, but that’s about it.  [Collaborator] has begun building one in parallel with me based on the more refined part selection after this recent testing.  He is joining the code development side of this project, since my skills there are basically caveman art to his Mona Lisa.   I know Retort is a highly anticipated product, so you will be seeing a much larger update soon™ pending the arrival of these shipments.  (Sorry all)

#### Candidate 6 — `Alchemical 3D / #🗞printer-design-blog (2026-05-22)` (`96` words, score `18.7`)
> Retort is on its way to another revision right now.  The control circuit has gotten a fair bit more complex and I have been sitting in front of spreadsheets and simulation for the past few days learning about power design methods and part functions.   It's a deep, deep rabbit hole...   However, I am happy to say the final thermal balance and range has been selected, and the parts ordered.   It will need to undergo one more test to validate these selections, but it's been on track thus far and so we do not anticipate any surprises.
