# 03 System Architecture

## Overview

Tossly is a layered pipeline. Perception runs in Python, classification in Wekinator, game logic in Processing, and physical actuation on Arduino. Each layer has a single responsibility, which made development, debugging, and replacement manageable under time and power constraints.

## Full data flow

Camera
→ Python (MediaPipe feature extraction)
→ Wekinator (gesture classification)
→ Processing (winner and scoring logic)
→ Arduino (servos, fan, motor)

## Reasons for this structure

- Arduino stays lightweight and reliable by avoiding CV and game logic
- The ML model can be retrained without touching firmware
- Software and hardware can fail independently without taking down the whole system
- Team members can work in parallel on separate layers
- Inputs can change in future without redesigning the actuation layer

## Layer responsibilities

Python
- Extracts 21 hand landmarks per hand
- Converts landmarks to 10 finger curl values
- Sends numeric data to Wekinator using OSC

Wekinator
- Classifies 10 inputs into Rock, Paper, or Scissors for each player
- Produces two integers at roughly 30 updates per second
- Uses k nearest neighbours for quick training and low data requirements

Processing
- Receives gesture outputs and determines the round winner
- Manages first to three scoring and countdown triggers
- Sends one integer to Arduino per round result

Arduino
- Animates the scoreboard digits
- Controls the fan movement and music box motor
- Uses sequential motion and servo detaching to respect the 5 V budget

## Serial communication contract

Processing sends a single integer per round
- 0 means tie or idle
- 1 means Player 1 wins
- 2 means Player 2 wins

## Constraints that shaped the system

- Only 5 V USB power, so motion is staged and servos detach after each move
- The PCA9685 board could not be fully populated with independent channels using available tools, so the top and bottom digit segments were paired
- All digits except 7 can be shown, which is acceptable for this game
- The DC motor introduced noise, so a second Arduino isolates motor and fan

## What worked well

- The modular pipeline prevented cascading failures
- ML classification remained stable after short training
- Low serial bandwidth was robust and predictable
- Each layer ran in isolation for debugging

## Future revision ideas

- Replace the PCA module with a larger custom PCB for full segment independence
- Consolidate to one Arduino with isolated power rails
- Export the trained model to remove Wekinator
- Switch to I2C or embedded recognition to simplify the chain

See also
- Software, ML and actuation: 04_Software_ML_Actuation.md
- Hardware and fabrication: 05_Hardware_Fabrication.md

Project by Group 17, Cyber Physical Systems 2025–26
