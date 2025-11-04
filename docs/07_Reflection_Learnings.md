# 07 Reflection and Learning Outcomes

## What this project taught us

The most difficult part of a cyber physical system is translating digital certainty into meaningful physical behaviour. We had to think like designers, engineers, animators, and stage technicians at the same time.

We learned that motion has weight, delay, and cost, and that a system can be technically correct but unreadable unless its motion is legible.

## Design reflections

- The scoreboard is a performance surface, not a passive display
- Removing a screen made every decision visible
- One well paced movement carries more meaning than a busy UI
- The mechanical seven segment display became a study in motion grammar

## Engineering lessons

- Power budgets shape architecture
- Sequential actuation and servo detaching are essential under 5 V limits
- Real circuits behave differently from CAD models
- Splitting into two Arduinos was correct under constraints

## ML and software lessons

- After training, the ML layer was the least fragile part
- kNN was more effective in live conditions than a heavier neural network
- The pipeline stayed robust because each layer had one job
- Gesture recognition only felt intelligent once the mechanics were stable

## Team and process

- The pivot to Tossly saved the project
- Cutting features is a design decision
- Cross discipline debugging was productive
- Cardboard prototypes revealed truths faster than CAD

## What we would change next time

- Design power and actuation first
- Build a custom PCB instead of stretching a small PCA board
- Treat ML as optional so the system still functions if classification fails
- Allocate more time for wiring and assembly
- Prototype motion before enclosure

## Final position

Tossly is not a finished product, it is a coherent object that works within real constraints. It shows that a machine can communicate through motion, that mechanisms can be expressive without pretending to be invisible, and that intelligence can be physical as well as computational.

Project by Group 17, Cyber Physical Systems 2025–26
