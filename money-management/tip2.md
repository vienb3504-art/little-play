# Role: Python 后端开发专家 (FastAPI/Flask)

# Context:

我正在开发一个基于腾讯云智能体的“校园记账助手”。
目前后端已经实现了“记账”和“查账”的基础接口。
现在我需要利用 `pandas`, `matplotlib` 和 `seaborn` 等数据分析库，补充两个高级功能接口。

# Data Structure (输入数据示例，具体请查看已有代码):

假设从数据库查询出来的消费记录列表 (`expense_list`) 格式如下：
[
{"date": "2025-12-01", "item": "食堂早餐", "amount": 5.5, "category": "餐饮"},
{"date": "2025-12-03", "item": "打车去市区", "amount": 35.0, "category": "交通"},
{"date": "2025-12-05", "item": "买教材", "amount": 45.0, "category": "学习"},
// ... 更多数据
]

# Task: 请编写以下两个 Python 函数/接口逻辑

## 功能 1：生成可视化周报 (Visual Report)

**目标**：接收上述 `expense_list`，生成一张包含“消费占比”和“每日趋势”的组合图表，并返回图片的 Base64 编码（或者文件路径）。
**具体要求**：

1. **数据处理**：将 JSON 列表转换为 Pandas DataFrame，并确保 `date` 字段转为 datetime 对象。
2. **绘图逻辑**：
   - 使用 `matplotlib` 和 `seaborn`。
   - **关键点**：必须处理**中文乱码**问题（代码中需指定系统字体，如 SimHei 或 Arial Unicode MS）。
   - 画布分为左右两部分：
     - 左边：饼图 (Pie Chart)，展示各 `category` 的消费占比。
     - 右边：折线图 (Line Chart)，展示每日消费总额的变化趋势（x 轴为日期，y 轴为金额）。
   - 配色风格：使用 seaborn 的 pastel 或 muted 配色，要看起来现代、美观。
3. **输出**：将图片保存到内存 (BytesIO)，并转换为 Base64 字符串返回。

## 功能 2：毒舌 AI 趋势预测 (Toxic Prediction)

**目标**：接收 `expense_list` 和可选的 `budget`（默认 2000 元），计算消费速度，并返回一段“毒舌”风格的预测文案。
**具体要求**：

1. **算法逻辑**：
   - 获取当前日期。
   - 计算本月已过的天数和剩余天数。
   - 计算本月目前的 `daily_average`（日均消费）。
   - 线性预测月底总消费：`predicted_total = current_total + (daily_average * days_left)`。
   - 计算超支金额：`overrun = predicted_total - budget`。
2. **文案生成（毒舌人设）**：
   - 必须包含：当前已花金额、日均消费、预计月底总额。
   - **分级反馈**：
     - **严重超支 (>500 元)**：语气尖酸刻薄，嘲讽用户败家，建议吃土。
     - **轻微超支 (>0 元)**：语气警告，带有紧迫感。
     - **未超支**：语气傲娇，勉强夸奖一下。
3. **输出**：直接返回格式化好的 Markdown 字符串。

# Tech Stack:

- Python 3.9+
- Pandas, Matplotlib, Seaborn
- 接口框架假设使用 FastAPI (如果你能提供 Flask 版本也可以)

# Output Requirement:

请提供完整的 Python 代码文件，包含依赖库导入、解决中文乱码的配置代码、以及这两个核心处理函数的实现。代码要有详细注释。
