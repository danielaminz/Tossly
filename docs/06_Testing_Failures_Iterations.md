# 06 Integration, Testing and Iteration Log

## Overview

We built bottom up. Single components were validated first, then digits, then logic, then ML. The final build is reliable within scope, but only after forced pivots and scope reductions.

## Integration order

1. Actuation tests for servos, PCA mapping, and motor driver
2. Scoreboard sequencing, detach strategy, and reset logic
3. Game logic and first to three scoring
4. Full ML and CV pipeline live testing

## Final live flow

Camera → Python → Wekinator → Processing → Arduino 1 for digits → Arduino 2 for fan and music box

## Major constraints and workarounds

- PCA board was too small to wire 14 fully independent channels
  - Top and bottom segments share a linkage
  - All digits work except 7
- USB only 5 V power caused brownouts under parallel motion
  - Sequential movement and immediate detach
- DC motor spikes caused jitter and resets
  - Split into two Arduinos on separate rails
- ML latency occasionally triggered false rounds
  - Double Rock rule, countdown starts only when both show Rock

## Testing methods

- Unit testing for servo sweep, channel mapping, and motor direction
- Simulation testing by sending manual serial input without ML
- Full system testing with real gestures
- Stress testing with repeated matches to check heat and resets

## Reliable outcomes

- High classification accuracy after short training
- Predictable scoring and match reset
- No jitter after detaching servos
- Clear fan motion
- Stable power behaviour under sequential movement

## Features reduced

- Full independence of all segments
- Live punched music strip mechanism from the early concept
- Single board architecture
- Multi directional motor control
- Simultaneous servo animation

## Lessons from failures

- Mechanical realities overrule ideal software designs
- Power is a design material
- A simpler working system is better than a complex almost working system
- Motion must be intentional or it reads as noise

## If extended

- Custom PCB for full independence of all segments
- Isolated power rail to recombine both Arduinos
- Reintroduce ballerina and multi layer stage from the original concept
- Alternative sensing such as Leap Motion or embedded ML
- Export Wekinator model and run without the app

See also
- Reflection and outcomes, 07_Reflection_Learnings.md

Project by Group 17, Cyber Physical Systems 2025–26
