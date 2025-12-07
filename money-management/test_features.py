import base64
from fastapi.testclient import TestClient
from main import app
import datetime
import os
import sys

# Ensure we can import modules from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

client = TestClient(app)

def test_features():
    user_id = "test_user_expert"
    
    # 1. Create dummy data
    print(f"Adding sample data for user: {user_id}...")
    
    today = datetime.date.today()
    expenses = [
        {"item-name": "Starbucks Coffee", "amount": 35.0, "category": "餐饮", "date": today.strftime("%Y-%m-%d")},
        {"item-name": "Subway Lunch", "amount": 25.0, "category": "餐饮", "date": today.strftime("%Y-%m-%d")},
        {"item-name": "Taxi", "amount": 45.0, "category": "交通", "date": (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")},
        {"item-name": "Books", "amount": 120.0, "category": "学习", "date": (today - datetime.timedelta(days=2)).strftime("%Y-%m-%d")},
        {"item-name": "Game", "amount": 299.0, "category": "娱乐", "date": (today - datetime.timedelta(days=3)).strftime("%Y-%m-%d")},
    ]

    for e in expenses:
        response = client.post("/expenses/", json={
            "user_id": user_id,
            "amount": e["amount"],
            "category": e["category"],
            "item-name": e["item-name"],
            "transaction_date": f"{e['date']}T12:00:00"
        })
        if response.status_code != 200:
            print(f"Failed to add expense: {response.text}")

    print("Data added successfully.\n")

    # 2. Test Toxic Prediction
    print(">>> Testing Toxic Prediction API...")
    # Set a low budget to trigger toxic response
    budget = 100.0 
    response = client.get(f"/analysis/toxic_prediction?user_id={user_id}&budget={budget}")
    if response.status_code == 200:
        print("Response received:")
        print("-" * 30)
        print(response.json().get("report", "No report field found"))
        print("-" * 30)
    else:
        print(f"Error: {response.status_code} - {response.text}")
    print("\n")

    # 3. Test Visual Report
    print(">>> Testing Visual Report API...")
    response = client.get(f"/analysis/visual_report?user_id={user_id}")
    if response.status_code == 200:
        data = response.json()
        b64_str = data.get("image_base64")
        if b64_str:
            # Save to file
            output_file = "test_report_result.png"
            with open(output_file, "wb") as f:
                f.write(base64.b64decode(b64_str))
            print(f"Success! Visual report saved to: {os.path.abspath(output_file)}")
        else:
            print("Error: No image data returned.")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_features()
