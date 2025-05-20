import os
import subprocess
from pathlib import Path
import argparse

def create_video(frames_dir, output_path, fps=30, crf=18, preset='slow', bitrate='20M'):
    """
    将图片帧合成为高质量视频
    
    参数:
    frames_dir: 包含帧图片的目录
    output_path: 输出视频的路径
    fps: 帧率
    crf: 视频质量（0-51，越小质量越好，18是视觉无损）
    preset: 编码预设（slower/slow/medium/fast/faster）
    bitrate: 视频比特率
    """
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 构建ffmpeg命令
    cmd = [
        'ffmpeg',
        '-y',  # 覆盖已存在的文件
        '-framerate', str(fps),
        '-i', os.path.join(frames_dir, 'frame_%04d.png'),
        
        # 视频过滤器
        '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',  # 确保尺寸是2的倍数
        
        # 视频编码设置
        '-c:v', 'libx264',  # 使用H.264编码器
        '-preset', preset,  # 编码速度预设
        '-crf', str(crf),  # 质量控制
        '-b:v', bitrate,  # 比特率
        '-maxrate', bitrate,  # 最大比特率
        '-bufsize', '40M',  # 缓冲区大小
        
        # 高级编码设置
        '-profile:v', 'high',  # 使用high profile
        '-level', '4.2',  # 兼容性级别
        '-pix_fmt', 'yuv420p',  # 像素格式
        '-movflags', '+faststart',  # 支持快速开始播放
        
        # 其他设置
        '-threads', 'auto',  # 自动选择线程数
        '-hide_banner',  # 隐藏ffmpeg标语
        
        output_path
    ]
    
    print("开始生成视频...")
    print(f"使用参数:")
    print(f"- 帧率: {fps} fps")
    print(f"- 质量: CRF {crf}")
    print(f"- 编码预设: {preset}")
    print(f"- 目标比特率: {bitrate}")
    
    try:
        # 运行ffmpeg命令
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # 实时输出进度
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # 获取返回码
        return_code = process.poll()
        
        if return_code == 0:
            print(f"\n✅ 视频生成成功！")
            print(f"保存至: {output_path}")
            
            # 获取视频文件大小
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"文件大小: {size_mb:.1f} MB")
        else:
            print(f"\n❌ 视频生成失败，错误代码: {return_code}")
            
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='将图片帧合成为高质量视频')
    parser.add_argument('--frames-dir', type=str, 
                       default='animation_results/frames',
                       help='包含帧图片的目录路径')
    parser.add_argument('--output', type=str, 
                       default='animation_results/word_swarm_final.mp4',
                       help='输出视频的路径')
    parser.add_argument('--fps', type=int, default=30,
                       help='视频帧率')
    parser.add_argument('--crf', type=int, default=18,
                       help='视频质量（0-51，越小质量越好，18是视觉无损）')
    parser.add_argument('--preset', type=str, default='slow',
                       choices=['ultrafast', 'superfast', 'veryfast', 'faster', 
                               'fast', 'medium', 'slow', 'slower', 'veryslow'],
                       help='编码速度预设')
    parser.add_argument('--bitrate', type=str, default='20M',
                       help='视频比特率')
    
    args = parser.parse_args()
    
    # 确保路径是相对于脚本所在目录的
    script_dir = os.path.dirname(os.path.abspath(__file__))
    frames_dir = os.path.join(script_dir, args.frames_dir)
    output_path = os.path.join(script_dir, args.output)
    
    # 创建视频
    create_video(
        frames_dir=frames_dir,
        output_path=output_path,
        fps=args.fps,
        crf=args.crf,
        preset=args.preset,
        bitrate=args.bitrate
    )

if __name__ == '__main__':
    main() 