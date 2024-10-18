import cv2

from utils.handDetector import HandDetector
from utils.oneHand import *
import tkinter
import time
import keyboard
import warnings
import queue
import threading

warnings.filterwarnings("ignore")

q = queue.Queue()
for i in range(10):
    q.put(' ')
def show_func():
    msg = q.get()
    while msg:
        label = tkinter.Label(text=msg, font=('Times', '30'), fg='red', bg='white')
        label.master.overrideredirect(True)
        label.master.geometry("+250+250")
        label.master.lift()
        label.master.wm_attributes("-topmost", True)
        label.master.wm_attributes("-disabled", True)
        label.master.wm_attributes("-transparentcolor", "white")
        label.pack()
        label.after(30, label.quit)
        label.mainloop()
        label.destroy()
        msg = q.get()


def press_hot_key(hotkey):
    if hotkey != '':
        keyboard.press_and_release(hotkey)


def recognize(camera_device, func_dict, short_dict, short_time):
    cap = cv2.VideoCapture(camera_device)
    shaka_list = []
    thumb_list = []
    finger_thumb_list = []
    palm_list = []
    rot_palm_list = []

    frame_cnt = 0
    rec = HandDetector()
    show_thread = threading.Thread(target=show_func)
    show_thread.start()
    while True:
        start = time.time()
        rec.init_landmarks()
        ret, img = cap.read()
        if not ret:
            break
        h, w, _ = img.shape

        img = cv2.flip(img, 1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        frame_cnt += 1
        rec.detect_hands(img)
        boxes = cal_box(rec.hand_landmarks)
        gestures = recognize_gesture(rec.hand_landmarks)
        gesture = ''
        two_mode = False
        if len(gestures) == 2:
            if gestures[0] == gestures[1] == 'Lshape' and np.abs(rec.hand_landmarks[0][0][1] - rec.hand_landmarks[1][0][1]) < 150:
                p1 = rec.hand_landmarks[0][0][:2]
                p2 = rec.hand_landmarks[1][0][:2]
                p_center = (p1 + p2) / 2
                dist = cal_dist(p1, p2)
                if len(shaka_list) > 10:
                    if frame_cnt - shaka_list[-1][1] < 10:
                        if dist < shaka_list[-10][0]-10:
                            cv2.putText(img, 'shaka close', (int(p_center[0]), int(p_center[1])), cv2.FONT_ITALIC, 1,
                                        (255, 0, 0), 2)
                            q.put(func_dict['shaka close'])
                            two_mode = True
                            if short_dict['shaka close'] is not "":
                                press_hot_key(short_dict['shaka close'])
                        if dist > shaka_list[-10][0]+10:
                            cv2.putText(img, 'shaka far', (int(p_center[0]), int(p_center[1])), cv2.FONT_ITALIC, 1,
                                        (255, 0, 0), 2)
                            q.put(func_dict['shaka far'])
                            two_mode = True
                            if short_dict['shaka far'] != "":
                                press_hot_key(short_dict['shaka far'])
                        shaka_list.append((dist, frame_cnt))
                shaka_list.append((dist, frame_cnt))


        # recognize cross

            if gestures[0] == gestures[1] == "one" and \
                    cal_dist(rec.hand_landmarks[0][6][:2], rec.hand_landmarks[1][6][:2]) < cal_dist(
                                            rec.hand_landmarks[0][5][:2], rec.hand_landmarks[0][8][:2]):
                p1 = rec.hand_landmarks[0][0][:2]
                p2 = rec.hand_landmarks[1][0][:2]
                p_center = (p1 + p2) / 2
                gesture = 'cross'
                q.put(func_dict[gesture])
                if short_dict[gesture] != "":
                    press_hot_key(short_dict[gesture])
                cv2.putText(img, 'cross', (int(p_center[0]), int(p_center[1])), cv2.FONT_ITALIC, 1,
                            (255, 0, 0), 2)
                two_mode = True
        for i in range(len(gestures)):
            # print(rec.hand_landmarks[i][0][1], h)
            if np.abs(rec.hand_landmarks[i][0][1]-h) < h*0.3:
                continue
            box = boxes[i]
            if gestures[i] == 'rock':
                thumb_list, shaka_list, finger_thumb_list, palm_list = [], [], [], []
            if gestures[i] == 'Thumb':

                if len(thumb_list) > 10 and frame_cnt - thumb_list[-1][1] < 10:
                    p_cur = rec.hand_landmarks[0][0][:2]
                    p_prev = thumb_list[-10][0]
                    angle = cal_angle(p_prev, p_cur)
                    dist = cal_dist(p_cur, p_prev)
                    if np.pi / 6 < angle < np.pi * 2 / 6 and dist > np.min((h, w)) * 0.05:
                        gesture = 'thumb right up'
                    elif np.pi * 2 / 6 < angle < 4 * np.pi / 6 and dist > np.min((h, w)) * 0.05:
                        gesture = 'thumb up'
                    elif np.pi * 4 / 6 < angle < 5 * np.pi / 6 and dist > np.min((h, w)) * 0.05:
                        gesture = 'thumb left up'
                    elif np.pi * 5 / 6 < angle < 7 * np.pi / 6 and dist > np.min((h, w)) * 0.05:
                        gesture = 'thumb left'
                    elif np.pi * 7 / 6 < angle < 8 * np.pi / 6 and dist > np.min((h, w)) * 0.05:
                        gesture = 'thumb left down'
                    elif (np.pi * 8 / 6 < angle or angle < -2 * np.pi / 6) and dist > np.min((h, w)) * 0.05:
                        gesture = 'thumb down'
                    elif -np.pi * 2 / 6 < angle < -np.pi / 6 and dist > np.min((h, w)) * 0.05:
                        gesture = 'thumb right down'
                    elif -np.pi / 6 < angle < np.pi / 6 and dist > np.min((h, w)) * 0.05:
                        gesture = 'thumb right'
                thumb_list.append((rec.hand_landmarks[i][0][:2], frame_cnt))
            elif gestures[i] == 'finger_thumb':
                dist_cur = cal_dist(rec.hand_landmarks[i][4][:2], rec.hand_landmarks[i][8][:2])
                if len(finger_thumb_list) > 10 > frame_cnt - finger_thumb_list[-1][1]:
                    dist_prev = finger_thumb_list[-5][0]
                    if np.abs(dist_prev - dist_cur) > np.min((h, w)) * 0.05:
                        if dist_prev < dist_cur:
                            gesture = "finger and thumb extend"
                        else:
                            gesture = 'finger and thumb close'
                finger_thumb_list.append((dist_cur, frame_cnt))
            elif gestures[i] == 'palm open':
                angle_cur = cal_angle(rec.hand_landmarks[i][0][:2], rec.hand_landmarks[i][12][:2])
                if len(palm_list) > 10 > frame_cnt - palm_list[-1][1]:
                    angle_prev = palm_list[-5][0]
                    if np.abs(angle_prev - angle_cur) > np.pi / 18:
                        if angle_prev < angle_cur:
                            gesture = 'palm vertical left'
                        else:
                            gesture = 'palm vertical right'
                    else:
                        gesture = 'palm open'
                palm_list.append((angle_cur, frame_cnt))
            elif gestures[i] == 'rot palm':
                angle_cur = cal_angle(rec.hand_landmarks[i][0][:2], rec.hand_landmarks[i][12][:2])
                if len(palm_list) > 10 and 5 > frame_cnt - rot_palm_list[-1][1]:
                    angle_prev = rot_palm_list[-5][0]
                    if np.abs(angle_prev - angle_cur) > np.pi / 18:
                        if angle_prev < angle_cur:
                            gesture = 'palm outward left'
                        else:
                            gesture = 'palm outward right'
                rot_palm_list.append((angle_cur, frame_cnt))
            else:
                gesture = gestures[i]
            if gesture != '':
                q.put(func_dict[gesture])
                press_hot_key(short_dict[gesture])
                cv2.putText(img, gesture, (box[0][0], box[0][1]), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)
            cv2.rectangle(img, (box[0][0], box[0][1], box[1][0] - box[0][0], box[1][1] - box[0][1]), (0, 255, 0),
                          2)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imshow("result", img)
        end = time.time()
        if (short_time-end-start)*1000 > 0:
            cv2.waitKey(int(short_time-(end-start)*1000))
        else:
            cv2.waitKey(1)
    cap.release()
    cv2.destroyAllWindows()
    q.put('')
    show_thread.join()
