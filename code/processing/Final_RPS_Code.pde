// Tossly — Processing bridge with serial output to Arduino
// Sends: 0=tie, 1=P1 win, 2=P2 win, 3=double-rock "ready"
// Mapping used here after subtracting 1 from Wekinator: 0=Rock, 1=Scissors, 2=Paper

import oscP5.*;
import netP5.*;
import processing.serial.*;

OscP5 oscP5;
Serial serialPort;
boolean serialReady = false;

final int BAUD = 9600;     // match Serial.begin(...) on Arduino
final int LOCK_TIME = 2000; // ms to lock after handling a round
final int READY_COOLDOWN_MS = 800; // ms debounce for repeated double-rock events

// Gesture classes (internal)
int p1 = -1, p2 = -1;      // 0=Rock, 1=Scissors, 2=Paper, -1 unknown
int lastP1 = -1, lastP2 = -1;

// Scores
int score1 = 0, score2 = 0;

// Round control
boolean roundLocked = false;
boolean roundComplete = false;
int roundLockMillis = 0;

// Serial send tracking
int lastSentValue = -999;
int lastReadySentAt = -999999;

// UI
String lastWinnerMsg = "";

void setup() {
  size(900, 600);
  surface.setTitle("Tossly — Processing → Arduino bridge");
  oscP5 = new OscP5(this, 12000);
  tryOpenSerial();
}

void draw() {
  background(10, 15, 30);
  drawTitle();
  drawScoreboard();
  drawWinnerBanner();

  if (roundLocked && millis() - roundLockMillis > LOCK_TIME) {
    roundLocked = false;
  }
}

void drawTitle() {
  fill(255);
  textAlign(CENTER, TOP);
  textSize(28);
  text("Tossly — Rock Paper Scissors", width/2, 20);
  textSize(16);
  fill(180);
  text("Classes: Rock=0  Scissors=1  Paper=2   |   Keys: R=reset, Shift+R=rescan serial", width/2, 55);
  fill(200);
  text(serialReady ? ("Serial: " + serialPort.portName() + " @ " + BAUD) : "Serial: not connected (dry-run)", width/2, 80);
}

void drawScoreboard() {
  pushStyle();
  rectMode(CENTER);
  fill(25);
  stroke(100);
  strokeWeight(3);
  rect(width/2, height/2, 600, 220, 20);
  popStyle();

  // Left digit (P1)
  pushMatrix();
  translate(width/2 - 180, height/2 - 90);
  drawDigit(score1, 100, 180, 16, true);
  popMatrix();

  // Right digit (P2)
  pushMatrix();
  translate(width/2 + 100, height/2 - 90);
  drawDigit(score2, 100, 180, 16, true);
  popMatrix();

  // colon
  noStroke();
  fill(120);
  ellipse(width/2, height/2 - 25, 10, 10);
  ellipse(width/2, height/2 + 45, 10, 10);
}

void drawDigit(int num, float w, float h, float t, boolean power) {
  boolean[][] map = {
    {true, true, true, true, true, true, false},   // 0
    {false, true, true, false, false, false, false}, // 1
    {true, true, false, true, true, false, true},  // 2
    {true, true, true, true, false, false, true},  // 3
    {false, true, true, false, false, true, true}, // 4
    {true, false, true, true, false, true, true},  // 5
    {true, false, true, true, true, true, true},   // 6
    {true, true, true, false, false, false, false},// 7
    {true, true, true, true, true, true, true},    // 8
    {true, true, true, true, false, true, true}    // 9
  };
  boolean[] on = map[constrain(num, 0, 9)];

  pushStyle();
  rectMode(CORNER);
  noStroke();

  int cOn  = color(255, 60, 60);
  int cOff = color(70, 20, 20);

  fill(on[0] ? cOn : cOff); rect(t, 0, w - 2*t, t, 4);                         // A
  fill(on[1] ? cOn : cOff); rect(w - t, t, t, (h/2 - t*1.5f), 4);              // B
  fill(on[2] ? cOn : cOff); rect(w - t, h/2 + t*0.5f, t, (h/2 - t*1.5f), 4);   // C
  fill(on[3] ? cOn : cOff); rect(t, h - t, w - 2*t, t, 4);                     // D
  fill(on[4] ? cOn : cOff); rect(0, h/2 + t*0.5f, t, (h/2 - t*1.5f), 4);       // E
  fill(on[5] ? cOn : cOff); rect(0, t, t, (h/2 - t*1.5f), 4);                  // F
  fill(on[6] ? cOn : cOff); rect(t, h/2 - t/2, w - 2*t, t, 4);                 // G
  popStyle();
}

void drawWinnerBanner() {
  if (lastWinnerMsg.length() > 0) {
    fill(240, 220, 120);
    textAlign(CENTER, CENTER);
    textSize(22);
    text(lastWinnerMsg, width/2, height - 90);
  }
  fill(180);
  textAlign(LEFT, BOTTOM);
  textSize(16);
  text("Press R to reset   |   Shift+R to rescan serial", 20, height - 20);
}

// ---------- Serial helpers ----------
void tryOpenSerial() {
  String[] ports = Serial.list();
  println("Available serial ports:");
  for (int i = 0; i < ports.length; i++) println(i + ": " + ports[i]);

  int chosen = -1;
  for (int i = 0; i < ports.length; i++) {
    String p = ports[i].toLowerCase();
    if (p.contains("usbmodem") || p.contains("usbserial") || p.contains("tty.usb")) {
      chosen = i;
      break;
    }
  }
  if (chosen == -1 && ports.length > 0) chosen = 0;

  if (chosen >= 0) {
    try {
      serialPort = new Serial(this, ports[chosen], BAUD);
      serialReady = true;
      println("Opened serial:", ports[chosen], "@", BAUD);
    } catch (Exception e) {
      println("Could not open serial:", e.getMessage());
      serialReady = false;
    }
  } else {
    println("No serial ports found. Running in dry-run.");
    serialReady = false;
  }
}

void resendSerial(int value, String reason) {
  // Sends a single byte value and logs it
  if (serialReady && serialPort != null) {
    try {
      serialPort.write((byte)value);
    } catch (Exception e) {
      println("Serial write error:", e.getMessage());
      serialReady = false;
    }
  }
  lastSentValue = value;
  println("SERIAL >", value, "|", reason);
}

// ---------- Round logic ----------
int winner(int a, int b) {
  if (a == b) return 0; // tie
  // With mapping 0=Rock,1=Scissors,2=Paper:
  // Rock beats Scissors, Scissors beats Paper, Paper beats Rock
  if ((a == 0 && b == 1) || (a == 1 && b == 2) || (a == 2 && b == 0)) return 1;
  return 2;
}

void handleRound(int a, int b) {
  int w = winner(a, b);
  if (w == 1) {
    score1++;
    showResult("Player 1 wins");
    resendSerial(1, "P1 wins");
  } else if (w == 2) {
    score2++;
    showResult("Player 2 wins");
    resendSerial(2, "P2 wins");
  } else {
    // tie but not necessarily double-rock, double-rock handled upstream
    showResult("Tie");
    resendSerial(0, "Tie");
  }
}

void showResult(String msg) {
  lastWinnerMsg = msg;
  roundLocked = true;
  roundComplete = true;
  roundLockMillis = millis();
}

// ---------- Keyboard ----------
void keyPressed() {
  if (key == 'r' || key == 'R') {
    if (keyEvent.isShiftDown()) {
      // Rescan serial
      if (serialPort != null) {
        try { serialPort.stop(); } catch(Exception e) {}
      }
      serialReady = false;
      tryOpenSerial();
      return;
    }
    // Reset scoreboard
    score1 = score2 = 0;
    lastWinnerMsg = "";
    roundLocked = false;
    roundComplete = false;
    println("Reset scoreboard");
  }
}

// ---------- OSC from Wekinator ----------
void oscEvent(OscMessage msg) {
  if (msg.checkAddrPattern("/wek/outputs")) {
    if (msg.typetag().length() >= 2) {
      // Wekinator likely outputs 1..3 for classes; convert to 0..2
      float a = msg.get(0).floatValue() - 1;
      float b = msg.get(1).floatValue() - 1;
      p1 = constrain(round(a), 0, 2);
      p2 = constrain(round(b), 0, 2);

      // If we just completed a round and inputs changed, clear banner
      if (roundComplete && (p1 != lastP1 || p2 != lastP2)) {
        roundComplete = false;
        lastWinnerMsg = "";
      }

      // Special case: double-rock "ready" → send 3 exactly once per cooldown
      if (!roundLocked && !roundComplete && p1 == 0 && p2 == 0) {
        if (millis() - lastReadySentAt > READY_COOLDOWN_MS) {
          resendSerial(3, "Double-rock ready");
          lastReadySentAt = millis();
        }
        // Do not return; you may still want to handle a round later when hands change
      }

      // Normal handling: if not locked and not complete, evaluate round
      if (!roundLocked && !roundComplete && p1 != -1 && p2 != -1) {
        // Only trigger a round when there is a decisive outcome or a non-ready tie
        int w = winner(p1, p2);
        boolean isDoubleRock = (p1 == 0 && p2 == 0);
        if (w != 0) {
          handleRound(p1, p2);
        } else if (!isDoubleRock) {
          // Ordinary tie (non-ready)
          handleRound(p1, p2);
        }
      }

      lastP1 = p1;
      lastP2 = p2;
    }
  }
}
