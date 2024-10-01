
import cv2
import numpy as np
import os


def load_model():
    """Load the YOLO model."""
    net = cv2.dnn.readNet('project_files/yolov4_tiny.weights', 'project_files/yolov4_tiny.cfg')
    model = cv2.dnn_DetectionModel(net)
    model.setInputParams(scale=1 / 255, size=(416, 416), swapRB=True)
    return model

def detect_potholes(img, model):
    """Detect potholes in the image and return their areas."""
    classIds, scores, boxes = model.detect(img, confThreshold=0.6, nmsThreshold=0.4)
    pixel_area = []
    pothole_count = 0  # Initialize pothole counter

    # Detection 
    for (classId, score, box) in zip(classIds, scores, boxes):
        area = box[2] * box[3]
        pixel_area.append(area)
        print(f"Pothole detected with area (in pixels): {area}")

        # Draw rectangle around detected pothole
        cv2.rectangle(img, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]),
                      color=(0, 255, 0), thickness=2)

        pothole_count += 1  # Increment counter for each detected pothole

    print(f"Total number of potholes detected: {pothole_count}")
    return pixel_area, pothole_count

def classify_potholes(pixel_area):
    """Classify potholes based on pixel area and calculate total price."""
    # Define thresholds for categorizing potholes
    small_threshold = 10_000   # Small potholes: up to 10,000 pixels
    medium_threshold = 50_000   # Medium potholes: from 10,001 to 50,000 pixels

    # Price settings per pothole size
    small_pothole_price = 100
    medium_pothole_price = 150
    large_pothole_price = 250

    total_price = 0
    sizes_count = {'small': 0, 'medium': 0, 'large': 0}

    # Classify potholes based on pixel area
    for area in pixel_area:
        if area <= small_threshold:
            total_price += small_pothole_price
            sizes_count['small'] += 1  # Increment small pothole count
        elif area <= medium_threshold:
            total_price += medium_pothole_price
            sizes_count['medium'] += 1  # Increment medium pothole count
        else:  # area > medium_threshold
            total_price += large_pothole_price
            sizes_count['large'] += 1  # Increment large pothole count

    print(f"Total Price: {total_price}")
    print(f"Sizes Count: {sizes_count}")
    return total_price, sizes_count

def calculate_labor_costs(sizes_count):
    """Calculate labor costs based on pothole sizes."""
    labor_rate_per_hour = 400  # Example: 400 currency units per hour
    labor_time = {
        'small': 1,    # 1 hour for small potholes
        'medium': 2,   # 2 hours for medium potholes
        'large': 3     # 3 hours for large potholes
    }
    
    # Define how many workers are needed for each pothole size
    workers_needed = {
        'small': 1,    # 1 worker for small potholes
        'medium': 2,   # 2 workers for medium potholes
        'large': 3     # 3 workers for large potholes
    }

    # Calculate total labor hours and costs
    total_labor_hours = (sizes_count['small'] * labor_time['small'] +
                         sizes_count['medium'] * labor_time['medium'] +
                         sizes_count['large'] * labor_time['large'])

    total_workers = (sizes_count['small'] * workers_needed['small'] +
                     sizes_count['medium'] * workers_needed['medium'] +
                     sizes_count['large'] * workers_needed['large'])

    labor_cost = total_labor_hours * labor_rate_per_hour
    return labor_cost, total_workers

def generate_cost_items(sizes_count, labor_cost, total_workers):
    """Generate cost items including labor costs."""

    items = [
        { "item": "Asphalt Patch (Cold Mix)", "description": "Asphalt for pothole repair", "cost": 1500 },
        { "item": "Aggregate (Gravel)", "description": "Gravel to stabilize the base of the pothole.", "cost": 300 },
        { "item": "Tack Coat", "description": "Adhesive for bonding new asphalt to the old surface.", "cost": 150 },
        { "item": "Compacting Tools Rental", "description": "Hand tamper or small compactor rental.", "cost": 250 },
        { "item": "Labor Costs", "description": f"Workers for about {total_workers} workers, totaling {sum(sizes_count.values())} hours of work.", "cost": labor_cost }
    ]
    
    return items

def get_pothole_area(img_path):
    """Main function to process the image and calculate costs."""
    img = cv2.imread(img_path)
    model = load_model()
    pixel_area, pothole_count = detect_potholes(img, model)
    total_price, sizes_count = classify_potholes(pixel_area)
    labor_cost, total_workers = calculate_labor_costs(sizes_count)

    # Generate cost items
    items = generate_cost_items(sizes_count, labor_cost, total_workers)

    # Now, you can calculate the total item costs and distribute the costs
    total_item_cost = sum(item['cost'] for item in items)
    distributed_costs = []

    for item in items:
        allocated_cost = (item['cost'] / total_item_cost) * total_price
        distributed_costs.append({
            "item": item['item'],
            "allocated_cost": allocated_cost,
            "description": item['description']
        })

    return total_price, img, pothole_count, sizes_count, distributed_costs

