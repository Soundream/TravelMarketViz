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
import math
import numpy as np  # 添加用于平滑插值

import pygame
from pygame.locals import *
import Box2D
from Box2D import *
from Box2D.b2 import *

# 英文停用词列表
ENGLISH_STOP_WORDS = {
    # 人称代词
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", 'your', 'yours', 
    'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 
    'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
    
    # 疑问词和指示词
    'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'where', 'when', 'why', 'how',
    
    # 常见动词
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing', 'can', 'could', 'should', 'would', 'shall', 'will', 'might',
    'must', 'may', 'says', 'said', 'say', 'like', 'liked', 'want', 'wants', 'wanted',
    'get', 'gets', 'got', 'make', 'makes', 'made', 'see', 'sees', 'saw', 'look', 'looks',
    'looking', 'take', 'takes', 'took', 'come', 'comes', 'came',
    
    # 介词和连词
    'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 
    'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 
    'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 
    'off', 'over', 'under', 'again', 'further', 'than',
    
    # 时间和数量词
    'now', 'then', 'once', 'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'first', 'last', 'many', 'much', 'one', 'two', 'three',
    'next', 'previous', 'today', 'tomorrow', 'yesterday', 'day', 'week', 'month', 'year',
    
    # 其他常见词
    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'too', 'very', 'just', 'well',
    'also', 'back', 'even', 'still', 'way', 'ways', 'thing', 'things', 'new', 'old',
    'good', 'better', 'best', 'bad', 'worse', 'worst', 'high', 'low', 'possible',
    'different', 'early', 'late', 'later', 'latest', 'hard', 'easy', 'earlier',
    
    # 缩写和常见组合
    "don't", 'cant', "can't", 'wont', "won't", "isn't", "aren't", "wasn't", "weren't",
    "hasn't", "haven't", "hadn't", "doesn't", "don't", "didn't", "shouldn't", "wouldn't",
    "couldn't", "mustn't", "mightn't", "shan't", 'let', "let's", 'lets',
}

# 过滤掉的特定高频词
FILTERED_WORDS = {
    'travel', 'hotel', 'hotels', 'company', 'companies', 'business', 'million', 'billion',
    'market', 'markets', 'year', 'years', 'month', 'months', 'week', 'weeks', 'day', 'days',
    'time', 'times', 'report', 'reported', 'according', 'says', 'said', 'say', 'told',
    'announced', 'launched', 'based', 'include', 'includes', 'including', 'included',
    'percent', 'percentage', 'number', 'numbers', 'group', 'groups', 'service', 'services',
    'use', 'used', 'using', 'provide', 'provides', 'provided', 'providing', 'make', 'makes',
    'made', 'making', 'set', 'sets', 'setting', 'need', 'needs', 'needed', 'needing',
    'work', 'works', 'working', 'worked', 'call', 'calls', 'called', 'calling',
    'find', 'finds', 'finding', 'found', 'show', 'shows', 'showed', 'shown', 'showing',
    'think', 'thinks', 'thinking', 'thought', 'way', 'ways', 'thing', 'things',
    'people', 'person', 'world', 'global', 'international', 'domestic', 'local',
    'industry', 'industries', 'sector', 'sectors', 'customer', 'customers',
    'data', 'information', 'technology', 'technologies', 'platform', 'platforms',
    'solution', 'solutions', 'system', 'systems', 'product', 'products',
    'place', 'places', 'area', 'areas', 'region', 'regions', 'country', 'countries',
    'city', 'cities', 'state', 'states', 'part', 'parts', 'end', 'ends', 'start', 'starts',
    'level', 'levels', 'rate', 'rates', 'value', 'values', 'price', 'prices',
    'cost', 'costs', 'revenue', 'revenues', 'sale', 'sales', 'growth', 'increase',
    'decrease', 'change', 'changes', 'changed', 'changing', 'development', 'developments',
    'plan', 'plans', 'planned', 'planning', 'strategy', 'strategies', 'strategic',
    'operation', 'operations', 'operating', 'operated', 'management', 'managing',
    'managed', 'manager', 'managers', 'executive', 'executives', 'director', 'directors',
    'leader', 'leaders', 'leadership', 'team', 'teams', 'staff', 'employee', 'employees',
    'partner', 'partners', 'partnership', 'partnerships', 'client', 'clients',
    'user', 'users', 'consumer', 'consumers', 'visitor', 'visitors', 'guest', 'guests',
    'passenger', 'passengers', 'traveler', 'travelers', 'tourist', 'tourists',
    'booking', 'bookings', 'booked', 'reservation', 'reservations', 'reserved',
    'flight', 'flights', 'airline', 'airlines', 'airport', 'airports',
    'destination', 'destinations', 'location', 'locations', 'site', 'sites',
    'property', 'properties', 'room', 'rooms', 'accommodation', 'accommodations',
    'tour', 'tours', 'trip', 'trips', 'experience', 'experiences', 'experienced',
    'offer', 'offers', 'offered', 'offering', 'deal', 'deals', 'option', 'options',
    'feature', 'features', 'featured', 'featuring', 'support', 'supports', 'supported',
    'supporting', 'help', 'helps', 'helped', 'helping', 'create', 'creates', 'created',
    'creating', 'build', 'builds', 'building', 'built', 'develop', 'develops',
    'developed', 'developing', 'launch', 'launches', 'launched', 'launching',
    'implement', 'implements', 'implemented', 'implementing', 'introduce', 'introduces',
    'introduced', 'introducing', 'bring', 'brings', 'bringing', 'brought',
}

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
        
        # 初始化PyGame（使用离屏渲染）
        pygame.init()
        os.environ['SDL_VIDEODRIVER'] = 'dummy'  # 使用虚拟显示
        self.screen = pygame.Surface((1920, 1080))
        
        # 创建Box2D世界 - 调整重力为向中心
        self.world = b2World(gravity=(0, 0))
        
        # 动画相关参数 - 调整以获得更好的效果
        self.frequency = 0.5  # 增加频率使运动更快
        self.damping = 1.0   # 减小阻尼使运动更流畅
        self.max_size = 3.0  # 调整最大尺寸
        self.min_size = 0.5  # 调整最小尺寸
        self.transition_frames = 30  # 过渡帧数
        
        # 中心点坐标（屏幕中心）
        self.center_x = 0
        self.center_y = 0
        
        # 存储单词对象和它们的目标状态
        self.word_objects = []
        self.bodies = []
        self.joints = []
        self.center_body = None
        self.target_sizes = {}  # 存储目标大小
        
        # 设置中心引力场
        self.setup_center_gravity()

    def setup_center_gravity(self):
        """设置中心引力场"""
        # 创建中心锚点
        self.center_body = self.world.CreateStaticBody(
            position=(self.center_x, self.center_y)
        )

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
        
    def interpolate_sizes(self, current_freqs, next_freqs, progress):
        """在两个时间点之间平滑插值词频"""
        sizes = {}
        max_current = builtins.max(current_freqs.values()) if current_freqs else 1
        max_next = builtins.max(next_freqs.values()) if next_freqs else 1
        
        for word in set(current_freqs.keys()) | set(next_freqs.keys()):
            current_freq = current_freqs.get(word, 0)
            next_freq = next_freqs.get(word, 0)
            
            # 使用平滑插值
            current_size = self.min_size + (self.max_size - self.min_size) * (current_freq / max_current)
            next_size = self.min_size + (self.max_size - self.min_size) * (next_freq / max_next)
            
            # 使用三次方插值使过渡更平滑
            t = progress
            t = t * t * (3 - 2 * t)  # 平滑插值函数
            sizes[word] = current_size * (1 - t) + next_size * t
            
        return sizes

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
            
        # 创建单词对象（初始布局）
        radius = 15.0
        angle_step = 2 * math.pi / len(all_words)
        
        for i, word in enumerate(all_words):
            angle = angle_step * i
            init_x = self.center_x + radius * math.cos(angle)
            init_y = self.center_y + radius * math.sin(angle)
            
            word_obj = WordObj(word)
            self.word_objects.append(word_obj)
            
            body = self.world.CreateDynamicBody(
                position=(init_x, init_y),
                linearDamping=0.8,
                angularDamping=0.9,
                fixtures=b2FixtureDef(
                    shape=b2PolygonShape(box=(word_obj.width/2, word_obj.height/2)),
                    density=1.0,
                    friction=0.3,
                    restitution=0.1
                )
            )
            self.bodies.append(body)
            
            joint = self.world.CreateDistanceJoint(
                bodyA=self.center_body,
                bodyB=body,
                anchorA=self.center_body.position,
                anchorB=body.position,
                frequencyHz=self.frequency,
                dampingRatio=self.damping,
                length=radius
            )
            self.joints.append(joint)
            
        # 动画循环
        frame_count = 0
        total_frames = (len(self.dates) - 1) * self.transition_frames
        
        print("正在生成动画帧...")
        for frame in tqdm(range(total_frames)):
            # 计算当前日期索引和过渡进度
            date_idx = frame // self.transition_frames
            next_date_idx = builtins.min(date_idx + 1, len(self.dates) - 1)
            progress = (frame % self.transition_frames) / self.transition_frames
            
            current_date = self.dates[date_idx]
            next_date = self.dates[next_date_idx]
            
            # 获取当前和下一个时间点的频率
            current_freqs = self.word_frequencies[current_date]
            next_freqs = self.word_frequencies[next_date]
            
            # 计算插值后的大小
            interpolated_sizes = self.interpolate_sizes(current_freqs, next_freqs, progress)
            
            # 清屏
            self.screen.fill((0, 0, 0))
            
            # 更新物理世界
            self.world.Step(1.0/60.0, 8, 3)
            
            # 更新和绘制每个单词
            for i, word_obj in enumerate(self.word_objects):
                # 获取插值后的大小
                target_size = interpolated_sizes.get(word_obj.text, self.min_size)
                word_obj.size = target_size
                word_obj.update_surface()
                
                # 更新物理体
                body = self.bodies[i]
                
                # 添加向中心的力
                center_force = b2Vec2(
                    self.center_x - body.position.x,
                    self.center_y - body.position.y
                )
                force_mag = target_size * 10.0  # 根据大小调整力度
                center_force.Normalize()
                center_force *= force_mag
                body.ApplyForceToCenter(center_force, True)
                
                # 更新碰撞体大小
                fixture = body.fixtures[0]
                body.DestroyFixture(fixture)
                body.CreateFixture(
                    shape=b2PolygonShape(box=(word_obj.width * target_size / 2, 
                                            word_obj.height * target_size / 2)),
                    density=1.0,
                    friction=0.3,
                    restitution=0.1
                )
                
                # 绘制单词
                pos = body.position
                screen_pos = (int(pos.x * 20 + self.screen.get_width()/2),
                            int(-pos.y * 20 + self.screen.get_height()/2))
                
                text_rect = word_obj.surface.get_rect()
                screen_pos = (screen_pos[0] - text_rect.width//2,
                            screen_pos[1] - text_rect.height//2)
                
                self.screen.blit(word_obj.surface, screen_pos)
            
            # 绘制日期（使用插值）
            font = pygame.font.Font(None, 48)
            date_text = current_date
            if progress > 0:
                date_text = f"{current_date} → {next_date}"
            date_surface = font.render(date_text, True, (255, 255, 255))
            date_rect = date_surface.get_rect()
            date_rect.topright = (self.screen.get_width() - 50, 50)
            self.screen.blit(date_surface, date_rect)
            
            # 保存帧
            pygame.image.save(self.screen, 
                            os.path.join(self.output_dir, "frames", f"frame_{frame_count:04d}.png"))
            frame_count += 1
        
        # 使用ffmpeg合成视频
        output_path = os.path.join(self.output_dir, 'word_swarm.mp4')
        cmd = (f"ffmpeg -y -framerate 30 -i {os.path.join(self.output_dir, 'frames', 'frame_%04d.png')} "
               f"-vf 'pad=ceil(iw/2)*2:ceil(ih/2)*2' "
               f"-c:v libx264 -pix_fmt yuv420p -crf 18 {output_path}")
        os.system(cmd)
        
        print(f"动画已保存至: {output_path}")
        pygame.quit()
        
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