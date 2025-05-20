import sys
import os
from random import randint, uniform
import json
import glob
from datetime import datetime
import re
from pathlib import Path
from tqdm import tqdm
import builtins

import pygame
from pygame.locals import *
import Box2D
from Box2D import *
from Box2D.b2 import *

# 英文停用词列表
ENGLISH_STOP_WORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
    'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
    'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',
    'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
}

# 过滤掉的特定高频词
FILTERED_WORDS = {'travel', 'hotel', 'hotels', 'company', 'companies', 'business'}

class WordObj:
    def __init__(self, text, color=None):
        self.text = text
        self.color = color or (randint(0, 255), randint(0, 255), randint(0, 255))
        self.font = None
        self.surface = None
        self.size = 1.0
        self.update_surface()
        
    def update_surface(self):
        if not pygame.font.get_init():
            pygame.font.init()
        self.font = pygame.font.Font(None, int(32 * self.size))
        self.surface = self.font.render(self.text, True, self.color)
        rect = self.surface.get_rect()
        self.width = rect.width / 20.0  # Scale down for Box2D
        self.height = rect.height / 20.0
        self.aspect_ratio = self.width / self.height

class WordSwarm:
    def __init__(self, data_dir="output", output_dir="animation_results"):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.articles = []
        self.word_frequencies = {}
        self.dates = []
        
        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(output_dir, "frames")).mkdir(parents=True, exist_ok=True)
        
        # 初始化PyGame和Box2D
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080))
        pygame.display.set_caption("WordSwarm")
        
        # 创建Box2D世界
        self.world = b2World(gravity=(0, 0))
        
        # 动画相关参数
        self.frequency = 0.1
        self.damping = 2
        self.max_size = 5
        self.min_size = 0.1
        
        # 存储单词对象
        self.word_objects = []
        self.bodies = []
        self.joints = []
        self.suns = []
        
    def load_data(self):
        """从JSON文件加载文章数据"""
        json_files = glob.glob(os.path.join(self.data_dir, "phocuswire_page_*.json"))
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
        self.articles = all_articles
        return all_articles

    def process_articles(self):
        """处理文章数据，提取关键词频率"""
        word_freq_by_date = {}
        dates = set()
        
        for article in tqdm(self.articles, desc="处理文章"):
            try:
                date_str = article.get('date')
                if not date_str:
                    continue
                    
                date_obj = self.parse_date(date_str)
                if not date_obj:
                    continue
                
                # 将日期转换为年月格式
                year_month = date_obj.strftime("%Y-%m")
                dates.add(year_month)
                
                # 预处理文章内容
                content = article.get('content', '')
                words = self.preprocess_text(content)
                
                # 更新词频
                if year_month not in word_freq_by_date:
                    word_freq_by_date[year_month] = {}
                
                for word in words:
                    word_freq_by_date[year_month][word] = word_freq_by_date[year_month].get(word, 0) + 1
                    
            except Exception as e:
                print(f"处理文章时出错: {e}")
        
        self.word_frequencies = word_freq_by_date
        self.dates = sorted(list(dates))
        
    def create_animation(self, top_n=50):
        """创建基于物理引擎的词云动画"""
        if not self.word_frequencies or not self.dates:
            print("请先运行 process_articles() 方法")
            return
            
        # 获取所有时间点的前N个关键词
        all_words = set()
        for date in self.dates:
            words = sorted(self.word_frequencies[date].items(), 
                         key=lambda x: x[1], 
                         reverse=True)[:top_n]
            all_words.update([w[0] for w in words])
            
        # 创建单词对象
        for word in all_words:
            word_obj = WordObj(word)
            self.word_objects.append(word_obj)
            
            # 创建物理体
            body = self.world.CreateDynamicBody(
                position=(uniform(-30, 30), uniform(-20, 20)),
                fixtures=b2FixtureDef(
                    shape=b2PolygonShape(box=(word_obj.width/2, word_obj.height/2)),
                    density=1.0,
                    friction=0.3,
                    restitution=0.5
                )
            )
            self.bodies.append(body)
            
            # 创建"太阳"（固定点）
            sun = self.world.CreateStaticBody(
                position=(uniform(-25, 25), 0)
            )
            self.suns.append(sun)
            
            # 创建弹簧关节
            joint = self.world.CreateDistanceJoint(
                bodyA=sun,
                bodyB=body,
                anchorA=sun.position,
                anchorB=body.position,
                frequencyHz=self.frequency,
                dampingRatio=self.damping,
                length=0.5
            )
            self.joints.append(joint)
            
        # 动画循环
        clock = pygame.time.Clock()
        frame_count = 0
        
        running = True
        while running and frame_count < len(self.dates) * 30:  # 30帧/日期
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    
            # 清屏
            self.screen.fill((0, 0, 0))
            
            # 更新物理世界
            self.world.Step(1.0/60.0, 6, 2)
            
            # 计算当前日期索引
            date_idx = frame_count // 30
            if date_idx >= len(self.dates):
                break
            current_date = self.dates[date_idx]
            
            # 更新单词大小
            current_freqs = self.word_frequencies[current_date]
            max_freq = builtins.max(current_freqs.values()) if current_freqs else 1
            
            for i, word_obj in enumerate(self.word_objects):
                freq = current_freqs.get(word_obj.text, 0)
                target_size = self.min_size + (self.max_size - self.min_size) * (freq / max_freq)
                word_obj.size = target_size
                word_obj.update_surface()
                
                # 更新物理体大小
                body = self.bodies[i]
                fixture = body.fixtures[0]
                body.DestroyFixture(fixture)
                body.CreateFixture(
                    shape=b2PolygonShape(box=(word_obj.width * target_size / 2, 
                                            word_obj.height * target_size / 2)),
                    density=1.0,
                    friction=0.3,
                    restitution=0.5
                )
                
                # 绘制单词
                pos = body.position
                screen_pos = (int(pos.x * 20 + self.screen.get_width()/2),
                            int(-pos.y * 20 + self.screen.get_height()/2))
                self.screen.blit(word_obj.surface, screen_pos)
            
            # 绘制日期和进度条
            font = pygame.font.Font(None, 36)
            date_surface = font.render(current_date, True, (255, 255, 255))
            self.screen.blit(date_surface, (50, 50))
            
            # 保存帧
            pygame.image.save(self.screen, 
                            os.path.join(self.output_dir, "frames", f"frame_{frame_count:04d}.png"))
            
            pygame.display.flip()
            clock.tick(60)
            frame_count += 1
            
        pygame.quit()
        
        # 使用ffmpeg合成视频
        output_path = os.path.join(self.output_dir, 'word_swarm.mp4')
        cmd = f"ffmpeg -y -framerate 30 -i {os.path.join(self.output_dir, 'frames', 'frame_%04d.png')} " \
              f"-c:v libx264 -pix_fmt yuv420p -crf 18 {output_path}"
        os.system(cmd)
        
        print(f"动画已保存至: {output_path}")
        
    def parse_date(self, date_str):
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
    
    def preprocess_text(self, text):
        """预处理文本"""
        if not text:
            return []
            
        # 移除非字母字符
        text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
        
        # 分词
        words = [word.strip() for word in text.split() if word.strip()]
        
        # 移除停用词、短词和特定过滤词
        words = [word for word in words if word not in ENGLISH_STOP_WORDS 
                and word not in FILTERED_WORDS 
                and len(word) > 2]
        
        return words

if __name__ == "__main__":
    # 创建WordSwarm实例
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "animation_results")
    
    swarm = WordSwarm(data_dir=data_dir, output_dir=output_dir)
    
    # 加载和处理数据
    swarm.load_data()
    swarm.process_articles()
    
    # 创建动画
    swarm.create_animation(top_n=50) 