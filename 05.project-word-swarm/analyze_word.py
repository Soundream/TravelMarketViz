import sys
import os
import json
import glob
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
from tqdm import tqdm

def load_articles(data_dir):
    """加载所有文章数据"""
    json_files = glob.glob(os.path.join(data_dir, "phocuswire_page_*.json"))
    all_articles = []
    
    print(f"找到 {len(json_files)} 个JSON文件")
    
    for json_file in tqdm(json_files, desc="加载文章数据"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
                all_articles.extend(articles)
        except Exception as e:
            print(f"读取文件 {json_file} 时出错: {e}")
    
    print(f"总共加载了 {len(all_articles)} 篇文章")
    return all_articles

def parse_date(date_str):
    """解析日期字符串为日期对象"""
    try:
        date_formats = [
            "%B %d, %Y",
            "%d %B %Y",
            "%B %Y",
            "%Y-%m-%d",
        ]
        
        for date_format in date_formats:
            try:
                return datetime.strptime(date_str.strip(), date_format)
            except ValueError:
                continue
                
        return None
    except:
        return None

def analyze_word_frequency(articles, target_word):
    """分析目标词语的频率分布"""
    # 初始化月度统计
    monthly_counts = defaultdict(int)
    total_count = 0
    articles_containing_word = 0
    
    # 转换目标词为小写
    target_word = target_word.lower()
    
    # 遍历所有文章
    for article in tqdm(articles, desc="分析文章"):
        try:
            # 获取文章日期
            date_str = article.get('date')
            if not date_str:
                continue
                
            date_obj = parse_date(date_str)
            if not date_obj:
                continue
            
            # 将日期转换为年月格式
            year_month = date_obj.strftime("%Y-%m")
            
            # 获取文章内容并转换为小写
            content = article.get('content', '').lower()
            title = article.get('title', '').lower()
            
            # 统计词语在内容中的出现次数
            content_count = content.count(target_word)
            title_count = title.count(target_word)
            total_in_article = content_count + title_count
            
            if total_in_article > 0:
                monthly_counts[year_month] += total_in_article
                total_count += total_in_article
                articles_containing_word += 1
            
        except Exception as e:
            print(f"处理文章时出错: {e}")
    
    return monthly_counts, total_count, articles_containing_word

def plot_frequency_distribution(monthly_counts, target_word, output_dir):
    """绘制频率分布图"""
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 准备数据
    months = sorted(monthly_counts.keys())
    counts = [monthly_counts[month] for month in months]
    
    # 创建图表
    plt.figure(figsize=(15, 8))
    plt.plot(months, counts, marker='o')
    
    # 设置标题和标签
    plt.title(f'"{target_word}" 词频随时间的分布', fontsize=14)
    plt.xlabel('时间', fontsize=12)
    plt.ylabel('出现次数', fontsize=12)
    
    # 旋转x轴标签以防重叠
    plt.xticks(rotation=45, ha='right')
    
    # 添加网格
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 保存图表
    output_path = os.path.join(output_dir, f'frequency_{target_word.replace(" ", "_")}.png')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    
    return output_path

def main():
    if len(sys.argv) < 2:
        print("使用方法: python analyze_word.py <要分析的词语>")
        print("例如: python analyze_word.py 'artificial intelligence'")
        sys.exit(1)
    
    # 获取要分析的词语
    target_word = sys.argv[1]
    
    # 设置数据目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "output")
    output_dir = os.path.join(script_dir, "analysis_results")
    
    # 加载文章
    articles = load_articles(data_dir)
    
    # 分析词频
    monthly_counts, total_count, articles_count = analyze_word_frequency(articles, target_word)
    
    # 打印统计结果
    print(f"\n分析结果:")
    print(f"词语 '{target_word}' 的统计信息:")
    print(f"- 总出现次数: {total_count}")
    print(f"- 出现该词的文章数: {articles_count}")
    print(f"- 平均每篇文章出现次数: {total_count/articles_count:.2f}")
    
    # 按月份打印详细统计
    print("\n月度分布:")
    for month in sorted(monthly_counts.keys()):
        count = monthly_counts[month]
        print(f"{month}: {count}次")
    
    # 绘制分布图
    output_path = plot_frequency_distribution(monthly_counts, target_word, output_dir)
    print(f"\n频率分布图已保存至: {output_path}")

if __name__ == "__main__":
    main() 