 # Gesture Controlled Smart Widget System

import cv2
import mediapipe as mp
import math
import pyautogui

# Utils
def distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

# Setup
cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

mode = "MENU"
cooldown = 0
menu_hold_time = 0
exit_hold_time = 0

# UI Buttons
menu_buttons = [
    {"text": "PRESENTATION", "x": 50, "y": 80},
    {"text": "MEDIA", "x": 50, "y": 180},
    {"text": "DASHBOARD", "x": 50, "y": 280},
    {"text": "EXIT", "x": 50, "y": 380}
]

def draw_menu(img, hover):
    for b in menu_buttons:
        color = (0,255,0) if hover == b["text"] else (255,255,255)
        cv2.rectangle(img, (b["x"], b["y"]),
                      (b["x"]+350, b["y"]+70), color, 2)
        cv2.putText(img, b["text"], (b["x"]+20, b["y"]+45),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

# Main loop
 while True:
    success, img = cap.read()
    if not success:
        continue
    img = cv2.flip(img, 1)
    h, w, _ = img.shape
    cooldown = max(0, cooldown-1)

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    hover = None

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)

            index = hand.landmark[8]
            middle = hand.landmark[12]
            thumb = hand.landmark[4]

            cx, cy = int(index.x*w), int(index.y*h)
            cv2.circle(img, (cx, cy), 8, (0,0,255), -1)

            # Distances for gestures
            thumb_index = distance(index, thumb)
            index_middle = distance(index, middle)

            # MENU MODE
            if mode == "MENU":
                for b in menu_buttons:
                    if b["x"] < cx < b["x"]+350 and b["y"] < cy < b["y"]+70:
                        hover = b["text"]
                        if thumb_index < 0.05:
                            if b["text"] == "EXIT":
                                exit_hold_time += 1
                                cv2.putText(img, "HOLD TO EXIT...",
                                            (450,50),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                            (0,0,255), 2)
                                if exit_hold_time > 40:
                                    cap.release()
                                    cv2.destroyAllWindows()
                                    exit()
                            else:
                                if cooldown == 0:
                                    mode = b["text"]
                                    cooldown = 20
                        else:
                            exit_hold_time = 0

            # PRESENTATION MODE
            elif mode == "PRESENTATION":
                cv2.putText(img, "PRESENTATION MODE",
                            (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0,255,0), 2)
                if thumb_index < 0.05 and cooldown == 0:
                    pyautogui.press("right")
                    cooldown = 20
                elif thumb_index > 0.25 and cooldown == 0:
                    pyautogui.press("left")
                    cooldown = 20

                # Back to menu -> open hand
                if thumb_index > 0.3:
                    menu_hold_time += 1
                    if menu_hold_time > 90:
                        mode = "MENU"
                        menu_hold_time = 0
                else:
                    menu_hold_time = 0

            # MEDIA MODE
            elif mode == "MEDIA":
                cv2.putText(img, "MEDIA MODE",
                            (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255,0,0), 2)

                # Play/Pause -> thumb + index pinch
                if thumb_index < 0.05 and cooldown == 0:
                    pyautogui.press("space")
                    cooldown = 20

                # Volume Up/Down -> hand up/down
                if cy < h//3 and cooldown == 0:
                    pyautogui.press("up")
                    cooldown = 10
                elif cy > h*2//3 and cooldown == 0:
                    pyautogui.press("down")
                    cooldown = 10

                # Fullscreen -> index + middle pinch
                if index_middle < 0.02 and cooldown == 0:
                    pyautogui.press("f")
                    cooldown = 30

                # Back to menu -> open hand
                if thumb_index > 0.3:
                    menu_hold_time += 1
                    if menu_hold_time > 90:
                        mode = "MENU"
                        menu_hold_time = 0
                else:
                    menu_hold_time = 0

            # DASHBOARD MODE
            elif mode == "DASHBOARD":
                cv2.putText(img, "DASHBOARD MODE",
                            (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0,255,255), 2)

                # Volume control
                if cooldown == 0:
                    if cy < h//2:
                        pyautogui.press("up")
                        cooldown = 10
                    else:
                        pyautogui.press("down")
                        cooldown = 10

                # Back to menu -> open hand
                if thumb_index > 0.3:
                    menu_hold_time += 1
                    if menu_hold_time > 90:
                        mode = "MENU"
                        menu_hold_time = 0
                else:
                    menu_hold_time = 0

    if mode == "MENU":
        draw_menu(img, hover)

    cv2.imshow("Gesture Controlled Smart System", img)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()


