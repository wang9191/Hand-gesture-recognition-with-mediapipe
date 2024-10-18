import numpy as np
import cv2


def recognize_gesture(hand_landmarks):
    result = []
    for i in range(len(hand_landmarks)):
        result.append(recognize_one_hand(hand_landmarks[i]))
    return result


def recognize_one_hand(landmarks):
    dists = []
    marksArray = []
    for j in range(21):
        dists.append(cal_dist(landmarks[j][:2], landmarks[0][:2]))
        marksArray.append(landmarks[j][:2])
    marksArray = np.array(marksArray)
    hull = cv2.convexHull(marksArray, returnPoints=False).reshape((-1,)).tolist()
    minR = (dists[1] + dists[5] + dists[9] + dists[13] + dists[17]) / 5

    if 4 in hull and 8 not in hull and 12 not in hull and 16 not in hull and 20 not in hull and \
            cal_dist(landmarks[4][:2], landmarks[6][:2]) > cal_dist(landmarks[18][:2],
                                                                    landmarks[6][:2]) * 0.7:
        result = "Thumb"
    elif 4 in hull and 8 in hull and 12 in hull and 16 in hull and 20 in hull:
        result = "palm open"
    elif 4 not in hull and 8 in hull and 12 not in hull and 16 not in hull and 20 not in hull:
        result = "one"
    elif 4 not in hull and 8 in hull and 12 in hull and 16 not in hull and 20 not in hull:
        result = "two"
    elif 8 in hull and 12 in hull and 16 in hull and 4 not in hull and 20 not in hull and \
            cal_dist(landmarks[4][:2], landmarks[20][:2]) < 100:
        result = "three"
    elif 4 not in hull and 8 in hull and 12 in hull and 16 in hull and 20 in hull:
        result = "four"
    elif 12 in hull and 16 in hull and 20 in hull and cal_dist(landmarks[4][:2], landmarks[8][:2]) < 100:
        result = "ok"
    elif 12 not in hull and 16 not in hull and 20 not in hull and \
            cal_dist(landmarks[4][:2], landmarks[6][:2]) < cal_dist(landmarks[18][:2],
                                                                    landmarks[6][:2]) * 0.7:
        result = "rock"
    elif 4 in hull and 8 in hull and 12 not in hull and 16 not in hull and 20 not in hull:
        if np.abs(np.abs(cal_angle(landmarks[1][:2], landmarks[4][:2]) - cal_angle(landmarks[5][:2],
                                                                                   landmarks[8][
                                                                                   :2])) - np.pi / 2) < np.pi / 6:
            result = "Lshape"
        else:
            result = "finger_thumb"
    else:
        result = ""

    return result


def cal_dist(p1, p2):
        return np.sqrt(np.sum(np.power(p1-p2, 2)))


def cal_box(hand_landmarks):
        boxes = []
        for i in range(len(hand_landmarks)):
            boxes.append((np.min(hand_landmarks[i], 0)[:2], np.max(hand_landmarks[i], 0)[:2]))
        return boxes


def cal_angle(p1, p2):
        x = p2[0]-p1[0]+1
        y = p1[1]-p2[1]
        if x > 0 and y > 0:
            return np.arctan(y/x)
        elif x < 0 < y:
            return np.pi-np.arctan(y/np.abs(x))
        elif x < 0 and y < 0:
            return np.pi+np.arctan(np.abs(y)/np.abs(x))
        else:
            return -np.arctan(np.abs(y)/x)
