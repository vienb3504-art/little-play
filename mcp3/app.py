import os
import json
import tempfile
from flask import Flask, request, send_file, send_from_directory

# 1. Configure ImageMagick BEFORE importing moviepy (just in case)
IMAGEMAGICK_PATH = r"D:\tools\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
os.environ["MOVIEPY_IMAGEMAGICK_BINARY"] = IMAGEMAGICK_PATH

# 2. MoviePy 2.x Imports
from moviepy import *
import moviepy.video.fx as vfx
import moviepy.audio.fx as afx
from effects import create_cinematic_clip # 导入新写的特效函数

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/auto_vlog', methods=['POST'])
def auto_vlog():
    temp_dir = tempfile.mkdtemp()
    # We need to keep track of opened clips to close them properly
    opened_resources = []
    
    try:
        # 1. Save inputs
        images = request.files.getlist('images')
        audio_file = request.files['audio']
        captions_str = request.form.get('captions')
        
        image_paths = []
        for img in images:
            path = os.path.join(temp_dir, img.filename)
            img.save(path)
            image_paths.append(path)
            
        audio_path = os.path.join(temp_dir, audio_file.filename)
        audio_file.save(audio_path)
        
        captions = []
        if captions_str:
            try:
                captions = json.loads(captions_str)
            except:
                pass

        # 2. Process images
        clips = []
        
        # Define font path for Windows (Prioritize Chinese Fonts)
        # 微软雅黑 > 黑体 > Arial
        possible_fonts = [
            r"C:\Windows\Fonts\msyh.ttc", 
            r"C:\Windows\Fonts\simhei.ttf",
            r"C:\Windows\Fonts\arial.ttf"
        ]
        FONT_PATH = "Arial" # Default fallback
        for f in possible_fonts:
            if os.path.exists(f):
                FONT_PATH = f
                break

        for i, img_path in enumerate(image_paths):
            # 使用新的特效函数生成视频片段
            # 默认 3秒时长，包含 Ken Burns 效果或背景模糊效果
            final_clip_step = create_cinematic_clip(img_path, duration=3)
            
            # Add CrossFadeIn (0.5s)
            final_clip_step = final_clip_step.with_effects([vfx.CrossFadeIn(duration=0.5)])
            
            # 3. Add captions (Optional)
            if i < len(captions):
                try:
                    # MoviePy 2.x TextClip
                    # 修复文字下半部分被截断的问题：
                    # 1. 使用 margin 参数增加内边距，防止描边被切
                    # 2. 调整位置到 0.80，防止被屏幕边缘切
                    txt_clip = TextClip(
                        text=captions[i], 
                        font=FONT_PATH,
                        font_size=50, 
                        color='white',
                        stroke_color='black', 
                        stroke_width=2,
                        margin=(20, 20) # 增加内边距，确保描边不被切
                    )
                    opened_resources.append(txt_clip)
                    
                    # 位置调整：底部稍微往上抬一点 (0.80 处)
                    txt_clip = txt_clip.with_position(('center', 0.80), relative=True) \
                                       .with_duration(3) \
                                       .with_effects([vfx.CrossFadeIn(duration=0.5)])
                    
                    # Composite
                    final_clip_step = CompositeVideoClip([final_clip_step, txt_clip], size=(1280, 720))
                    opened_resources.append(final_clip_step)
                except Exception as e:
                    print(f"TextClip error (skipping caption): {e}")
                    # Fallback is already final_clip_step
                    pass
            
            clips.append(final_clip_step)
            opened_resources.append(final_clip_step)

        # Concatenate
        final_video = concatenate_videoclips(clips, method="compose")
        opened_resources.append(final_video)
        
        # 4. Process Audio
        audio = AudioFileClip(audio_path)
        opened_resources.append(audio)
        
        if audio.duration < final_video.duration:
            # Loop audio
            audio = audio.with_effects([afx.AudioLoop(duration=final_video.duration)])
        else:
            # Subclip audio
            audio = audio.subclipped(0, final_video.duration)
            
        final_video = final_video.with_audio(audio)
        
        # 5. Export
        output_path = os.path.join(temp_dir, 'final_vlog.mp4')
        final_video.write_videofile(
            output_path, 
            codec='libx264', 
            audio_codec='aac', 
            fps=24, 
            logger=None
        )
        
        return send_file(output_path, mimetype='video/mp4', as_attachment=True, download_name='final_vlog.mp4')

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}, 500
        
    finally:
        # Cleanup resources
        for res in opened_resources:
            try:
                res.close()
            except:
                pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
