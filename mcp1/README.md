# AI 播客生成器 (mcp1)

这是 **方案一 (mcp1)** 的实现：基于 Flask + edge-tts + pydub 的轻量级播客生成服务。

## 目录结构
```
mcp1/
├── output/             # 🎧 存放生成的 MP3 音频
├── docs/               # 📚 项目文档 (mcp1.md, advice.md 等)
├── .venv/              # 🐍 独立的 Python 虚拟环境
├── app.py              # 🚀 核心服务入口
├── requirements.txt    # 📦 依赖列表
├── test_api.py         # 🧪 测试脚本
└── README.md           # 📖 本说明文件
```

## 环境准备

本方案使用独立的虚拟环境，互不干扰。

### 1. 安装 FFmpeg (必须)
请确保系统已安装 FFmpeg 并配置好环境变量 (在终端运行 `ffmpeg -version` 检查)。

### 2. 启动服务
进入 `mcp1` 目录后：

```powershell
# 1. 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 2. 运行服务
python app.py
```
服务将在 `http://127.0.0.1:5000` 启动。

## 使用方法

### API 接口
- **地址**: `POST /api/podcast`
- **参数**:
  ```json
  {
    "script": [
      {"role": "male", "text": "你好，今天天气怎么样？"},
      {"role": "female", "text": "天气非常好，适合出去玩！"}
    ],
    "bgm_volume": -15
  }
  ```

### 测试脚本
在服务运行的情况下，另开一个终端：
```powershell
cd mcp1
.\.venv\Scripts\Activate.ps1
python test_api.py
```
生成的音频将保存在 `mcp1/output/` 目录下。
