# 02 Design Rationale

## Challenge

How can a familiar game become a mechanical performance rather than another screen based interface, and can intelligence and playfulness be expressed through motion instead of pixels or voice feedback

## Key insight

Replacing visual display with kinetic behaviour reframes computation as action rather than representation. The result feels sculptural and spatial, and it is natural to read because people already understand motion as communication.

## Concept summary

Tossly is a small arena where the game is performed physically. Scores are shown by moving servo segments, not LEDs. A fan rotates like a miniature stage curtain to cover the losing side. A music box plays only when someone wins the match. The interface is not looked at, it is watched.

## Tradition and technology

- Rock Paper Scissors is universal, here read by computer vision
- The seven segment display is rebuilt as a mechanical typographic object
- The palette combines white 3D printed PLA with wood veneers and plywood
- A hand wound music box is driven by a DC motor controlled in code

## User flow

1. Players show hands, system stabilises in idle
2. Gestures are detected, classified, and converted to a single round value
3. Score increments mechanically, one digit at a time
4. First to three wins
5. Fan hides the losing score, music box plays
6. System resets for the next round

## Design principles

- Motion is the interface
- Clarity over spectacle
- Mechanisms remain visible and interpretable
- Constraints inform form and rhythm
- Perception, logic, and actuation remain modular

## From original idea to final form

The early music box concept aimed for complex theatre. The final system is intentionally simpler, but preserves the intention to communicate through motion and sound. The pivot traded ornament for legibility and made choreography, not props, the centre of the interaction.

See also

[01 – Project overview](../docs/01_ProjectOverview.md)

[03 – System architecture](../docs/03_SystemArchitecture.md)

[04 – Software, ML and actuation](../docs/04_Software_ML_Actuation.md)

[05 – Hardware and fabrication](../docs/05_Hardware_Fabrication.md)

[06 – Testing, failures and iterations](../docs/06_Testing_Failures_Iterations.md)

[07 – Reflection and learning outcomes](../docs/07_Reflection_Learnings.md)



Project by Group 17, Cyber Physical Systems 2025–26
