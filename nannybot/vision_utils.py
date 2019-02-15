import os
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import pdb

genet = cv2.dnn.readNet('models/age-gender-recognition-retail-0013.xml', 'models/age-gender-recognition-retail-0013.bin')
genet.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

def detect_gender(frame):
    blob = cv2.dnn.blobFromImage(frame, size=(62, 62), ddepth=cv2.CV_8U)
    genet.setInput(blob)
    out = genet.forward()
    print(out)
    # pdb.set_trace()
    print("age: %2.2f" % out[0][0][0][0] * 100)
    print("pct_male: %2.2f" % out[0][1][0][0] * 100)
    return out

emonet = cv2.dnn.readNet('models/emotions-recognition-retail-0003.xml', 'models/emotions-recognition-retail-0003.bin')
emonet.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

def detect_emotion(frame):
    blob = cv2.dnn.blobFromImage(frame, size=(62, 62), ddepth=cv2.CV_8U)
    emonet.setInput(blob)
    out = emonet.forward()
    print(out)
    # pdb.set_trace()
    # print("age: %2.2f" % out[0][0][0][0] * 100)
    # print("pct_male: %2.2f" % out[0][1][0][0] * 100)
    return out

facenet = cv2.dnn.readNet('models/face-detection-adas-0001.xml', 'models/face-detection-adas-0001.bin')
facenet.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

FN_DIM = (672, 384)

def detect_face(frame, thr_conf=.5, detect_extra=False):
    frame_fit = cv2.resize(frame, FN_DIM)
    blob = cv2.dnn.blobFromImage(frame_fit, size=FN_DIM, ddepth=cv2.CV_8U)
    facenet.setInput(blob)
    out = facenet.forward()

    predictions = []

    # Draw detected faces on the frame
    for detection in out.reshape(-1, 7):
        conf = float(detection[2])
        xmin = int(detection[3] * frame.shape[1])
        ymin = int(detection[4] * frame.shape[0])
        xmax = int(detection[5] * frame.shape[1])
        ymax = int(detection[6] * frame.shape[0])

        if conf > thr_conf:
            pred_boxpts = ((xmin, ymin), (xmax, ymax))
            if detect_extra:
                frame_face = frame[ymin:ymax, xmin:xmax]
                frame_face_small = cv2.resize(frame_face, (62, 62))
                cv2.imshow("Cropped", frame_face_small)
                gender = detect_gender(frame_face_small)
                emotion = detect_emotion(frame_face_small)
                prediction = (conf, pred_boxpts, gender, emotion)
            else:
                prediction = (conf, pred_boxpts)
            predictions.append(prediction)

    return predictions


def anno_face(img, pred):
    (pred_conf, pred_boxpts) = pred
    label = "person: {:.2f}%".format(pred_conf * 100)

    # extract information from the prediction boxpoints
    (ptA, ptB) = (pred_boxpts[0], pred_boxpts[1])
    (startX, startY) = (ptA[0], ptA[1])
    y = startY - 15 if startY - 15 > 15 else startY + 15

    # display the rectangle and label text
    cv2.rectangle(img, ptA, ptB,
                  (255, 0, 0), 2)
    cv2.putText(img, label, (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
    return img


def get_rel_pos_size(box):
    print(box)
    xloc = (box[0][0] + box[1][0]) / 2
    yloc = (box[0][1] + box[1][1]) / 2
    xsize = (box[1][0] - box[0][0])
    ysize = (box[1][1] - box[0][1])
    return xloc / FN_DIM[0], yloc / FN_DIM[1], xsize / FN_DIM[0], ysize / FN_DIM[1]


# initialize the camera and grab a reference to the raw camera capture
def init_picamera(res = (640, 480)):
    camera = PiCamera()
    camera.resolution = res
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=res)
    camera.rotation = 180
    time.sleep(0.1)

    return (camera, rawCapture)
