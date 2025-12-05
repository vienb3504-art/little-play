
import os
from moviepy import TextClip

def check_margin():
    print("--- Margin 测试 ---")
    font_path = r"C:\Windows\Fonts\msyh.ttc"
    if not os.path.exists(font_path):
        font_path = "Arial"
        
    try:
        # 测试带 margin 的 TextClip
        clip = TextClip(
            text="测试下沉 gjpqy", 
            font=font_path, 
            font_size=60, 
            color='white', 
            stroke_color='black', 
            stroke_width=5,
            margin=(20, 20) # 尝试添加 margin
        )
        clip.save_frame("test_margin.png", t=0)
        print(f"✅ 生成成功: test_margin.png, Size: {clip.size}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    check_margin()
