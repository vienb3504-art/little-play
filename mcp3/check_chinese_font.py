
import os
from moviepy import TextClip

def check_fonts():
    print("--- 字体可用性测试 ---")
    
    # 常见的支持中文的字体路径
    fonts = [
        r"C:\Windows\Fonts\msyh.ttc", # 微软雅黑
        r"C:\Windows\Fonts\simhei.ttf", # 黑体
        r"C:\Windows\Fonts\simsun.ttc", # 宋体
    ]
    
    found_font = None
    for f in fonts:
        if os.path.exists(f):
            print(f"✅ 找到字体: {f}")
            found_font = f
            break
    
    if not found_font:
        print("❌ 未找到常见中文字体")
        return

    try:
        print(f"尝试使用字体 '{found_font}' 生成中文...")
        clip = TextClip(
            text="你好世界 Hello World", 
            font=found_font, 
            font_size=60, 
            color='white', 
            stroke_color='black',
            stroke_width=2,
            size=(600, 200),
            method='caption'
        )
        clip.save_frame("test_chinese.png", t=0)
        print("✅ 中文字幕测试成功！已保存 test_chinese.png")
    except Exception as e:
        print(f"❌ 字体测试失败: {e}")

if __name__ == "__main__":
    check_fonts()
