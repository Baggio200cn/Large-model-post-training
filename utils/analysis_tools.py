import pandas as pd
import matplotlib.pyplot as plt

def generate_analysis_chart(data, output_file):
    """
    生成数据分析图表
    :param data: 分析数据
    :param output_file: 输出文件路径
    """
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(data.index, data['NormalizedNumber1'], label='Normalized Number1')
        plt.plot(data.index, data['NormalizedNumber2'], label='Normalized Number2')
        plt.legend()
        plt.title("数据分析图表")
        plt.xlabel("日期")
        plt.ylabel("标准化值")
        plt.savefig(output_file)
        print(f"图表已保存至 {output_file}")
    except Exception as e:
        print(f"生成图表失败: {e}")

def generate_analysis_table(data):
    """
    生成分析表格
    :param data: 分析数据
    :return: HTML表格字符串
    """
    try:
        return data.head().to_html()
    except Exception as e:
        print(f"生成表格失败: {e}")
        return ""
