
from moviepy import *
import moviepy.video.fx as vfx
import math

def create_cinematic_clip(img_path, duration=3, screen_size=(1280, 720)):
    """
    创建一个带有“高级感”的视频片段：
    1. 自动判断图片比例
    2. 竖图/方图：使用模糊/变暗背景 + 主体投影 + 缓慢缩放
    3. 横图：使用缓慢推拉 (Ken Burns) 效果
    """
    w_screen, h_screen = screen_size
    img = ImageClip(img_path)
    w_img, h_img = img.size
    aspect_ratio = w_img / h_img
    screen_ratio = w_screen / h_screen

    # --- 效果 A: 竖屏/方图 (加背景) ---
    if aspect_ratio < 1.5: # 只要比 3:2 窄，就当做竖图处理 (通常 16:9 是 1.77)
        # 1. 背景：放大填满屏幕，变暗
        bg_clip = img.resized(height=h_screen)
        if bg_clip.w < w_screen:
            bg_clip = img.resized(width=w_screen)
        
        # 裁剪中心部分作为背景
        bg_clip = bg_clip.cropped(width=w_screen, height=h_screen, x_center=bg_clip.w/2, y_center=bg_clip.h/2)
        
        # 变暗处理 (MultiplyColor 0.3)
        bg_clip = bg_clip.with_effects([vfx.MultiplyColor(0.3)])
        
        # 2. 前景：适应屏幕高度的 90%，居中，加缓慢缩放
        fg_h = h_screen * 0.9
        fg_clip = img.resized(height=fg_h)
        
        # 缓慢放大效果 (1.0 -> 1.05)
        fg_clip = fg_clip.resized(lambda t: 1 + 0.015 * t)
        fg_clip = fg_clip.with_position('center')

        # 组合
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=screen_size)
        
    # --- 效果 B: 横屏大图 (推拉/摇移) ---
    else:
        # 1. 基础调整：先Resize到至少覆盖屏幕
        # 策略：先按高度充满，如果宽度不够再按宽度充满
        base_clip = img.resized(height=h_screen)
        if base_clip.w < w_screen:
            base_clip = img.resized(width=w_screen)
            
        # 2. 动态效果
        # 随机一种效果：缓慢放大 或 缓慢平移
        # 这里为了稳定性，统一使用“中心放大”效果，最百搭
        
        # 技巧：先放大一点点 (1.1倍)，然后在这个基础上做动态
        # 为了避免黑边，我们让起始大小就是覆盖屏幕的
        
        # 动态放大: t=0时 1.0倍, t=duration时 1.1倍
        # 注意：resized 的参数如果是函数，是对原始尺寸的乘数
        # 我们需要保证每一帧都比 screen 大，然后 crop center
        
        # 让图片初始稍微大一点点，方便剪裁
        scale_start = max(w_screen/w_img, h_screen/h_img)
        
        # 动态缩放函数
        def zoom_func(t):
            # 随时间线性增加 5%
            return scale_start * (1 + 0.02 * t)
            
        anim_clip = img.resized(zoom_func)
        
        # 始终居中裁剪出 1280x720
        # CompositeVideoClip 会自动处理超出画布的部分（即裁剪）
        # 只要我们把 anim_clip 设为 center 即可
        final_clip = CompositeVideoClip([anim_clip.with_position('center')], size=screen_size)

    # 设置时长
    final_clip = final_clip.with_duration(duration)
    
    return final_clip
