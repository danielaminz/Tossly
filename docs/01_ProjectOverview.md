# 01 Project Overview

Tossly is a physical digital Rock Paper Scissors scoreboard that replaces screens with motion. It reads two players' hand gestures using computer vision, determines the winner using machine learning, and performs the outcome using a mechanical seven segment display, a fan reveal, and a motor driven music box. Instead of showing pixels, the system expresses computation through choreography.

The project explores how a device can communicate intelligence through movement, timing, and material behaviour. Motion is treated as the interface, so outcomes are legible at a glance.

## Why this project matters

- Uses kinetic articulation as the primary interface
- Connects an ancient game to modern sensing and ML
- Demonstrates a clean separation between perception, decision, and actuation
- Shows how constraints in power and mechanics can lead to clearer expression

## What the system does

- Detects Rock, Paper and Scissors using a webcam with MediaPipe
- Classifies gestures in real time with Wekinator
- Sends a single integer to Arduino representing the round result
- Updates two mechanical seven segment digits, first to three wins
- Performs a short celebration with a fan reveal and a music box
- Resets automatically for the next match

## High level pipeline

Camera → Python (MediaPipe feature extraction) → Wekinator (gesture classification) → Processing (winner logic and serial output) → Arduino → Servo digits, fan, motor

## Constraints and decisions

- USB 5 V power only, so servos move sequentially and detach to prevent brownouts
- The PCA servo driver board could not support fully independent wiring for all channels with available tools, so the top and bottom digit segments were paired
- All digits 0 to 9 can be displayed except 7, which never appears in gameplay
- A second Arduino was added to isolate the motor and fan from the main servo board

## Project pivot

The initial concept was a large scale Royal Albert Hall automaton with live punched music strips and stage motion. Mechanical complexity and weight forced a pivot. The theatrical essence survived in Tossly as a focused moment, a fan reveal and a music box that plays when someone wins.

See also
- Design rationale: 02_DesignRationale.md
- System architecture: 03_SystemArchitecture.md

Project by Group 17, Cyber Physical Systems 2025–26
