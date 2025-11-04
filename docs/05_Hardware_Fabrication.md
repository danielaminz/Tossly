# 05 Hardware, Electronics and Fabrication

## Overview

The hardware expresses state through motion. The scoreboard is mechanical, the fan hides the losing side, and a music box plays only when a match is won. The system is built under strict 5 V limits, so motion is staged and servos detach after each move.

## Core components

- 14 servos for the two mechanical seven segment digits
- 1 servo for the fan reveal
- 1 DC motor for the music box through an L298N driver
- Arduino Uno for digits
- Arduino Uno for fan and motor
- PCA9685 16 channel servo driver
- USB 5 V power shared across the system

## Mechanical digits

- Seven servos per digit
- Segments swing between 0 degrees for on and 90 degrees for off
- PLA arms on servo horns, behind a wooden face
- Top and bottom segments paired due to wiring constraints
- All digits except 7 are available, which is acceptable for this game
- Motion is sequential and quiet to respect power limits

## Fan reveal

- Single servo sweeps a panel to cover the losing side
- Built from veneered wood and acrylic
- Pin and slot linkage for repeatable motion
- Reads as a miniature stage curtain

## Music box

- Hand wound unit retrofitted with a DC motor
- Roller strip and light gear reduction
- Controlled by an L298N motor driver
- Plays during the win animation only

## Two Arduino architecture

The goal was one Arduino and a single PCA9685 board. Three issues forced a split. The PCA board was too small to wire every segment independently with available tools, the total current draw of servos plus motor exceeded USB limits, and the shared rail introduced noise that caused resets. Splitting into two microcontrollers created electrical isolation and stability.

## Fabrication methods

- 3D printing in PLA for servo mounts, segment arms, rollers and joints
- Laser cutting plywood for enclosure and frame, veneer for faces, acrylic for linkage tests
- Hand finishing for sanding, drilling, waxing and cable channels

## What worked

- Legible digits at several metres
- Stable behaviour under sequential motion
- Clear fan reveal
- Compact integration inside the frame

## What changed

- No fully independent segment control
- One board architecture was abandoned
- Music box control reduced to single direction playback
- Multi layer automaton reduced to a single focused stage

## Takeaways

- Power defines choreography
- Mechanical clarity is more important than mechanical completeness
- Build the enclosure early to protect electronics
- Visible motion communicates more effectively than lights

See also
- Software, ML and actuation, 04_Software_ML_Actuation.md
- Testing and iterations, 06_Testing_Failures_Iterations.md

Project by Group 17, Cyber Physical Systems 2025–26
