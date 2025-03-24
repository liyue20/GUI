import os

import pandas as pd
import re
import io
import base64
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib import font_manager as fm
import numpy as np
from matplotlib.ticker import ScalarFormatter

def set_chinese_font():
    """
    设置中文字体，确保路径兼容本地和服务器部署
    """
    # 获取项目根目录
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # 拼接字体文件的路径
    font_path = os.path.join(project_root, 'src', 'utils', 'noto', 'NotoSansCJK-Regular.ttc')
    
    # 检查字体文件是否存在
    if not os.path.exists(font_path):
        print(f"未找到合适的中文字体，请检查路径：{font_path}")
        return None

    # 返回字体属性
    return fm.FontProperties(fname=font_path)


def extract_tables(markdown):
    """
    从 Markdown 中提取表格和对应的标识
    表格必须符合标准Markdown格式：
    - 必须包含表头
    - 必须包含分隔行
    - 所有行必须以 | 开始和结束
    """
    # 修改正则表达式，使其能够处理表格末尾没有换行符的情况
    pattern = r'\[chart:(\w+)\](\|[^\n]*\n\|[\s-]*\|[^\n]*\n(?:\|[^\n]*(?:\n|$))*)'
    tables = []
    
    for match in re.finditer(pattern, markdown):
        chart_type = match.group(1)
        table_content = match.group(2)
        
        # 验证表格格式
        lines = table_content.strip().split('\n')
        if len(lines) >= 3:  # 确保至少有表头、分隔行和一行数据
            # 检查是否所有行都是以 | 开始和结束
            if all(line.strip().startswith('|') and line.strip().endswith('|') for line in lines):
                # 检查第二行是否为分隔行
                if re.match(r'^\|([\s\-]+(\|[\s\-]+)*)\|$', lines[1].strip()):
                    tables.append((chart_type, table_content, match.group(0)))
                    
    return tables
def generate_chart_base64(df, chart_type):
    """
    生成图表并返回Base64编码的图片字符串
    """
    plt.figure(figsize=(4, 3),dpi=100)
    font = set_chinese_font()
    
    if chart_type == "bar":
        dates = df.iloc[:, 0]
        counts = pd.to_numeric(df.iloc[:, 1])
        
        plt.bar(dates, counts, color="skyblue")
        plt.title("柱状图", fontproperties=font)
        plt.xlabel(df.columns[0], fontproperties=font)
        plt.ylabel(df.columns[1], fontproperties=font)
        
        plt.xticks(rotation=45, fontproperties=font)
        plt.yticks(fontproperties=font)
    if chart_type == "barh":
        dates = df.iloc[:, 0]
        counts = pd.to_numeric(df.iloc[:, 1])

        # 创建一个图形和轴对象，增加图像尺寸以适应更大的字体
        fig, ax = plt.subplots(figsize=(7, 3), dpi=100)  # 稍微增加图像尺寸
        
        # 为柱子生成颜色渐变 - 使用紫色到蓝色的渐变
        num_bars = len(dates)
        colors = plt.cm.cool(np.linspace(0.2, 0.8, num_bars))
        
        # 调整y轴，减少柱子间距
        y_pos = np.arange(len(dates))
        ax.set_yticks(y_pos)
        # 增加y轴标签字体大小
        ax.set_yticklabels(dates, fontproperties=font, fontsize=14)
        
        # 绘制横向柱状图
        bars = ax.barh(y_pos, counts, color=colors, height=0.3)  # 稍微增加柱子高度
        
        # 在每个柱子末端添加数值标签
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.02*max(counts), bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', va='center', fontsize=14, fontproperties=font)
        
        # 设置x轴刻度标签格式
        formatter = ScalarFormatter(useOffset=False)
        formatter.set_scientific(False)
        ax.xaxis.set_major_formatter(formatter)
        
        # 增加x轴刻度标签字体大小
        ax.set_xticklabels([f'{int(x)}' for x in ax.get_xticks()], 
                           fontproperties=font, 
                           fontsize=14)  # 增加字体大小
        
        # 设置轴标签字体大小
        ax.tick_params(axis='both', which='major', labelsize=14)  # 统一设置刻度标签大小
        
        # 添加网格线
        ax.grid(axis='x', linestyle='--', alpha=0.7, color='#E0E0E0')
        
        # 隐藏顶部和右侧的边框
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(True)
        ax.spines['bottom'].set_visible(True)
        
        # 设置x轴范围，确保有足够空间显示标签
        ax.set_xlim(0, max(counts) * 1.2)  # 稍微增加右侧空间
        
        # 调整y轴范围，减少上下空白
        ax.set_ylim(-0.5, len(dates) - 0.5)
        
        # 调整图表边距，为更大的标签留出空间
        plt.subplots_adjust(left=0.25, right=0.9, top=0.95, bottom=0.15)
    elif chart_type == "pie":
        # 自动选择第一列为分类，第二列为数值生成饼图
        labels = df.iloc[:, 0]
        sizes = pd.to_numeric(df.iloc[:, 1])
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title("饼图", fontproperties=font)
        
    elif chart_type == "line":
        # 自动选择前两列来生成折线图
        x = df.iloc[:, 0]
        y = pd.to_numeric(df.iloc[:, 1])
        plt.plot(x, y, marker="o")
        plt.title("折线图", fontproperties=font)
        plt.xlabel(df.columns[0], fontproperties=font)
        plt.ylabel(df.columns[1], fontproperties=font)

    elif chart_type == "scatter":
        x = df.iloc[:, 0]
        y = pd.to_numeric(df.iloc[:, 1])
        plt.scatter(x, y, color="blue")
        plt.title("散点图", fontproperties=font)
        plt.xlabel(df.columns[0], fontproperties=font)
        plt.ylabel(df.columns[1], fontproperties=font)

    elif chart_type == "area":
        x = df.iloc[:, 0]
        y = pd.to_numeric(df.iloc[:, 1])
        plt.fill_between(x, y, color="skyblue", alpha=0.4)
        plt.plot(x, y, color="Slateblue", alpha=0.6)
        plt.title("面积图", fontproperties=font)
        plt.xlabel(df.columns[0], fontproperties=font)
        plt.ylabel(df.columns[1], fontproperties=font)

    elif chart_type == "radar":
        labels = df.columns.tolist()
        values = df.iloc[0].tolist()
        angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
        values += values[:1]
        angles += angles[:1]

        plt.subplot(111, polar=True)
        plt.plot(angles, values, color='blue', linewidth=2, linestyle='solid')
        plt.fill(angles, values, color='blue', alpha=0.4)
        plt.title("雷达图", fontproperties=font)
        plt.xticks(angles[:-1], labels, fontproperties=font)

    elif chart_type == "stacked_bar":
        df = df.set_index(df.columns[0])
        df = df.apply(pd.to_numeric, errors='coerce')
        df.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='Set2')
        plt.title("堆叠柱状图", fontproperties=font)
        plt.xlabel(df.columns[0], fontproperties=font)
        plt.ylabel('数量', fontproperties=font)        
    elif chart_type == "grouped_bar":
        df = df.set_index(df.columns[0])
        df = df.apply(pd.to_numeric, errors='coerce')
        ax = df.plot(kind='line', figsize=(12, 4), width=0.8, colormap='Set2')
        ax.set_xlabel("日期", fontproperties=font,fontsize=8)  #
        ax.set_ylabel("数值", fontproperties=font,fontsize=8) 
        ax.legend(labels=df.columns, loc='upper left', bbox_to_anchor=(1, 1),prop=font,fontsize=8) 
        for container in ax.containers:
            ax.bar_label(container, fontsize=8, padding=5)  # 设置字体大小和标签位置（padding）
        ax.spines['top'].set_visible(False)  # 隐藏顶部边框
        ax.spines['right'].set_visible(False)  # 隐藏右边框
        ax.spines['left'].set_visible(True)  # 保持左边框
        ax.spines['bottom'].set_visible(True)  # 保持底部边框
        plt.tight_layout()
        plt.xticks(rotation=45, fontproperties=font)
    elif chart_type == "grouped_line":
        df = df.set_index(df.columns[0])
        df = df.apply(pd.to_numeric, errors='coerce')
        ax = df.plot(kind='line', figsize=(12, 5), linewidth=1, colormap='Set2')
        ax.set_xlabel("日期", fontproperties=font, fontsize=12)  # x 轴设置为"日期"
        ax.set_ylabel("数值", fontproperties=font, fontsize=12)  # y 轴的标签可以固定为"数量"
        ax.legend(labels=df.columns, loc='upper left', bbox_to_anchor=(1, 1), prop=font, fontsize=12)

        # 设置线条标签（每个数据点上方显示数值）
        for line in ax.lines:
            yvals = line.get_ydata()
            for i, j in enumerate(yvals):
                ax.text(line.get_xdata()[i], yvals[i], f'{j:.2f}', fontsize=12, ha='center', va='bottom')

        # 隐藏图表的顶部和右边框
        ax.spines['top'].set_visible(False)  # 隐藏顶部边框
        ax.spines['right'].set_visible(False)  # 隐藏右边框
        ax.spines['left'].set_visible(True)  # 保持左边框
        ax.spines['bottom'].set_visible(True)  # 保持底部边框

        # 调整布局，避免标签重叠
        plt.tight_layout()
        # 旋转 x 轴标签（日期），避免重叠
        plt.xticks(rotation=45, fontproperties=font, fontsize=12)

    elif chart_type == "heatmap":
        plt.figure(figsize=(10, 6))
        sns.heatmap(df.corr(), annot=True, cmap="YlGnBu", fmt=".2f")
        plt.title("热力图", fontproperties=font)

    elif chart_type == "boxplot":
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=df, orient='h', palette="Set2")
        plt.title("箱型图", fontproperties=font)
        plt.xlabel('数值', fontproperties=font)

    elif chart_type == "density":
        plt.figure(figsize=(10, 6))
        sns.kdeplot(df.iloc[:, 1], shade=True, color="blue")
        plt.title("密度图", fontproperties=font)
        plt.xlabel(df.columns[1], fontproperties=font)
        plt.ylabel('密度', fontproperties=font)

    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png",transparent=True, bbox_inches="tight", dpi=100)
    plt.close()
    
    # 获取图像的Base64编码
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    
    return image_base64


def parse_table(table_str):
    """
    解析 Markdown 表格为 DataFrame
    优化：增加了列数一致性检查、格式错误处理、空格清理等功能。
    """
    # 确保输入表格字符串以换行符结束
    if not table_str.endswith('\n'):
        table_str += '\n'
        
    # 去除首尾空白和多余的空格
    lines = [line.strip() for line in table_str.strip().split('\n')]

    # 移除分隔行（行中包含 '---' 或者 '-')
    lines = [line for line in lines if not re.match(r'^\|\s*-+', line)]

    # 确保表格至少有表头和一行数据
    if len(lines) < 2:
        print("表格数据不足，无法解析")
        return None
    
    # 分割每行并清理空白
    rows = [
        [cell.strip() for cell in re.split(r'\|', line.strip('|'))]
        for line in lines
    ]
    
    # 检查列数一致性：表头和每一行的数据列数应一致
    header_columns = len(rows[0])
    valid_rows = [rows[0]]  # 保存表头
    
    for row in rows[1:]:
        if len(row) == header_columns:
            valid_rows.append(row)
        else:
            print(f"警告：表格数据行列数不一致，跳过这一行: {row}")
    
    # 如果没有有效数据行，返回None
    if len(valid_rows) < 2:
        print("没有有效的数据行")
        return None

    # 创建 DataFrame
    df = pd.DataFrame(valid_rows[1:], columns=valid_rows[0])
    
    return df



def markdown_to_markdown(markdown):
    """
    将带有图表标记的 Markdown 转换为包含Base64图片的 Markdown。
    """
    # 确保输入文本以换行符结束
    if not markdown.endswith('\n'):
        markdown += '\n'
        
    tables = extract_tables(markdown)
    result = markdown

    for i, (chart_type, table_content, full_match) in enumerate(tables):
        if chart_type:
            df = parse_table(table_content)
            image_base64 = generate_chart_base64(df, chart_type)
            # 创建数据 URI
            data_uri = f"data:image/png;base64,{image_base64}"
            # 构建 Markdown 图片标签
            image_markdown = f"![{chart_type}_chart_{i}]({data_uri})"
            # 使用 re.escape 处理 table_content 中的特殊字符
            table_pattern = re.escape(full_match)
            # 替换原始标记和表格为图片标签
            result = re.sub(table_pattern, image_markdown, result, count=1)

    
    return result


