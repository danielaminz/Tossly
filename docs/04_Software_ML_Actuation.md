# 04 Software, Machine Learning and Actuation

## Overview

The goal was simple, let people play Rock Paper Scissors with their hands while the system recognises gestures in real time and translates them into motion. The pipeline is split into four layers, Python for perception, Wekinator for classification, Processing for game logic, and Arduino for actuation.

## Computer vision in Python

- Uses a standard webcam with MediaPipe
- Detects 21 hand landmarks per hand
- Converts landmarks to five finger curl values per hand
- Sends ten values per frame to Wekinator using OSC
- Performs no classification, only feature encoding

Finger curl values provide stability across distance and lighting, and reduce input size.

Relevant code
- Python sender: code/python/python_feed_wekinator.py

## Gesture classification in Wekinator

- Ten numeric inputs
- Two discrete outputs, one per player
- Three classes, Rock, Paper, Scissors
- k nearest neighbours with k between 3 and 5
- Chosen for low data needs and live retraining

Training procedure
- Record Rock, Paper and Scissors for both hands
- Collect about 30 to 40 samples per class
- Train, then test with new users

## Game logic in Processing

- Receives Wekinator outputs
- Calculates round winner and manages first to three scoring
- Sends one integer to Arduino on valid rounds
- Filters noisy or partial gestures to avoid accidental triggers

Values sent to Arduino
- 0 for tie or idle
- 1 for Player 1 wins
- 2 for Player 2 wins

Relevant code
- Processing bridge: code/processing/processing_game_logic.pde

## Firmware on Arduino

- Receives one value per round
- Animates mechanical digits using staged motion
- Controls the fan reveal and music box motor
- Detaches servos after each move to stay within power limits

Two Arduino configuration
- Arduino 1, scoreboard servos via PCA9685
- Arduino 2, fan servo and DC motor

Relevant code
- Main firmware: code/arduino/arduino_scoreboard.ino
- Support firmware: code/arduino/arduino_fan_music.ino

## What worked

- Stable classification after short training
- Reliable serial communication
- Motion matched classification with no visible drift
- The stack tolerated restarts without breaking state

## What was reduced

- Full independence of all segments due to PCA size and wiring limits
- Motor and servos on one rail due to noise and resets
- Timed music playback reduced to a simple celebration trigger
- Embedded ML postponed due to deadline

## Why the pipeline holds value

- Inputs can be replaced without changing the hardware
- Wekinator can be removed later by exporting a model
- The system continues to function if ML is offline
- The architecture remains teachable and inspectable

See also
- Hardware and fabrication, 05_Hardware_Fabrication.md
- Testing and iterations, 06_Testing_Failures_Iterations.md

Project by Group 17, Cyber Physical Systems 2025–26
