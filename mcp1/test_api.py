import requests
import json

url = "http://127.0.0.1:5000/api/podcast"

payload = {
    "script": [
        {"role": "male", "text": "你好，我是云希。今天我们要讨论什么话题？"},
        {"role": "female", "text": "你好，我是晓晓。今天我们来聊聊人工智能的发展吧！"}
    ],
    "bgm_volume": -15
}

try:
    print("正在发送请求...")
    response = requests.post(url, json=payload, stream=True)
    
    if response.status_code == 200:
        print("请求成功，正在下载音频...")
        with open("test_output.mp3", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("音频已保存为 test_output.mp3")
    else:
        print(f"请求失败: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"发生错误: {e}")
