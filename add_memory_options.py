#!/usr/bin/env python3
"""
Generate realistic A/B/C/D options for Memory Items and patch the MD file.
Run from project root. Reads Citation_XL_XLS_Chapter2_5_QA.md and writes
options into each memory item block, then changes **Answer:** to **Correct answer: X –**.
"""
import re
import random
from pathlib import Path

MD_PATH = Path(__file__).resolve().parent / "Citation_XL_XLS_Chapter2_5_QA.md"

# All 70 memory items: (correct_answer_text, list of 3 distractor texts)
# Distractors are plausible wrong answers (other procedures, common confusions).
MEMORY_OPTIONS = [
    # APU FIRE
    ("Lift cover and push (APU FIRE button)", ["BATT Switch — EMER", "Throttle (affected engine) — IDLE", "Oxygen masks — DON and 100% oxygen"]),
    # BATT O'TEMP
    ("BATT DC AMPS — Note", ["BATT Switch — EMER", "BATT DC AMPS — Note decrease", "IGNITION Switches — ON"]),
    ("BATT Switch — EMER", ["BATT DC AMPS — Note", "BATT DC AMPS — Note decrease", "APU MASTER switch — OFF"]),
    ("BATT DC AMPS — Note decrease", ["BATT Switch — EMER", "BATT DC AMPS — Note", "FUEL BOOST Switches (both) — ON"]),
    # CAB ALT
    ("Oxygen masks — DON and 100% oxygen", ["Microphone switches — MIC OXY MASK", "Emergency descent — as required", "Oxygen masks/goggles — DON and EMER"]),
    ("Microphone switches — MIC OXY MASK", ["Oxygen masks — DON and 100% oxygen", "Emergency descent — as required", "Throttles (both) — IDLE"]),
    ("Emergency descent — as required", ["Oxygen masks — DON and 100% oxygen", "Microphone switches — MIC OXY MASK", "Initiate maximum rate of descent to a safe altitude"]),
    # EMER DESCENT
    ("Initiate maximum rate of descent to a safe altitude", ["Emergency descent — as required", "Thrust — REDUCE AS REQUIRED", "Takeoff — Abort"]),
    # LH/RH ENGINE FIRE
    ("Throttle (affected engine) — IDLE", ["ENGINE FIRE button (affected engine) — Lift cover and push", "Either displayed BOTTLE ARMED annunciator — Push", "Throttles (both) — CUT OFF"]),
    ("ENGINE FIRE button (affected engine) — Lift cover and push", ["Throttle (affected engine) — IDLE", "Either displayed BOTTLE ARMED annunciator — Push", "APU FIRE Button — Lift cover and push"]),
    ("Either displayed BOTTLE ARMED annunciator — Push", ["ENGINE FIRE button (affected engine) — Lift cover and push", "Throttle (affected engine) — IDLE", "THRUST REVERSER STOW switch (affected side) — EMER"]),
    # UNLOCK
    ("THRUST REVERSER STOW switch (affected side) — EMER", ["Thrust reverser levers — Check in stowed (full forward) position", "Throttle (affected engine) — Check IDLE", "AP TRIM DISC button — Push"]),
    ("Thrust reverser levers — Check in stowed (full forward) position", ["THRUST REVERSER STOW switch (affected side) — EMER", "Airspeed — 140 KIAS maximum", "Control wheel — GRIP"]),
    # ENG FAILURE BELOW V1
    ("Takeoff — Abort", ["Takeoff — Continue to a safe altitude", "Go-around procedures — EXECUTE", "WING XFLOW switch (if wing anti-ice is ON) — ON"]),
    # ENG FAILURE AT OR ABOVE V1
    ("Takeoff — Continue to a safe altitude", ["Takeoff — Abort", "Go-around procedures — EXECUTE", "Emergency descent — as required"]),
    ("WING XFLOW switch (if wing anti-ice is ON) — ON", ["Takeoff — Continue to a safe altitude", "IGNITION Switches — ON", "THRUST REVERSER STOW switch (affected side) — EMER"]),
    # DUAL ENGINE FAILURE
    ("IGNITION Switches — ON", ["FUEL BOOST Switches (both) — ON", "Throttles (both) — IDLE", "BATT Switch — EMER"]),
    ("FUEL BOOST Switches (both) — ON", ["IGNITION Switches — ON", "Throttles (both) — IDLE", "Oxygen masks/goggles — DON and EMER"]),
    ("Throttles (both) — IDLE", ["IGNITION Switches — ON", "FUEL BOOST Switches (both) — ON", "Throttles (both) — CUT OFF"]),
    # ENVIRONMENTAL SMOKE
    ("Oxygen masks/goggles — DON and EMER", ["Microphone switch — MIC OXY MASK", "Oxygen masks — DON and 100% oxygen", "Throttles (both) — CUT OFF"]),
    ("Microphone switch — MIC OXY MASK", ["Oxygen masks/goggles — DON and EMER", "Emergency descent — as required", "APU MASTER switch — OFF"]),
    # ELECTRICAL FIRE
    ("Oxygen masks/goggles — DON and EMER", ["Microphone switch — MIC OXY MASK", "BATT switch — OFF", "LH ENGINE FIRE button — Push"]),
    ("Microphone switch — MIC OXY MASK", ["Oxygen masks/goggles — DON and EMER", "BATT switch — OFF", "Parking brake — SET"]),
    # SMOKE REMOVAL
    ("Oxygen masks/goggles — DON and EMER", ["Microphone switches — MIC OXY MASK", "Oxygen masks — DON and 100% oxygen", "Thrust — REDUCE AS REQUIRED"]),
    ("Microphone switches — MIC OXY MASK", ["Oxygen masks/goggles — DON and EMER", "Emergency descent — as required", "Speed brakes — AS REQUIRED"]),
    # THRUST REVERSER IN-FLIGHT (5 steps)
    ("Control wheel — GRIP", ["AP TRIM DISC button — Push", "THRUST REVERSER STOW switch (affected side) — EMER", "Throttle (affected engine) — Check IDLE"]),
    ("AP TRIM DISC button — Push", ["Control wheel — GRIP", "THRUST REVERSER STOW switch (affected side) — EMER", "AP YD DISC/TRIM INT button — PRESS and RELEASE"]),
    ("THRUST REVERSER STOW switch (affected side) — EMER", ["Throttle (affected engine) — Check IDLE", "Airspeed — 140 KIAS maximum", "Control wheel — GRIP"]),
    ("Throttle (affected engine) — Check IDLE", ["THRUST REVERSER STOW switch (affected side) — EMER", "Airspeed — 140 KIAS maximum", "Throttles (both) — IDLE"]),
    ("Airspeed — 140 KIAS maximum", ["Throttle (affected engine) — Check IDLE", "Thrust — REDUCE AS REQUIRED", "Thrust — T/O DETENT"]),
    # EMERGENCY EVACUATION (6 steps)
    ("Parking brake — SET", ["Throttles (both) — CUT OFF", "LH ENGINE FIRE button — Push", "BATT switch — OFF"]),
    ("Throttles (both) — CUT OFF", ["Parking brake — SET", "LH ENGINE FIRE button — Push", "APU MASTER switch — OFF"]),
    ("LH ENGINE FIRE button — Push", ["RH ENGINE FIRE button — Push", "APU MASTER switch — OFF", "BATT switch — OFF"]),
    ("RH ENGINE FIRE button — Push", ["LH ENGINE FIRE button — Push", "APU MASTER switch — OFF", "BATT switch — OFF"]),
    ("APU MASTER switch — OFF", ["BATT switch — OFF", "Throttles (both) — CUT OFF", "Parking brake — SET"]),
    ("BATT switch — OFF", ["APU MASTER switch — OFF", "Throttles (both) — CUT OFF", "IGNITION Switches — ON"]),
    # OVERSPEED RECOVERY
    ("Thrust — REDUCE AS REQUIRED", ["Speed brakes — As required", "Thrust — INCREASE as required", "Airspeed — 140 KIAS maximum"]),
    ("Speed brakes — As required", ["Thrust — REDUCE AS REQUIRED", "Speed brakes — CONFIRM RETRACTED", "Flaps — RETRACT (15°) if required"]),
    # AILERON MISTRIM (fix: one option was a list)
]
# Fix the one list typo and continue
MEMORY_OPTIONS[36] = ("Speed brakes — As required", ["Thrust — REDUCE AS REQUIRED", "Speed brakes — CONFIRM RETRACTED", "Flaps — RETRACT (15°) if required"])

# Remaining 33 items (Aileron 1,2,3, Elevator 1,2,3, Rudder 1,2,3, Wheel brake 1,2, Autopilot/trim 1,2,3,4, Stall 1,2,3,4, Underspeed 1,2, TAWS 1-7, TWY/RWY 4)
REST = [
    ("Control wheel — GRIP FIRMLY", ["AP YD DISC/TRIM INT button — PRESS and RELEASE", "Roll trim — AS REQUIRED", "Pitch trim — ADJUST AS REQUIRED (in flight)"]),
    ("AP YD DISC/TRIM INT button — PRESS and RELEASE", ["Control wheel — GRIP FIRMLY", "Roll trim — AS REQUIRED", "AP YD DISC/TRIM INT button — PUSH and HOLD"]),
    ("Roll trim — AS REQUIRED", ["Control wheel — GRIP FIRMLY", "AP YD DISC/TRIM INT button — PRESS and RELEASE", "Rudder trim — AS REQUIRED"]),
    # Elevator
    ("Control wheel — GRIP FIRMLY", ["AP YD DISC/TRIM INT button — PRESS and RELEASE", "Pitch trim — ADJUST AS REQUIRED (in flight)", "Roll trim — AS REQUIRED"]),
    ("AP YD DISC/TRIM INT button — PRESS and RELEASE", ["Control wheel — GRIP FIRMLY", "Pitch trim — ADJUST AS REQUIRED (in flight)", "AP TRIM DISC button — Push"]),
    ("Pitch trim — ADJUST AS REQUIRED (in flight)", ["Control wheel — GRIP FIRMLY", "AP YD DISC/TRIM INT button — PRESS and RELEASE", "Roll trim — AS REQUIRED"]),
    # Rudder
    ("Rudder trim — AS REQUIRED", ["Rudder pedals — HOLD FIRMLY", "AP YD DISC/TRIM INT button — PRESS and RELEASE", "Roll trim — AS REQUIRED"]),
    ("Rudder pedals — HOLD FIRMLY", ["Rudder trim — AS REQUIRED", "AP YD DISC/TRIM INT button — PRESS and RELEASE", "Control wheel — GRIP FIRMLY"]),
    ("AP YD DISC/TRIM INT button — PRESS and RELEASE", ["Rudder trim — AS REQUIRED", "Rudder pedals — HOLD FIRMLY", "AP YD DISC/TRIM INT button — PUSH and HOLD"]),
    # Wheel brake
    ("Brake pedals — Remove feet", ["EMER BRAKE handle — Pull", "Parking brake — SET", "Throttles (both) — CUT OFF"]),
    ("EMER BRAKE handle — Pull", ["Brake pedals — Remove feet", "Parking brake — SET", "THRUST REVERSER STOW switch (affected side) — EMER"]),
    # Autopilot/trim runaway
    ("Control wheel — GRIP FIRMLY", ["AP YD DISC/TRIM INT button — PUSH and HOLD", "Throttles — Reduce as required to control airspeed", "Speed brakes — AS REQUIRED"]),
    ("AP YD DISC/TRIM INT button — PUSH and HOLD", ["Control wheel — GRIP FIRMLY", "AP YD DISC/TRIM INT button — PRESS and RELEASE", "Throttles — Reduce as required to control airspeed"]),
    ("Throttles — Reduce as required to control airspeed", ["Speed brakes — AS REQUIRED", "Thrust — INCREASE as required", "Throttles — Maximum thrust"]),
    ("Speed brakes — AS REQUIRED", ["Throttles — Reduce as required to control airspeed", "Speed brakes — CONFIRM RETRACTED", "Flaps — UP"]),
    # Stall
    ("AP TRIM DISC button — Push", ["Pitch attitude — Reduce", "Roll attitude — Level", "Throttles — Maximum thrust"]),
    ("Pitch attitude — Reduce", ["Roll attitude — Level", "Throttles — Maximum thrust", "AP TRIM DISC button — Push"]),
    ("Roll attitude — Level", ["Pitch attitude — Reduce", "Throttles — Maximum thrust", "Aircraft attitude and altitude — MONITOR"]),
    ("Throttles — Maximum thrust", ["Pitch attitude — Reduce", "Roll attitude — Level", "Thrust — T/O DETENT"]),
    # Underspeed
    ("Thrust — INCREASE as required", ["Aircraft attitude and altitude — MONITOR", "Thrust — REDUCE AS REQUIRED", "Throttles — Maximum thrust"]),
    ("Aircraft attitude and altitude — MONITOR", ["Thrust — INCREASE as required", "Aircraft pitch attitude — Smoothly pitch up climb as required to avoid terrain", "Landing gear — UP"]),
    # TAWS 1-7
    ("AP YD DISC/TRIM INT button — PRESS and RELEASE", ["Aircraft pitch attitude — Smoothly pitch up climb as required to avoid terrain", "Thrust — T/O DETENT", "Flaps — RETRACT (15°) if required"]),
    ("Aircraft pitch attitude — Smoothly pitch up climb as required to avoid terrain", ["Thrust — T/O DETENT", "Flaps — RETRACT (15°) if required", "Landing gear — UP"]),
    ("Thrust — T/O DETENT", ["Flaps — RETRACT (15°) if required", "Landing gear — UP", "Flaps — UP"]),
    ("Flaps — RETRACT (15°) if required", ["Landing gear — UP", "Flaps — UP", "Speed brakes — CONFIRM RETRACTED"]),
    ("Landing gear — UP", ["Flaps — UP", "Speed brakes — CONFIRM RETRACTED", "Thrust — T/O DETENT"]),
    ("Flaps — UP", ["Speed brakes — CONFIRM RETRACTED", "Landing gear — UP", "Flaps — RETRACT (15°) if required"]),
    ("Speed brakes — CONFIRM RETRACTED", ["Flaps — UP", "Landing gear — UP", "Speed brakes — As required"]),
    # TWY/RWY (4 items)
    ("Takeoff — ABORT", ["Takeoff — Continue to a safe altitude", "Go-around procedures — EXECUTE", "WING XFLOW switch (if wing anti-ice is ON) — ON"]),
    ("Go-around procedures — EXECUTE", ["Takeoff — ABORT", "Takeoff — Continue to a safe altitude", "Emergency descent — as required"]),
    ("Takeoff — ABORT", ["Go-around procedures — EXECUTE", "Takeoff — Continue to a safe altitude", "Emergency descent — as required"]),
    ("Go-around procedures — EXECUTE", ["Takeoff — ABORT", "Takeoff — Continue to a safe altitude", "Emergency descent — as required"]),
]
# Fix typo in REST (one had nested list)
REST[27] = ("Go-around procedures — EXECUTE", ["Takeoff — ABORT", "Takeoff — Continue to a safe altitude", "Emergency descent — as required"])
MEMORY_OPTIONS = MEMORY_OPTIONS + REST


def build_options_line(correct: str, distractors: list) -> tuple:
    """Return (list of 4 option strings A.–D., letter that is correct)."""
    combined = [correct] + list(distractors)[:3]
    combined = combined[:4]
    # Ensure we have exactly 4 unique options
    seen = set()
    unique = []
    for x in combined:
        x = x.strip()
        if x and x not in seen:
            seen.add(x)
            unique.append(x)
    while len(unique) < 4:
        unique.append("(No other action required)")
    random.shuffle(unique)
    letters = ["A", "B", "C", "D"]
    options = [f"{letters[i]}. {unique[i]}" for i in range(4)]
    idx = unique.index(correct)
    correct_letter = letters[idx]
    return options, correct_letter


def main():
    # For reproducible output
    random.seed(42)
    n_opts = len(MEMORY_OPTIONS)
    print("Memory option sets:", n_opts)
    text = MD_PATH.read_text(encoding="utf-8")

    # Find every **Answer: ...** line in the file (only in Memory Items section).
    # We replace them in order so the first match gets MEMORY_OPTIONS[0], etc.
    pattern = re.compile(r"\n\*\*Answer: ([^*]+)\*\*[ \t]*\n")
    matches = list(pattern.finditer(text))
    # Only replace those in the Memory Items section (after "## APU FIRE")
    mem_start = text.find("## APU FIRE")
    if mem_start == -1:
        mem_start = text.find("Memory Items (CE-560XL")
    matches = [m for m in matches if m.start() >= mem_start]
    print("Found", len(matches), "memory Answer lines in section.")

    # Build replacements (from end to start so indices stay valid)
    replacements = []
    for i, mo in enumerate(matches):
        if i >= n_opts:
            break
        correct, distractors = MEMORY_OPTIONS[i]
        options_list, correct_letter = build_options_line(correct, distractors)
        options_block = "\n".join(options_list) + "\n\n"
        answer_text = mo.group(1).strip()
        new_text = "\n" + options_block + f"**Correct answer: {correct_letter} – {answer_text}**\n"
        replacements.append((mo.start(), mo.end(), new_text))
    for start, end, new_text in reversed(replacements):
        text = text[:start] + new_text + text[end:]

    MD_PATH.write_text(text, encoding="utf-8")
    print("Patched", min(len(matches), n_opts), "memory items with options.")


if __name__ == "__main__":
    main()
