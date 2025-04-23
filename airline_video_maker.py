import os
import argparse
import subprocess
import glob
from tqdm import tqdm

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='将生成的帧合成为视频')
    parser.add_argument('--frames-dir', type=str, default='frames', help='帧文件夹路径')
    parser.add_argument('--output', type=str, default='output/airline_revenue_animation.mp4', help='输出视频文件路径')
    parser.add_argument('--fps', type=int, default=60, help='每秒帧数 (默认: 60)')
    parser.add_argument('--quality', type=str, choices=['high', 'medium', 'low'], default='high', 
                        help='视频质量: high, medium, or low (默认: high)')
    parser.add_argument('--crf', type=int, default=None, help='FFmpeg CRF值 (15-25推荐，越低质量越高)')
    return parser.parse_args()

def get_video_settings(quality, custom_crf=None):
    """根据质量参数配置视频编码设置"""
    if custom_crf is not None:
        crf = str(max(min(custom_crf, 28), 10))  # 限制CRF在10-28之间
    elif quality == 'high':
        crf = '15'  # 高质量
        preset = 'slow'  # 慢编码以获得更好的压缩
        bitrate = '25M'  # 高比特率
    elif quality == 'medium':
        crf = '18'
        preset = 'medium'
        bitrate = '15M'
    else:  # low
        crf = '23'
        preset = 'faster'
        bitrate = '8M'
    
    # 如果指定了自定义CRF，调整其他参数
    if custom_crf is not None:
        if int(crf) < 18:
            preset = 'slow'
            bitrate = '25M'
        elif int(crf) < 22:
            preset = 'medium'
            bitrate = '15M'
        else:
            preset = 'faster'
            bitrate = '8M'
    
    # 始终使用高质量像素格式以保持颜色准确度
    pix_fmt = 'yuv444p'  # 无色度子采样，更好的颜色保存
    
    return {
        'crf': crf,
        'preset': preset,
        'bitrate': bitrate,
        'pix_fmt': pix_fmt
    }

def create_video(frames_dir, output_path, fps, video_settings):
    """使用FFmpeg创建视频"""
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 获取所有帧并按名称排序
    frames = sorted(glob.glob(os.path.join(frames_dir, 'frame_*.png')))
    
    if not frames:
        print(f"在 {frames_dir} 中未找到帧文件！")
        return False
    
    print(f"找到 {len(frames)} 个帧文件，开始创建视频...")
    
    # 创建ffmpeg命令
    command = [
        'ffmpeg', '-y',  # 覆盖输出文件（如果存在）
        '-f', 'image2',  # 输入格式
        '-framerate', str(fps),  # 帧率
        '-i', os.path.join(frames_dir, 'frame_%05.2f.png'),  # 输入模式
        '-c:v', 'libx264',  # 输出编解码器
        '-profile:v', 'high444',  # 支持yuv444p
        '-pix_fmt', video_settings['pix_fmt'],
        '-preset', video_settings['preset'],
        '-crf', video_settings['crf'],
        '-b:v', video_settings['bitrate'],
        '-movflags', '+faststart',  # 优化网络播放
        '-colorspace', 'bt709',     # 使用标准色彩空间
        '-color_primaries', 'bt709',
        '-color_trc', 'bt709',
        '-vf', 'format=yuv444p',  # 视频过滤器
        output_path
    ]
    
    # 执行命令
    try:
        print("\n执行FFmpeg命令创建视频...")
        print(" ".join(command))
        
        # 使用进度条显示处理进度
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 显示输出
        for line in iter(process.stderr.readline, b''):
            line_str = line.decode('utf-8', errors='replace').strip()
            print(line_str)
        
        process.wait()
        
        if process.returncode == 0:
            print(f"\n视频创建成功！保存在: {output_path}")
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"视频文件大小: {file_size_mb:.2f} MB")
            return True
        else:
            print("\nFFmpeg出错，视频创建失败")
            return False
            
    except Exception as e:
        print(f"\nFFmpeg错误: {e}")
        return False

def main():
    """主函数"""
    args = parse_args()
    
    # 确保帧目录存在
    if not os.path.exists(args.frames_dir):
        print(f"错误: 帧目录 '{args.frames_dir}' 不存在！")
        return False
    
    # 获取视频设置
    video_settings = get_video_settings(args.quality, args.crf)
    
    # 创建视频
    success = create_video(args.frames_dir, args.output, args.fps, video_settings)
    
    if success:
        print("视频生成成功完成！")
    else:
        print("视频生成失败。")
    
    return success

if __name__ == "__main__":
    main() 