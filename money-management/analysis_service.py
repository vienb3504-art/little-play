import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime, timedelta
import platform
from matplotlib import font_manager

# --- Configuration ---

def configure_fonts() -> None:
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
    import matplotlib.patheffects as path_effects

    # Use a dark/cyberpunk style
    plt.style.use('dark_background')
    
    # Custom Neon Palette
    neon_palette = ['#08F7FE', '#FE53BB', '#F5D300', '#00ff41', '#FF2C05', '#bc13fe']
    sns.set_palette(neon_palette)
    
    # Ensure fonts are set again after style change
    configure_fonts() 
    
    # Create a Grid Layout: 
    # Top Left: Summary Text
    # Top Right: Donut Chart
    # Bottom: Area Chart
    fig = plt.figure(figsize=(12, 10))
    fig.patch.set_facecolor('#212946') # Dark blue-grey background
    
    grid = plt.GridSpec(2, 2, height_ratios=[1, 1.2], hspace=0.3, wspace=0.3)
    
    # --- A. Summary Panel (Top Left) ---
    ax_text = fig.add_subplot(grid[0, 0])
    ax_text.set_facecolor('#212946')
    ax_text.axis('off')
    
    # Calculate totals
    total_spent = df['amount'].sum()
    if 'category' in df.columns:
        top_cat = df.groupby('category')['amount'].sum().idxmax()
        top_cat_amount = df.groupby('category')['amount'].sum().max()
    else:
        top_cat = "N/A"
        top_cat_amount = 0
        
    date_range = f"{df[date_col].min().strftime('%m/%d')} - {df[date_col].max().strftime('%m/%d')}"
    
    # Text Effect: Glow/Outline
    glow_effect = [path_effects.withStroke(linewidth=3, foreground='#212946')]

    # Draw fancy text
    t1 = ax_text.text(0.1, 0.9, "本周消费总览", fontsize=20, color='#08F7FE', fontweight='heavy', fontfamily='sans-serif')
    t1.set_path_effects([path_effects.withStroke(linewidth=3, foreground='#212946', alpha=0.8)])
    
    t2 = ax_text.text(0.1, 0.65, f"￥{total_spent:,.2f}", fontsize=40, color='white', fontweight='bold')
    # Add a subtle shadow/glow to the main number to make it pop
    t2.set_path_effects([path_effects.SimpleLineShadow(offset=(2, -2), alpha=0.3), path_effects.Normal()])
    
    t3 = ax_text.text(0.1, 0.45, f"周期: {date_range}", fontsize=14, color='#e0e0e0', fontweight='bold')
    
    t4 = ax_text.text(0.1, 0.25, f"最大开销: {top_cat}", fontsize=14, color='#FE53BB', fontweight='bold')
    t5 = ax_text.text(0.1, 0.10, f"金额: ￥{top_cat_amount:,.2f}", fontsize=14, color='#FE53BB', fontweight='bold')

    # --- B. Donut Chart (Top Right) ---
    ax_pie = fig.add_subplot(grid[0, 1])
    ax_pie.set_facecolor('#212946')
    
    if 'category' in df.columns:
        raw_cat_data = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        # --- Optimization: Group small slices into "Others" ---
        total_sum = raw_cat_data.sum()
        threshold = 0.05 # Categories < 5% go to "Others"
        
        # Split into big and small
        big_cats = raw_cat_data[raw_cat_data / total_sum >= threshold]
        small_cats = raw_cat_data[raw_cat_data / total_sum < threshold]
        
        if not small_cats.empty:
            others_sum = small_cats.sum()
            # Create a new series for plotting
            category_data = big_cats.copy()
            category_data['其他'] = others_sum
        else:
            category_data = raw_cat_data

        # Donut chart
        wedges, texts, autotexts = ax_pie.pie(
            category_data, 
            labels=category_data.index, 
            autopct='%1.1f%%', 
            startangle=140,
            colors=neon_palette[:len(category_data)],
            wedgeprops=dict(width=0.4, edgecolor='#212946', linewidth=2), # Thicker edge for cleaner look
            textprops=dict(color="white", fontsize=11, fontweight='bold'),
            pctdistance=0.80  # Move percentage text closer to the edge
        )
        
        # Make percent labels stand out
        plt.setp(autotexts, size=10, weight="bold", color="white")
        # Add stroke to labels for readability against dark background slices if they overlap
        for text in autotexts + texts:
            text.set_path_effects([path_effects.withStroke(linewidth=2, foreground='#212946')])
            
        ax_pie.set_title('消费构成', color='white', fontsize=16, pad=20, fontweight='bold')
    else:
        ax_pie.text(0.5, 0.5, "No Category Data", ha='center', color='white')

    # --- C. Area Chart / Glow Line (Bottom) ---
    ax_line = fig.add_subplot(grid[1, :])
    ax_line.set_facecolor('#212946')
    
    daily_data = df.groupby(date_col)['amount'].sum().reset_index()
    
    # Main line
    sns.lineplot(data=daily_data, x=date_col, y='amount', ax=ax_line, 
                 color='#08F7FE', linewidth=3, marker='o', markersize=8, markeredgecolor='white', markeredgewidth=2)
    
    # "Glow" effect - simple fill under
    ax_line.fill_between(daily_data[date_col], daily_data['amount'], color='#08F7FE', alpha=0.15)
    ax_line.fill_between(daily_data[date_col], daily_data['amount'], color='#08F7FE', alpha=0.08) # Layering for gradient feel
    
    # Grid styling
    ax_line.grid(color='#2A3459', linestyle='--', alpha=0.6) # Dashed grid
    ax_line.spines['bottom'].set_color('#4A5580')
    ax_line.spines['left'].set_color('#4A5580')
    ax_line.spines['bottom'].set_linewidth(2)
    ax_line.spines['left'].set_linewidth(2)
    ax_line.spines['top'].set_visible(False)
    ax_line.spines['right'].set_visible(False)
    
    ax_line.tick_params(axis='x', colors='white', labelsize=10)
    ax_line.tick_params(axis='y', colors='white', labelsize=10)
    
    ax_line.set_title('每日消费趋势 (Neon Trend)', color='white', fontsize=16, pad=20, fontweight='bold')
    ax_line.set_xlabel('', color='white')
    ax_line.set_ylabel('金额 (CNY)', color='white', fontweight='bold')
    
    # Format x-axis dates nicely
    fig.autofmt_xdate()
    
    # plt.tight_layout() # tight_layout can conflict with custom GridSpec sometimes, use manual spacing if needed
    
    # 3. Output
    buffer = io.BytesIO()
    # Save with the facecolor to ensure background persists
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100, facecolor=fig.get_facecolor())
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
