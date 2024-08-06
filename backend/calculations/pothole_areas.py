import cv2
import os
import numpy as np



def get_pothole_area(img_path):
    # Reading test image
    img = cv2.imread(img_path)

    # Reading label name from obj.names file
    with open(os.path.join("project_files", 'obj.names'), 'r') as f:
        classes = f.read().splitlines()

    # Importing model weights and config file
    net = cv2.dnn.readNet('project_files/yolov4_tiny.weights', 'project_files/yolov4_tiny.cfg')
    model = cv2.dnn_DetectionModel(net)
    model.setInputParams(scale=1 / 255, size=(416, 416), swapRB=True)
    classIds, scores, boxes = model.detect(img, confThreshold=0.6, nmsThreshold=0.4)

    pixel_area = []

    # Detection 
    for (classId, score, box) in zip(classIds, scores, boxes):
        area = box[2] * box[3]
        pixel_area.append(area)
        
        cv2.rectangle(img, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]),
                    color=(0, 255, 0), thickness=2)
    
    # Getting Pixel Per Meter
    image = cv2.imread(img_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return [], img

    contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(contour)

    known_width_meters = 0.5  # Known width in meters
    reference_width_pixels = w

    ppm = reference_width_pixels / known_width_meters

    meter_area = [pixel / ppm for pixel in pixel_area]
        
    return meter_area, img

