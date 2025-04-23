#!/usr/bin/env python
import os
import argparse
import subprocess
import time
import sys

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='航空公司收入数据可视化生成工具')
    parser.add_argument('--frames-per-year', type=int, default=300, 
                        help='每年生成的帧数 (默认: 300，越大越流畅)')
    parser.add_argument('--output-dir', type=str, default='frames', 
                        help='帧输出目录 (默认: frames)')
    parser.add_argument('--video-output', type=str, default='output/airline_revenue_animation.mp4', 
                        help='最终视频输出路径 (默认: output/airline_revenue_animation.mp4)')
    parser.add_argument('--fps', type=int, default=60, 
                        help='视频帧率 (默认: 60)')
    parser.add_argument('--quality', type=str, choices=['high', 'medium', 'low'], default='high', 
                        help='视频质量: high, medium, or low (默认: high)')
    parser.add_argument('--dpi', type=int, default=108, 
                        help='输出帧的DPI (默认: 108)')
    parser.add_argument('--only-frames', action='store_true', 
                        help='仅生成帧，不制作视频')
    parser.add_argument('--only-video', action='store_true', 
                        help='仅从现有帧制作视频，不生成新帧')
    parser.add_argument('--clean', action='store_true', 
                        help='生成视频后删除帧文件以节省空间')
    return parser.parse_args()

def run_command(cmd, description):
    """运行外部命令并显示进度"""
    print(f"\n执行: {description}")
    print(f"命令: {' '.join(cmd)}")
    
    start_time = time.time()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    # 显示输出
    for line in iter(process.stdout.readline, b''):
        line_str = line.decode('utf-8', errors='replace').strip()
        print(line_str)
    
    # 等待进程完成
    process.wait()
    
    elapsed_time = time.time() - start_time
    
    if process.returncode == 0:
        print(f"\n{description}成功完成！用时: {elapsed_time:.2f}秒")
        return True
    else:
        print(f"\n{description}失败。退出代码: {process.returncode}")
        return False

def generate_frames(args):
    """生成可视化帧"""
    cmd = [
        "python3", "airline_frame_generator.py",
        "--frames-per-year", str(args.frames_per_year),
        "--output-dir", args.output_dir,
        "--dpi", str(args.dpi)
    ]
    
    return run_command(cmd, "生成可视化帧")

def create_video(args):
    """从帧创建视频"""
    cmd = [
        "python3", "airline_video_maker.py",
        "--frames-dir", args.output_dir,
        "--output", args.video_output,
        "--fps", str(args.fps),
        "--quality", args.quality
    ]
    
    return run_command(cmd, "生成视频")

def clean_frames(frames_dir):
    """删除帧文件以节省空间"""
    import glob
    
    frames = glob.glob(os.path.join(frames_dir, "frame_*.png"))
    frames_count = len(frames)
    
    if frames_count == 0:
        print(f"在 {frames_dir} 中未找到帧文件")
        return True
    
    print(f"\n清理 {frames_count} 个帧文件以节省空间...")
    
    try:
        for frame in frames:
            os.remove(frame)
        print(f"成功删除 {frames_count} 个帧文件")
        return True
    except Exception as e:
        print(f"清理帧文件时出错: {e}")
        return False

def main():
    """主函数"""
    args = parse_args()
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.dirname(args.video_output), exist_ok=True)
    
    # 处理流程
    success = True
    
    if not args.only_video:
        print("\n===== 步骤 1: 生成可视化帧 =====")
        success = generate_frames(args)
    
    if success and not args.only_frames:
        print("\n===== 步骤 2: 创建视频 =====")
        success = create_video(args)
    
    if success and args.clean and not args.only_frames:
        print("\n===== 步骤 3: 清理帧文件 =====")
        clean_frames(args.output_dir)
    
    if success:
        if not args.only_frames:
            video_size_mb = os.path.getsize(args.video_output) / (1024 * 1024)
            print(f"\n完成！视频已保存在 {args.video_output} (大小: {video_size_mb:.2f} MB)")
        else:
            print(f"\n完成！帧已保存在 {args.output_dir} 目录")
    else:
        print("\n处理过程中发生错误，请检查上面的日志")
        sys.exit(1)

if __name__ == "__main__":
    main() 