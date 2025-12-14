# 🚀 项目部署与迁移指南

本文档详细说明如何将本项目迁移到新的环境（如同事电脑或 Linux 服务器）并启动运行。

## 1. 环境准备

### 基础环境

- **操作系统**: Windows / macOS / Linux (Ubuntu/CentOS 等)
- **Python 版本**: 建议 Python 3.9 或更高版本 (最低 3.8)

### 文件清单

确保以下核心文件被复制到新环境：

- `main.py` (入口文件)
- `requirements.txt` (依赖列表)
- `index.html` (前端页面)
- `*.py` (所有 Python 源代码文件: `models.py`, `schemas.py`, `crud.py`, `database.py`, `analysis_service.py` 等)
- `static/` 目录 (如果没有会自动创建，但建议保留)

> **注意**: `sql_app.db` 是数据库文件。如果你想保留之前的记账数据，请一并复制该文件；如果你想重置数据，请**不要**复制它，程序启动时会自动创建一个新的空数据库。

## 2. 迁移步骤

### 第一步：安装 Python 依赖

在项目根目录下打开终端 (Terminal / CMD)，运行：

```bash
pip install -r requirements.txt
```

### 第二步：检查中文字体 (仅 Linux 服务器)

如果部署在 **Linux 服务器** 上，图表生成功能 (`analysis_service.py`) 可能会因为缺少中文字体而显示方块乱码。
**解决方法**: 安装开源中文字体，例如文泉驿微米黑：

- **Ubuntu/Debian**:
  ```bash
  sudo apt-get install fonts-wqy-microhei
  ```
- **CentOS**:
  ```bash
  sudo yum install wqy-microhei-fonts
  ```

_Windows 和 macOS 通常自带支持的字体，无需额外操作。_

### 第三步：启动服务

使用 `uvicorn` 启动后端服务：

```bash
# 开发模式 (修改代码自动重启)
uvicorn main:app --reload --port 9090

# 生产模式 (稳定运行，监听所有公网 IP)
uvicorn main:app --host 0.0.0.0 --port 9090
```

- `--host 0.0.0.0`: 允许局域网或公网访问（不仅仅是本机）。
- `--port 9090`: 指定端口号。

## 3. 访问验证

启动成功后，你会看到类似以下的日志：

```
INFO:     Uvicorn running on http://0.0.0.0:9090 (Press CTRL+C to quit)
```

此时，在浏览器中访问：

- **Web 界面**: `http://<服务器IP>:9090/`
- **API 文档**: `http://<服务器IP>:9090/docs`

## 4. 常见问题排查

- **Q: 启动报错 "Module not found"**

  - A: 确认是否成功运行了 `pip install -r requirements.txt`，并且没有报错。

- **Q: 图表里的中文显示为 "□□"**

  - A: 参考上述“检查中文字体”部分安装字体，或删除 `~/.cache/matplotlib` 缓存文件夹后重启服务。

- **Q: 局域网其他电脑无法访问**
  - A: 确保启动命令加了 `--host 0.0.0.0`，并检查电脑/服务器的**防火墙**是否放行了 9090 端口。
