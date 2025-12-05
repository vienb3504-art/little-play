
import os
import sys

# 1. 强制设置 ImageMagick 路径
IMAGEMAGICK_PATH = r"D:\tools\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
os.environ["MOVIEPY_IMAGEMAGICK_BINARY"] = IMAGEMAGICK_PATH

def check_imagemagick():
    print(f"Python Version: {sys.version}")
    
    # 尝试寻找字体路径
    font_path = r"C:\Windows\Fonts\arial.ttf"
    if not os.path.exists(font_path):
        # 尝试其他常见字体
        font_path = r"C:\Windows\Fonts\calibri.ttf"
    
    print(f"使用字体路径: {font_path}")

    try:
        from moviepy import TextClip
        
        # MoviePy 2.x: 传入字体文件的完整路径
        clip = TextClip(text="Test Success", font=font_path, font_size=50, color='white', size=(400, 100))
            
        print("✅ TextClip 创建成功！(使用 Pillow 渲染)")
        print(f"Clip Duration: {clip.duration}")
        clip.close()
        
    except Exception as e:
        print(f"❌ 出错了: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_imagemagick()
