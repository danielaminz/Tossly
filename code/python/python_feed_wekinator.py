"""
Tossly Trainer — Python + MediaPipe + Wekinator control

Purpose
- Capture two hands from a webcam.
- Compute 5 finger-curl features per hand (10 features total).
- Stream features to Wekinator over OSC for live classification.
- Provide keyboard-driven trainer controls to record examples, train, and run the model.
- Draw a simple HUD for visibility during data collection.

Pipeline
Webcam → MediaPipe (hand landmarks) → feature encoding (finger curls) → OSC /wek/inputs → Wekinator

Notes on class indexing
- This script sets p1_target and p2_target to 0, 1, 2 and sends them to Wekinator via
  /wekinator/control/outputs. By default Wekinator discrete classifiers often expect 1..K.
- If your Wekinator project is configured for classes 1..3, change the hotkeys and targets
  to send 1, 2, 3 instead of 0, 1, 2. Alternatively keep this and subtract or add in Processing.
"""

import cv2, math, time
from pythonosc.udp_client import SimpleUDPClient
import mediapipe as mp

# ----------------- Wekinator OSC configuration -----------------
# Wekinator usually listens on 127.0.0.1 (same machine). Change if remote.
WEK_HOST = "127.0.0.1"

# Port 6448 is the standard Wekinator input port for features and control.
WEK_INPUT_PORT = 6448

# Address used to stream the feature vector. Must match Wekinator project setup.
OSC_INPUT_ADDR = "/wek/inputs"

# Control endpoints for Wekinator. These enable you to drive training from this script.
OSC_CTRL_OUTPUTS   = "/wekinator/control/outputs"          # set target outputs for recording
OSC_CTRL_START_REC = "/wekinator/control/startRecording"   # begin capturing one training example
OSC_CTRL_STOP_REC  = "/wekinator/control/stopRecording"    # stop current example
OSC_CTRL_TRAIN     = "/wekinator/control/train"            # train the model
OSC_CTRL_RUN       = "/wekinator/control/startRunning"     # enable live predictions
OSC_CTRL_STOPRUN   = "/wekinator/control/stopRunning"      # disable live predictions
OSC_CTRL_DELETEALL = "/wekinator/control/deleteAllExamples"# clear dataset

# UDP OSC client to send both features and control messages to Wekinator.
osc = SimpleUDPClient(WEK_HOST, WEK_INPUT_PORT)

# ----------------- MediaPipe Hands setup -----------------
# MediaPipe returns 21 landmarks per detected hand, normalized to [0,1] image coordinates.
mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils

# Hands configuration:
# - max_num_hands=2 because we need two players
# - model_complexity=0 is the lightest graph
# - min_detection_confidence and min_tracking_confidence tuned for stability
hands = mp_hands.Hands(
    max_num_hands=2,
    model_complexity=0,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# Landmark indices of fingertips according to MediaPipe's hand model
TIP_IDXS = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky

def clamp01(x):
    """Clamp a float to [0,1]. Useful when normalizing or guarding against numeric drift."""
    return max(0.0, min(1.0, x))

def finger_curls(landmarks):
    """
    Compute 5 finger-curl features for a single hand.

    Method
    - Use wrist as a reference (landmark 0).
    - For each fingertip, compute wrist-to-tip distance in normalized image space.
    - Normalize by the hand width (max_x - min_x) to reduce scale dependence.
    - Convert distance to a "curl" score in [0,1] where 1 is curled and 0 is open.

    Returns
    - List of 5 floats [thumb, index, middle, ring, pinky] each in [0,1].
    """
    # Hand width for normalization
    xs = [lm.x for lm in landmarks]
    minx, maxx = min(xs), max(xs)
    width = max(0.001, maxx - minx)  # avoid divide by zero for edge cases

    wrist = landmarks[0]             # reference point
    curls = []

    for tip in TIP_IDXS:
        dx = landmarks[tip].x - wrist.x
        dy = landmarks[tip].y - wrist.y
        dist = (dx*dx + dy*dy) ** 0.5  # Euclidean distance in normalized coords

        # Heuristic mapping: larger distance implies more extended finger
        # Scale by width*2.2 to keep output roughly inside 0..1 across hand sizes
        curl = 1.0 - clamp01(dist / (width * 2.2))
        curls.append(curl)

    return curls

def sort_hands_left_to_right(multi_hand_landmarks):
    """
    Ensure consistent assignment of Player 1 and Player 2.

    - MediaPipe does not guarantee ordering of detected hands.
    - We compute each hand's center x and sort so Player 1 is on the left.

    Returns
    - List of hand landmarks sorted left to right.
    """
    centers = []
    for h in multi_hand_landmarks:
        xs = [lm.x for lm in h.landmark]
        centers.append(sum(xs)/len(xs))  # average x as a crude horizontal center

    pairs = list(zip(centers, multi_hand_landmarks))
    pairs.sort(key=lambda p: p[0])       # ascending x: leftmost first

    return [p[1] for p in pairs]

# ----------------- Trainer state -----------------
# Class map as used locally in this script:
# 0 = Rock, 1 = Paper, 2 = Scissors
# Confirm this matches your Wekinator project and Processing mapping.
p1_target, p2_target = 0, 0     # current class targets when recording
recording = False               # whether we are currently recording a training example
record_until = 0.0              # timestamp when current recording should stop
RECORD_SEC = 2.0                # length of each captured example

def send_desired_outputs():
    """
    In Wekinator, for 2 Outputs with Discrete classification:
    - Send two floats representing target class labels for P1 and P2.
    - This primes Wekinator so that startRecording captures features with these labels.
    """
    osc.send_message(OSC_CTRL_OUTPUTS, [float(p1_target), float(p2_target)])

def start_recording():
    """Begin a labeled recording window for RECORD_SEC seconds."""
    send_desired_outputs()
    osc.send_message(OSC_CTRL_START_REC, [])
    print(f"Start recording: P1={p1_target}  P2={p2_target}")

def stop_recording():
    """Stop recording the current example."""
    osc.send_message(OSC_CTRL_STOP_REC, [])
    print("Stop recording")

def send_train():
    """Ask Wekinator to train on all collected examples."""
    osc.send_message(OSC_CTRL_TRAIN, [])
    print("Train requested")

def send_run():
    """Enable live predictions in Wekinator."""
    osc.send_message(OSC_CTRL_RUN, [])
    print("Start running (prediction on)")

def send_stop_run():
    """Disable live predictions in Wekinator."""
    osc.send_message(OSC_CTRL_STOPRUN, [])
    print("Stop running (prediction off)")

def send_delete_all():
    """Clear all collected examples in Wekinator."""
    osc.send_message(OSC_CTRL_DELETEALL, [])
    print("Deleted all training examples")

# ----------------- Video capture -----------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("Camera not found. Allow camera access in system privacy settings.")

# Rate limiting for OSC feature sends. Target ~30 Hz.
prev_send = 0.0

def label_text(c):
    """Human-readable label for the HUD. Keep consistent with your class mapping."""
    return ["Rock (0)", "Paper (1)", "Scissors (2)"][c]

# ----------------- Main loop -----------------
while True:
    ok, frame = cap.read()
    if not ok:
        break  # camera ended or failed

    # Mirror image for a more natural user experience
    frame = cv2.flip(frame, 1)

    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Run the hand detector and tracker
    res = hands.process(rgb)

    # Default features when a hand is missing (neutral mid-value to keep vector length fixed)
    p1_curls = [0.5] * 5
    p2_curls = [0.5] * 5

    if res.multi_hand_landmarks:
        # Order hands consistently: Player 1 on left, Player 2 on right
        ordered = sort_hands_left_to_right(res.multi_hand_landmarks)

        # Compute curls for whichever hands are visible
        if len(ordered) >= 1:
            p1_curls = finger_curls(ordered[0].landmark)
        if len(ordered) >= 2:
            p2_curls = finger_curls(ordered[1].landmark)

        # Draw landmarks and a small P1/P2 label near each hand for visual feedback
        for i, handLms in enumerate(ordered):
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            x = int(handLms.landmark[5].x * w)  # near index finger MCP joint
            y = int(handLms.landmark[5].y * h)
            cv2.putText(frame, f"P{i+1}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # Concatenate features [P1 five curls] + [P2 five curls] → total 10 floats
    features = p1_curls + p2_curls

    # Send features at ~30 fps to avoid flooding Wekinator
    now = time.time()
    if now - prev_send > 1 / 30:
        osc.send_message(OSC_INPUT_ADDR, features)
        prev_send = now

    # --------------- On-screen HUD for data collection ---------------
    # Simple bar graphs for P1 curls
    for i, v in enumerate(p1_curls):
        cv2.rectangle(frame, (10, 20 + i * 20), (10 + int(150 * v), 35 + i * 20), (0, 255, 0), -1)
        cv2.putText(frame, f"P1 f{i+1}:{v:.2f}", (170, 35 + i * 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 255, 200), 1)

    # Simple bar graphs for P2 curls
    for i, v in enumerate(p2_curls):
        cv2.rectangle(frame, (10, 150 + i * 20), (10 + int(150 * v), 165 + i * 20), (255, 0, 0), -1)
        cv2.putText(frame, f"P2 f{i+1}:{v:.2f}", (170, 165 + i * 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 255), 1)

    # Trainer HUD for targets and controls
    cv2.putText(frame,
                f"P1 target: {label_text(p1_target)}   [1=Rock 2=Paper 3=Scissors]",
                (10, h - 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame,
                f"P2 target: {label_text(p2_target)}   [7=Rock 8=Paper 9=Scissors]",
                (10, h - 95), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame,
                "E=record 2s   T=train   R=run   S=stop   C=clear   Q=quit",
                (10, h - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

    # Recording overlay and timer
    if recording:
        remaining = max(0.0, record_until - now)
        cv2.putText(frame, f"Recording... {remaining:.1f}s",
                    (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        # It is harmless to resend outputs during recording to keep Wekinator in sync
        if int(remaining * 10) % 5 == 0:
            send_desired_outputs()

        # Stop automatically when time is up
        if now >= record_until:
            stop_recording()
            recording = False

    cv2.putText(frame, "Press Q to quit",
                (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    cv2.imshow("Tossly Trainer — Python + MediaPipe + Wekinator control", frame)

    # --------------- Keyboard input ---------------
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == ord('Q'):
        break

    # P1 label hotkeys (set desired training label for Player 1)
    if key == ord('1'): p1_target = 0
    if key == ord('2'): p1_target = 1
    if key == ord('3'): p1_target = 2

    # P2 label hotkeys (set desired training label for Player 2)
    if key == ord('7'): p2_target = 0
    if key == ord('8'): p2_target = 1
    if key == ord('9'): p2_target = 2

    # Start a labeled recording window
    if key in (ord('e'), ord('E')) and not recording:
        send_desired_outputs()
        start_recording()
        recording = True
        record_until = time.time() + RECORD_SEC

    # Train and run controls
    if key in (ord('t'), ord('T')): send_train()
    if key in (ord('r'), ord('R')): send_run()
    if key in (ord('s'), ord('S')): send_stop_run()
    if key in (ord('c'), ord('C')): send_delete_all()

# Cleanup
cap.release()
cv2.destroyAllWindows()
