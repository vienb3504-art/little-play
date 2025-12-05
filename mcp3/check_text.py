
import os
import sys

# 1. 强制设置 ImageMagick 路径
IMAGEMAGICK_PATH = r"D:\tools\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
os.environ["MOVIEPY_IMAGEMAGICK_BINARY"] = IMAGEMAGICK_PATH

def check_textclip():
    print("--- 字幕生成测试 ---")
    try:
        from moviepy import TextClip
        
        # 尝试使用默认字体，不指定 font
        # 在 Windows 上，MoviePy 2.x 有时自动检测不到默认字体
        print("1. 尝试指定 Arial 字体路径...")
        font_path = r"C:\Windows\Fonts\arial.ttf"
        
        clip = TextClip(
            text="测试字幕", 
            font=font_path, 
            font_size=50, 
            color='white', 
            bg_color='black',
            size=(400, 100)
        )
        
        print("✅ 字幕创建成功！")
        # 尝试写入一帧看看有没有报错
        clip.save_frame("test_caption.png", t=0)
        print("✅ 字幕渲染并保存图片成功 (test_caption.png)")
        
    except Exception as e:
        print(f"❌ 字幕测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_textclip()
