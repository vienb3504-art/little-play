
import os
from moviepy import TextClip
import moviepy.video.fx as vfx

def check_stroke_issue():
    print("--- 描边截断测试 ---")
    
    # 使用一个确定的字体
    font_path = r"C:\Windows\Fonts\msyh.ttc"
    if not os.path.exists(font_path):
        font_path = "Arial"
        
    print(f"使用字体: {font_path}")

    try:
        # 模拟 app.py 中的设置
        # 问题可能出在 stroke_width 导致文字变大，但容器 size 没变，或者 ImageMagick/Pillow 渲染时的边界计算问题
        
        # 方案 1: 增加 margin (MoviePy 2.x 没有 margin 参数在 init 里，通常在 Composite 时处理，或者 size 给大点)
        # 方案 2: method='label' (不换行) vs 'caption' (换行)
        
        # 我们尝试重现截断：使用 'caption' 且 size 限制宽度
        clip = TextClip(
            text="后面测试截断问题", 
            font=font_path, 
            font_size=60, 
            color='white', 
            stroke_color='black',
            stroke_width=5, # 加粗描边更容易重现
            method='caption',
            size=(400, None) # 限制宽度
        )
        clip.save_frame("test_truncation.png", t=0)
        print("✅ 测试图片已生成: test_truncation.png")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    check_stroke_issue()
