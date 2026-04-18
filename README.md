# 🍽️ AI Food Calorie Analyzer

An AI-powered web application that detects food items from an image (especially Indian thali) and calculates total calories automatically.

---

## 🚀 Features

- 📸 Upload image or capture using camera
- 🤖 Detect food items using Computer Vision
- 🔢 Count multiple servings of same item
- 🍛 Calculate total calories using nutrition database
- 📊 Visualize results with pie chart and bar graph
- 🌐 Interactive UI built with Streamlit

---

## 🧠 Tech Stack

- **Frontend/UI:** Streamlit
- **Backend:** Python
- **AI Model:** Roboflow (Computer Vision)
- **Visualization:** Plotly
- **Image Processing:** PIL

---

## ⚙️ How It Works

1. User uploads an image or captures via camera
2. Image is sent to Roboflow API
3. Model detects food items
4. Items are counted
5. Calories are calculated using nutrition database
6. Results are displayed with charts

---


## 📁 Project Structure

FoodCalorieAi/
│
├── app/
│ ├── detect.py # Food detection using Roboflow API
│ ├── calorie.py # Calorie calculation logic
│
├── utils/
│ ├── nutrition.py # Food calorie database
│
├── test_images/
│ ├── test.jpeg # Sample test image
│
├── main.py # CLI execution file
├── streamlit_app.py # Web app UI
└── README.md

