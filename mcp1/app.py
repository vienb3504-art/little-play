import os
import uuid
import asyncio
import logging
from flask import Flask, request, send_file, jsonify
import edge_tts
from pydub import AudioSegment

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 定义角色对应的语音模型
VOICE_MAPPING = {
    "male": "zh-CN-YunxiNeural",
    "female": "zh-CN-XiaoxiaoNeural"
}

# 临时文件目录
TEMP_DIR = "temp_audio"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

async def generate_speech_segment(text, role, output_file):
    """
    使用 edge-tts 生成单个语音片段
    """
    voice = VOICE_MAPPING.get(role, "zh-CN-XiaoxiaoNeural") # 默认使用女声
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    logger.info(f"生成的语音片段: {output_file} (角色: {role})")

async def process_podcast_generation(script, bgm_volume):
    """
    处理播客生成的核心逻辑
    """
    temp_files = []
    combined_audio = AudioSegment.empty()
    silence_500ms = AudioSegment.silent(duration=500)

    # 创建输出目录
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # 1. 遍历脚本生成语音
        for index, item in enumerate(script):
            role = item.get("role")
            text = item.get("text")
            
            if not role or not text:
                continue
            
            # 生成唯一文件名避免冲突
            temp_filename = os.path.join(TEMP_DIR, f"{uuid.uuid4()}_{index}.mp3")
            await generate_speech_segment(text, role, temp_filename)
            temp_files.append(temp_filename)

        # 2. 使用 pydub 拼接音频
        logger.info("开始拼接音频...")
        for i, temp_file in enumerate(temp_files):
            segment = AudioSegment.from_file(temp_file, format="mp3")
            combined_audio += segment
            
            # 在每段对话之间增加 500ms 的静音间隔 (最后一段后是否加看需求，这里加上保持一致或作为结束停顿)
            # 需求说“每段对话之间”，通常指中间。
            if i < len(temp_files) - 1:
                combined_audio += silence_500ms
        
        # 3. (可选) 处理背景音乐
        bgm_path = "background_music.mp3"
        if os.path.exists(bgm_path):
            logger.info(f"发现背景音乐: {bgm_path}")
            bgm = AudioSegment.from_file(bgm_path)
            
            # 调整背景音乐音量
            bgm = bgm + bgm_volume
            
            # 循环背景音乐以覆盖对话时长
            if len(bgm) < len(combined_audio):
                # 计算需要循环的次数
                loops = len(combined_audio) // len(bgm) + 1
                bgm = bgm * loops
            
            # 截取与对话相同的长度
            bgm = bgm[:len(combined_audio)]
            
            # 混合音频 (overlay)
            combined_audio = combined_audio.overlay(bgm)
        
        # 4. 导出最终文件
        output_filename = os.path.join(output_dir, f"podcast_{uuid.uuid4().hex[:8]}.mp3")
        combined_audio.export(output_filename, format="mp3")
        logger.info(f"最终音频已生成: {output_filename}")
        
        return output_filename

    finally:
        # 5. 清理临时文件
        logger.info("清理临时文件...")
        for f in temp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception as e:
                logger.error(f"清理文件失败 {f}: {e}")

@app.route('/api/podcast', methods=['POST'])
async def generate_podcast():
    """
    生成 AI 播客的 API 接口
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的 JSON 数据"}), 400
        
        script = data.get("script")
        if not script or not isinstance(script, list):
            return jsonify({"error": "缺少 script 列表或格式错误"}), 400
            
        bgm_volume = data.get("bgm_volume", -15)
        
        # 调用生成逻辑
        output_file = await process_podcast_generation(script, bgm_volume)
        
        # 返回文件下载
        return send_file(output_file, as_attachment=True, mimetype="audio/mpeg")

    except Exception as e:
        logger.error(f"生成播客失败: {str(e)}", exc_info=True)
        return jsonify({"error": f"处理失败: {str(e)}"}), 500

if __name__ == '__main__':
    # 检查 FFmpeg 是否安装 (简单的检查方式，依赖于 pydub 的报错，或者可以预检)
    # pydub 依赖 ffmpeg，如果没有安装，运行时会报错。
    # 这里打印提示信息。
    print("启动服务...")
    print("请确保系统已安装 FFmpeg 并添加到环境变量中。")
    app.run(debug=True, port=5000)
