import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime, timedelta
import platform
from matplotlib import font_manager

# --- Configuration ---

def configure_fonts():
    """
    Configures matplotlib to use a Chinese-compatible font.
    Tries to detect common Chinese fonts on Windows/macOS/Linux.
    """
    system = platform.system()
    
    # Common Chinese fonts to check
    # SimHei (Windows), Arial Unicode MS (macOS), WenQuanYi Micro Hei (Linux)
    # Microsoft YaHei is also good on Windows
    
    plt.rcParams['axes.unicode_minus'] = False # Fix minus sign display
    
    try:
        if system == "Windows":
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'sans-serif']
        elif system == "Darwin":
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'sans-serif']
        else:
            plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Droid Sans Fallback', 'sans-serif']
    except Exception as e:
        print(f"Warning: Font configuration failed: {e}")

# Apply font configuration on module load
configure_fonts()

# --- Feature 1: Visual Report ---

def generate_visual_report(expense_list: list) -> str:
    """
    Generates a visual report (Pie Chart + Line Chart) from expense data.
    
    Args:
        expense_list (list): List of dicts, e.g.,
                             [{"date": "2025-12-01", "item": "...", "amount": 5.5, "category": "Food"}]
                             
    Returns:
        str: Base64 encoded image string (PNG format).
    """
    if not expense_list:
        return "" 

    # 1. Data Processing
    df = pd.DataFrame(expense_list)
    
    # Ensure date is datetime
    # Adjust column name if necessary based on actual input, but prompt specified 'date'
    date_col = 'date' if 'date' in df.columns else 'transaction_date'
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col])
    else:
        # Fallback or error if no date column found
        return ""
        
    # 2. Plotting
    # Set seaborn style - use a style that works well with the font config
    sns.set_theme(style="whitegrid", palette="pastel")
    # Important: set_theme might reset rcParams, so we ensure fonts are set again or passed explicitly
    configure_fonts() 

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Pie Chart (Category Share)
    if 'category' in df.columns:
        category_data = df.groupby('category')['amount'].sum()
        ax1.pie(category_data, labels=category_data.index, autopct='%1.1f%%', startangle=140)
        ax1.set_title('消费占比 (By Category)')
    else:
        ax1.text(0.5, 0.5, "No Category Data", ha='center')

    # Right: Line Chart (Daily Trend)
    daily_data = df.groupby(date_col)['amount'].sum().reset_index()
    sns.lineplot(data=daily_data, x=date_col, y='amount', ax=ax2, marker='o')
    ax2.set_title('每日趋势 (Daily Trend)')
    ax2.set_xlabel('日期')
    ax2.set_ylabel('金额')
    
    # Format x-axis dates nicely
    fig.autofmt_xdate()
    
    plt.tight_layout()

    # 3. Output
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig) # Close to free memory

    return image_base64

# --- Feature 2: Toxic Prediction ---

def toxic_prediction(expense_list: list, budget: float = 2000.0) -> str:
    """
    Generates a "toxic" prediction of month-end spending based on current progress.
    
    Args:
        expense_list (list): List of expense dicts.
        budget (float): Monthly budget.
        
    Returns:
        str: Markdown formatted string with the prediction and commentary.
    """
    if not expense_list:
        return "本宫还没看到任何账单，去花点钱再来找我！"

    df = pd.DataFrame(expense_list)
    date_col = 'date' if 'date' in df.columns else 'transaction_date'
    
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col])
    
    # Logic: Filter for current month
    now = datetime.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # We filter data to only include this month's expenses for accurate prediction
    if date_col in df.columns:
        current_month_df = df[df[date_col] >= current_month_start]
    else:
        current_month_df = df # Fallback if no date
    
    current_total = current_month_df['amount'].sum()
    
    # Days passed (including today)
    days_passed = now.day
    
    # Calculate days in current month
    # Logic: First day of next month - 1 day
    if now.month == 12:
        next_month = now.replace(year=now.year + 1, month=1, day=1)
    else:
        next_month = now.replace(month=now.month + 1, day=1)
    
    days_in_month = (next_month - timedelta(days=1)).day
    days_left = days_in_month - days_passed
    
    if days_passed == 0:
        daily_average = 0.0
    else:
        daily_average = current_total / days_passed
        
    predicted_total = current_total + (daily_average * days_left)
    overrun = predicted_total - budget
    
    # Copywriting (Toxic Persona)
    report = f"### 🔮 毒舌AI 财运预测\n\n"
    report += f"- **当前已花**: {current_total:.2f} 元\n"
    report += f"- **本月进度**: {days_passed}/{days_in_month} 天\n"
    report += f"- **日均消费**: {daily_average:.2f} 元\n"
    report += f"- **预计月底**: {predicted_total:.2f} 元\n\n"
    
    if overrun > 500:
        report += f"**💀 严重超支警告**\n\n"
        report += f"> 呵呵，照你这个花法，月底准备吃土吧！预计超支 {overrun:.2f} 元！你的钱包在哭泣，听到了吗？败家子！😡"
    elif overrun > 0:
        report += f"**⚠️ 轻微超支预警**\n\n"
        report += f"> 小心点！预计超支 {overrun:.2f} 元。虽然不多，但也是钱啊！控制一下你的双手！😤"
    else:
        report += f"**💅 表现尚可**\n\n"
        report += f"> 哟，居然没超支？预计结余 {abs(overrun):.2f} 元。保持这个节奏，本宫勉强夸你一句：干得漂亮。😏"
        
    return report
