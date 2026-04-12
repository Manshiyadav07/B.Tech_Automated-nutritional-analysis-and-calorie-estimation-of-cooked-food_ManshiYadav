from app.detect import detect_food
from app.calorie import calculate_calories
import os

# Absolute safe path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
image_path = os.path.join(BASE_DIR, "test_images", "test.jpeg")

print("Using image:", image_path)

items = detect_food(image_path)

calculate_calories(items)