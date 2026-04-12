import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.nutrition import nutrition


def calculate_calories(items):
    total = 0

    print("\n--- FOOD ANALYSIS ---\n")

    if len(items) == 0:
        print("No food detected!")
        return

    # Count items
    count = {}
    for item in items:
        item_clean = item.lower().strip()
        count[item_clean] = count.get(item_clean, 0) + 1

    # Print + calculate
    for item, num in count.items():
        cal_per_item = nutrition.get(item, 0)
        total_item_cal = cal_per_item * num

        if cal_per_item == 0:
            print(f"{item}: {num} → Not in database")
        else:
            print(f"{item}: {num} → {total_item_cal} kcal")

        total += total_item_cal

    print(f"\nTotal Calories: {total} kcal")

    return total