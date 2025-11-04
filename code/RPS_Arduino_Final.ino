#include <Servo.h>

// ----------- Pin Mapping -----------
const int SEG_PINS[14] = {
  2, 3, 4, 5, 6, 7, 8,      // Digit 1 (Player 1)
  9, 10, 11, 12, 13, A0, A1 // Digit 2 (Player 2)
};

const int FAN_SERVO_PIN = A2;
const int MOTOR_PIN     = A3;  // PWM capable for DC motor

// ----------- Servos -----------
Servo segServos[14];
Servo fanServo;

// digit segment maps (only 6 unique segments because top+bottom linked)
bool digits[10][7] = {
  {1,1,1,1,1,1,0}, // 0
  {0,1,1,0,0,0,0}, // 1
  {1,1,0,1,1,0,1}, // 2
  {1,1,1,1,0,0,1}, // 3
  {0,1,1,0,0,1,1}, // 4
  {1,0,1,1,0,1,1}, // 5
  {1,0,1,1,1,1,1}, // 6
  {1,1,1,0,0,0,0}, // 7  (not used but valid)
  {1,1,1,1,1,1,1}, // 8
  {1,1,1,1,0,1,1}  // 9
};

// ----------- Game State -----------
int scoreP1 = 0;
int scoreP2 = 0;

bool waitingForCountdown = false;
unsigned long countdownStartTime = 0;
const unsigned long COUNTDOWN_WAIT_MS = 3000;
const unsigned long MUSIC_TIME_MS = 20000;

// ----------- Setup -----------
void setup() {
  Serial.begin(9600);

  for (int i = 0; i < 14; i++) {
    segServos[i].attach(SEG_PINS[i]);
    segServos[i].write(90);
  }

  fanServo.attach(FAN_SERVO_PIN);
  fanServo.write(90);

  pinMode(MOTOR_PIN, OUTPUT);
  analogWrite(MOTOR_PIN, 0);

  Serial.println("Tossly Arduino ready");
}


// ----------- Helper: set both digits -----------
void setDigit(int digitIndex, int number) {
  for (int seg = 0; seg < 7; seg++) {
    int servoIndex = digitIndex * 7 + seg;
    if (digits[number][seg]) {
      segServos[servoIndex].write(0);
    } else {
      segServos[servoIndex].write(90);
    }
    delay(80);
  }
}

// ----------- Helper: display live score -----------
void updateScoreboard() {
  setDigit(0, scoreP1);
  setDigit(1, scoreP2);
}

// ----------- Countdown sequence -----------
void runCountdown() {
  for (int i = 3; i >= 1; i--) {
    setDigit(0, i);
    setDigit(1, i);
    delay(600);
  }
  setDigit(0, 0);
  setDigit(1, 0);
}

// ----------- Win Animation -----------
void runWinAnimation(bool p1Winner) {
  int fanAngle = p1Winner ? 180 : 0;
  fanServo.write(fanAngle);
  analogWrite(MOTOR_PIN, 255);
  delay(MUSIC_TIME_MS);
  analogWrite(MOTOR_PIN, 0);
  fanServo.write(90);
  scoreP1 = scoreP2 = 0;
  updateScoreboard();
}


// ----------- Main Loop -----------
void loop() {
  if (Serial.available()) {
    int value = Serial.parseInt();

    Serial.print("Received: ");
    Serial.println(value);

    if (value == 3) {
      waitingForCountdown = true;
      countdownStartTime = millis();
    } else {
      waitingForCountdown = false;

      if (value == 1) scoreP1++;
      if (value == 0) scoreP2++;

      updateScoreboard();

      if (scoreP1 == 3) runWinAnimation(true);
      if (scoreP2 == 3) runWinAnimation(false);
    }
  }

  if (waitingForCountdown && millis() - countdownStartTime > COUNTDOWN_WAIT_MS) {
    waitingForCountdown = false;
    runCountdown();
    updateScoreboard();
  }
}