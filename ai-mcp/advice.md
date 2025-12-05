
### 给你的整合建议（Main.py）

这三个 Prompt 会生成三个独立的代码片段。为了方便比赛演示，你可以再问 AI 最后一个问题，把它们合在一起：

> **整合任务**：
> 我现在有上面三个功能代码。请帮我把它们整合到一个 `main.py` 文件中。
> 1. 使用 Flask 启动一个服务，端口 5000。
> 2. 包含 `/api/podcast`, `/api/art_qr`, `/api/auto_vlog` 三个路由。
> 3. 请优化导入语句，处理好依赖。
> 4. 增加一个 `/` 根路由，返回 HTML 页面，页面上有简单的表单可以测试这三个接口（不需要太美观，能用就行）。

### 必杀技：如果遇到环境报错

Python 的多媒体库（特别是 MoviePy 和 Edge-TTS）在 Windows/Mac/Linux 上可能会有一些环境差异。如果运行报错，直接把**报错信息复制给 AI**，它解决配置问题的能力极强。

例如：
*   “MoviePy 报错 `ImageMagick is not installed` 怎么办？”
*   “Edge-TTS 报错 `RuntimeError: asyncio...` 怎么解决？”

祝你一周内搞定，惊艳全场！