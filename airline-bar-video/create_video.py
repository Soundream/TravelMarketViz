import os
import cv2
import glob
import argparse
import numpy as np
from tqdm import tqdm
import re

# Add argument parser
parser = argparse.ArgumentParser(description='Create video from PNG frames')
parser.add_argument('--fps', type=int, default=30, help='Frames per second (default: 30)')
parser.add_argument('--output', type=str, default='output/airline_revenue.mp4', help='Output video file path')
parser.add_argument('--quality', type=str, choices=['high', 'medium', 'low'], default='medium', 
                    help='Video quality: high, medium, or low (default: medium)')
args = parser.parse_args()

def extract_frame_number(filename):
    """提取文件名中的帧序号，用于正确排序"""
    match = re.search(r'frame_(\d+)\.png', filename)
    if match:
        return int(match.group(1))
    return 0

def create_video_from_frames():
    # Input directory containing the frames
    frames_dir = 'output/frames'
    
    # Get all PNG files in the frames directory and正确数字排序
    frame_files = glob.glob(os.path.join(frames_dir, 'frame_*.png'))
    # 使用提取的数字进行排序，而不是字符串排序
    frame_files = sorted(frame_files, key=extract_frame_number)
    
    if not frame_files:
        print(f"No frame files found in {frames_dir}")
        return
    
    print(f"Found {len(frame_files)} frame files")
    # 检查帧序列连续性
    frame_numbers = [extract_frame_number(f) for f in frame_files]
    print(f"Frame range: {min(frame_numbers)} to {max(frame_numbers)}")
    
    # 检查是否有缺失帧
    expected_frames = set(range(min(frame_numbers), max(frame_numbers) + 1))
    missing_frames = expected_frames - set(frame_numbers)
    if missing_frames:
        print(f"Warning: Found {len(missing_frames)} missing frames in the sequence")
        print(f"First few missing: {sorted(list(missing_frames))[:10]}")
    
    # Calculate FPS based on desired duration
    target_duration = 80  # seconds
    ideal_fps = len(frame_files) / target_duration
    
    # Use ideal FPS or user-specified FPS
    fps = args.fps
    estimated_duration = len(frame_files) / fps
    
    print(f"Using {fps} fps (ideal would be {ideal_fps:.2f} fps for {target_duration}s)")
    print(f"Estimated video duration: {estimated_duration:.2f} seconds")
    
    # Determine video dimensions from the first frame
    first_frame = cv2.imread(frame_files[0])
    height, width, _ = first_frame.shape
    
    # Set video codec and quality parameters
    if args.quality == 'high':
        # 使用更好的编码器，确保颜色保真度
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4V codec
        bitrate = 8000000  # 增加比特率到8Mbps
    elif args.quality == 'medium':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4V codec
        bitrate = 4000000  # 4 Mbps
    else:  # low
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4V codec
        bitrate = 2000000  # 2 Mbps
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Create VideoWriter object
    out = cv2.VideoWriter(args.output, fourcc, fps, (width, height))
    
    # Add each frame to the video
    print(f"Creating video at {width}x{height} resolution")
    for frame_file in tqdm(frame_files, desc="Processing frames"):
        # 使用BGR到RGB转换保持颜色一致性
        frame = cv2.imread(frame_file)
        if frame is not None:
            # 确保颜色正确 - OpenCV默认以BGR读取，而PNG通常是RGB
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 如果需要颜色转换
            out.write(frame)
        else:
            print(f"Warning: Could not read frame {frame_file}")
    
    # Release the VideoWriter
    out.release()
    
    # 使用ffmpeg添加额外的比特率控制（如果可用）
    try:
        import subprocess
        output_temp = args.output + ".temp.mp4"
        os.rename(args.output, output_temp)
        
        cmd = [
            'ffmpeg', '-i', output_temp, 
            '-c:v', 'libx264', '-crf', '17', 
            '-preset', 'slow', '-pix_fmt', 'yuv420p',
            args.output
        ]
        
        print("\nRunning ffmpeg to optimize video quality...")
        subprocess.run(cmd, check=True)
        os.remove(output_temp)
        print("ffmpeg processing completed successfully")
    except Exception as e:
        print(f"Warning: Could not run ffmpeg optimization: {e}")
        # 如果ffmpeg失败，恢复原始文件
        if os.path.exists(output_temp):
            os.rename(output_temp, args.output)
    
    # Print final information
    output_size_mb = os.path.getsize(args.output) / (1024 * 1024)
    print(f"\nVideo created successfully: {args.output}")
    print(f"Video size: {output_size_mb:.2f} MB")
    print(f"Duration: {len(frame_files) / fps:.2f} seconds at {fps} fps")
    print(f"Resolution: {width}x{height}")

if __name__ == "__main__":
    create_video_from_frames() 