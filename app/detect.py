from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="VOEpgw2cTRKGUCQQnfXk"
)

def detect_food(image_path):
    result = CLIENT.infer(image_path, model_id="thali-detection-clean/1")

    detected_items = []

    for pred in result["predictions"]:
        confidence = pred["confidence"]

        if confidence > 0.2:
            detected_items.append(pred["class"])

    return detected_items