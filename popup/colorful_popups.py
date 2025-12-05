import tkinter as tk
import random

def create_popup(root, sentences):
    """创建一个随机的弹窗"""
    popup = tk.Toplevel(root)

    # 从列表中随机选择一句话
    sentence = random.choice(sentences)

    # 生成随机的十六进制背景色
    bg_color_hex = f'#{random.randint(0, 0xFFFFFF):06x}'
    popup.configure(bg=bg_color_hex)

    # 根据背景色的亮度决定文字颜色（黑色或白色）
    r = int(bg_color_hex[1:3], 16)
    g = int(bg_color_hex[3:5], 16)
    b = int(bg_color_hex[5:7], 16)
    brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    text_color = "black" if brightness > 0.5 else "white"

    # 获取屏幕尺寸
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 设置随机的窗口大小和位置
    width = random.randint(250, 450)
    height = random.randint(100, 250)
    x = random.randint(0, screen_width - width)
    y = random.randint(0, screen_height - height)
    popup.geometry(f'{width}x{height}+{x}+{y}')

    # 添加文本标签
    label = tk.Label(
        popup,
        text=sentence,
        wraplength=width - 20,  # 自动换行
        bg=bg_color_hex,
        fg=text_color,
        font=("Microsoft YaHei", 14, "bold"),
        padx=10,
        pady=10
    )
    label.pack(expand=True, fill='both')

    # 设置窗口标题
    popup.title("一条来自代码的消息")

def schedule_popups(root, sentences, count=10, start_delay=2000, end_delay=400):
    if count <= 0:
        return
    start = int(max(0, start_delay))
    end = int(max(0, end_delay))
    if count == 1:
        root.after(start, lambda: create_popup(root, sentences))
        return
    total = 0
    for i in range(count):
        d = start - (start - end) * (i / (count - 1))
        total += int(d)
        root.after(total, lambda: create_popup(root, sentences))

def main():
    # 创建主窗口并隐藏
    root = tk.Tk()
    root.withdraw()

    sentences = [
        "你今天看起来棒极了！",
        "代码的世界，创意无限！",
        "保持好奇，不断学习。",
        "你正在创造一些很酷的东西！",
        "每一个bug都是一次学习的机会。",
        "休息一下，喝杯咖啡吧！",
        "世界因你而更美好。",
        "你的努力终将获得回报。",
        "相信自己，你能行！",
        "每天都是新的一天，充满希望。"
    ]

    schedule_popups(root, sentences, count=20, start_delay=2000, end_delay=400)

    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    main()