---
name: emi-review
description: Review a PCB layout for EMI and EMC problems with the EMI Analyzer tools and turn the findings into a short, prioritized list of real problems with fixes. Use when the user asks to check a board for EMI, EMC, ESD, decoupling, return paths, plane gaps or signal integrity, to triage EMI Analyzer findings, or to compare two versions of a board.
---

# EMI review

The EMI Analyzer tools report what its checks find. A check works from geometry and names, so
its list mixes real problems with things that only look like problems. Your job is the part a
check cannot do: decide which findings matter on this board, prove it from the board itself,
and hand the user a short list they can act on.

## 1. Analyze

- `analyze_board` with the `.kicad_pcb` (its `.kicad_pro` and any `emi.rules.yaml` go with it),
  `wait_s: 300`. Unsaved edits in KiCad are not on disk: ask the user to save first.
- If the run does not start or never finishes, call `status`: Docker is the usual cause.
- The board becomes a project; every later analysis adds a version. Use `force: true` only to
  re-run unchanged files.

## 2. Read the overview, not everything

- `findings` with no filter: read `totals`, `by_rule` and `notes` first. Notes say what was
  missing (no project file means differential pairs were guessed from names).
- Then `findings` with `severity: critical`, then `severity: warning` per check (`rule`),
  `detail: true` only for the ones you are judging. Do not page through hundreds of findings.
- `decoupling` without arguments gives one line per rail; ask for a rail or IC only where
  there are gaps.

## 3. Judge each finding against the board

Before you call a finding real, check what the check could not:

- **What the net carries.** Long nets, plane gaps and missing return vias matter for fast edges
  (clocks, SPI, RMII/RGMII, USB, Ethernet, SDIO, DDR, QSPI/PSRAM) and hardly at all for I2C,
  resets, enables, status, LEDs or a strap that never toggles. Use the net name, the parts on
  it (`nets`, or the board file), and the user's knowledge.
- **What the pin is.** A decoupling finding on an IC pin is real only if that pin draws supply
  current. A current monitor's sense input, an LDO's enable tied to its input, an op-amp input,
  an analog switch pin or a GPIO on a net named like a rail needs no capacitor. The board file
  says what each pin is: `(pinfunction "...")` and `(pintype "...")` on the pad.
- **Whether a connector leaves the enclosure.** ESD findings and `run_esd` results matter for
  connectors a person or a cable can touch. A board-to-board ribbon inside the enclosure is low
  risk; ask the user when it is not obvious.
- **How good the model is.** In `esd`, IC pins use a generic model (5 pF, diodes to the rails):
  absolute volts are estimates, and parts with robust bus pins (CAN, RS-485 transceivers) take
  more than the model suggests. Compare a line with and without the clamp at the connector, and
  lines with each other, rather than reading a volt figure as pass or fail.
- **Whether it is one cause.** Forty findings on one check usually share one cause (a split
  plane, a missing stitching row). Report the cause once.

If you can read the board file, do: a few lines of parsing (pads with their nets, pin functions
and positions) settle most questions. If the KiCad MCP tools are connected, use them to locate
parts and nets.

## 4. Report

Give the user a short prioritized list, worst first, per board:

- what and where (reference designators, net, board position from the finding's x and y in mm),
- why it matters on this board (one sentence, with the evidence you checked),
- the fix (concrete: "100 nF at U37 pin 5 to the ground plane", "two ground vias beside the
  TXP/TXN vias").

Then, separately and briefly: findings you judged not to matter and why, so the user can
disagree. Offer `open_in_app` so they can see the findings on the board.

To accept a finding on purpose, `finding` gives the `emi.rules.yaml` suppress entry; a reason
is required. Suggest suppressions only for things the user agrees are intentional.

## 5. After a fix

Re-run `analyze_board` on the saved board and call `compare`: it lists what was fixed and what
is new, matching findings that moved a little. Report both; a fix that adds a finding elsewhere
is worth knowing.

## What the results are not

They compare versions of one board and point at likely causes. They are not a pre-compliance
test and do not predict whether a board passes at a test lab. Say so if the user asks.
