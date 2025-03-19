import os
import cv2
import glob
import argparse
import numpy as np
import re
from tqdm import tqdm
from PIL import Image

# Add argument parser
parser = argparse.ArgumentParser(description='Create video from PNG frames')
parser.add_argument('--fps', type=int, default=30, help='Frames per second (default: 30)')
parser.add_argument('--output', type=str, default='output/airline_revenue.mp4', help='Output video file path')
parser.add_argument('--quality', type=str, choices=['high', 'medium', 'low'], default='high', 
                    help='Video quality: high, medium, or low (default: high)')
parser.add_argument('--normalize', action='store_true', help='Normalize frame sizes if they differ')
args = parser.parse_args()

def natural_sort_key(s):
    # 提取数字部分进行自然排序
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def normalize_frame_sizes(frame_files):
    """检查所有帧的尺寸并调整为一致尺寸"""
    if not frame_files:
        return frame_files
    
    print("Checking frame sizes...")
    # 检查所有帧的尺寸
    sizes = {}
    for frame_file in tqdm(frame_files, desc="Analyzing frames"):
        try:
            img = Image.open(frame_file)
            size = img.size
            if size in sizes:
                sizes[size].append(frame_file)
            else:
                sizes[size] = [frame_file]
            img.close()
        except Exception as e:
            print(f"Error analyzing frame {frame_file}: {e}")
    
    # 如果所有帧尺寸一致，不需要处理
    if len(sizes) == 1:
        print("All frames have consistent size. No normalization needed.")
        return frame_files
    
    # 找出最常见的尺寸
    most_common_size = max(sizes.items(), key=lambda x: len(x[1]))[0]
    print(f"Found {len(sizes)} different frame sizes.")
    for size, files in sizes.items():
        print(f"  Size {size}: {len(files)} frames")
    
    print(f"Normalizing all frames to the most common size: {most_common_size}")
    
    # 如果用户没有要求规范化，则询问
    if not args.normalize:
        response = input("Frames have inconsistent sizes. Normalize them? (y/n): ")
        if response.lower() != 'y':
            print("Skipping normalization. Video creation may fail or produce unexpected results.")
            return frame_files
    
    # 创建临时目录存储规范化后的帧
    norm_dir = os.path.join(os.path.dirname(frame_files[0]), 'normalized_frames')
    os.makedirs(norm_dir, exist_ok=True)
    
    # 清空规范化目录
    for f in glob.glob(os.path.join(norm_dir, '*.png')):
        try:
            os.remove(f)
        except:
            pass
    
    # 规范化所有帧尺寸
    normalized_files = []
    for i, frame_file in enumerate(tqdm(frame_files, desc="Normalizing frames")):
        base_name = os.path.basename(frame_file)
        norm_file = os.path.join(norm_dir, base_name)
        
        try:
            img = Image.open(frame_file)
            if img.size != most_common_size:
                # 调整尺寸并保持原始宽高比
                img = img.resize(most_common_size, Image.Resampling.LANCZOS)
            img.save(norm_file, format='PNG', compress_level=1)
            img.close()
            normalized_files.append(norm_file)
        except Exception as e:
            print(f"Error normalizing frame {frame_file}: {e}")
            # 如果规范化失败，使用原始帧
            normalized_files.append(frame_file)
    
    print(f"Normalized {len(normalized_files)} frames to size {most_common_size}")
    return normalized_files

def create_video_from_frames():
    # Input directory containing the frames
    frames_dir = 'output/frames'
    
    # Get all PNG files in the frames directory with correct sorting
    frame_files = glob.glob(os.path.join(frames_dir, 'frame_*.png'))
    
    if not frame_files:
        print(f"No frame files found in {frames_dir}")
        return
    
    # 使用自然排序来确保帧按正确顺序
    frame_files.sort(key=natural_sort_key)
    
    print(f"Found {len(frame_files)} frame files")
    print(f"First few frames: {[os.path.basename(f) for f in frame_files[:5]]}")
    print(f"Last few frames: {[os.path.basename(f) for f in frame_files[-5:]]}")
    
    # 检查并规范化帧尺寸
    frame_files = normalize_frame_sizes(frame_files)
    
    # Calculate FPS based on desired duration
    target_duration = 80  # seconds
    ideal_fps = len(frame_files) / target_duration
    
    # Use ideal FPS or user-specified FPS
    fps = args.fps
    estimated_duration = len(frame_files) / fps
    
    print(f"Using {fps} fps (ideal would be {ideal_fps:.2f} fps for {target_duration}s)")
    print(f"Estimated video duration: {estimated_duration:.2f} seconds")
    
    # 将帧文件重命名为顺序数字 (0001.png, 0002.png, 等)
    # 这样能确保FFmpeg读取正确的帧顺序
    temp_dir = os.path.join(os.path.dirname(frames_dir), 'temp_frames')
    os.makedirs(temp_dir, exist_ok=True)
    
    # 先清空临时目录
    for f in glob.glob(os.path.join(temp_dir, '*.png')):
        try:
            os.remove(f)
        except:
            pass
    
    print("Creating sequential frame files...")
    for i, src_file in enumerate(tqdm(frame_files)):
        dst_file = os.path.join(temp_dir, f'{i+1:04d}.png')
        # 使用硬链接或复制，避免无谓的I/O操作
        try:
            os.link(src_file, dst_file)
        except:
            # 如果硬链接失败（例如不同文件系统），则复制文件
            import shutil
            shutil.copy2(src_file, dst_file)
    
    # 检查临时目录中的文件
    temp_files = glob.glob(os.path.join(temp_dir, '*.png'))
    print(f"Created {len(temp_files)} sequential files in {temp_dir}")
    if len(temp_files) != len(frame_files):
        print(f"WARNING: Number of temporary files ({len(temp_files)}) doesn't match number of source files ({len(frame_files)})")
    
    # 检查是否安装了FFmpeg
    try:
        import subprocess
        subprocess.check_output(['ffmpeg', '-version'])
        has_ffmpeg = True
        print("FFmpeg detected - will use direct FFmpeg encoding for best quality")
    except (ImportError, FileNotFoundError, subprocess.SubprocessError):
        has_ffmpeg = False
        print("FFmpeg not detected - will use OpenCV encoding")
    
    # 使用FFmpeg直接从图像创建视频（最可靠的方法）
    if has_ffmpeg:
        try:
            # 创建输出目录
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            
            # 准备FFmpeg命令
            if args.quality == 'high':
                crf = '18'
                preset = 'slow'
            elif args.quality == 'medium':
                crf = '23'
                preset = 'medium'
            else:  # low
                crf = '28'
                preset = 'fast'
            
            # 使用序列化的文件命名模式
            frames_pattern = os.path.join(temp_dir, '%04d.png')
            output_path = os.path.abspath(args.output)
            
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-framerate', str(fps),
                '-i', frames_pattern,
                '-c:v', 'libx264',
                '-profile:v', 'high',
                '-pix_fmt', 'yuv420p', 
                '-preset', preset,
                '-crf', crf,
                output_path
            ]
            
            print(f"Running FFmpeg command: {' '.join(ffmpeg_cmd)}")
            subprocess.run(ffmpeg_cmd, check=True)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
                output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"\nVideo created successfully with FFmpeg: {output_path}")
                print(f"Video size: {output_size_mb:.2f} MB")
                print(f"Duration: {len(frame_files) / fps:.2f} seconds at {fps} fps")
                
                # 尝试获取视频尺寸
                first_frame = cv2.imread(frame_files[0])
                if first_frame is not None:
                    height, width, _ = first_frame.shape
                    print(f"Resolution: {width}x{height}")
                
                # 清理临时文件
                print("Cleaning up temporary files...")
                for f in temp_files:
                    try:
                        os.remove(f)
                    except:
                        pass
                
                return
            else:
                print(f"FFmpeg did not create a valid video (file too small or not created)")
                print("Falling back to OpenCV encoding...")
        except Exception as e:
            print(f"Error using FFmpeg: {e}")
            print("Falling back to OpenCV encoding...")
    
    # OpenCV备用方法 - 使用已经排序好的帧文件
    print("Creating video using OpenCV...")
    
    # 读取第一帧获取尺寸
    first_frame = cv2.imread(frame_files[0])
    if first_frame is None:
        print(f"Error: Could not read first frame: {frame_files[0]}")
        return
    
    height, width, _ = first_frame.shape
    
    # 使用最可靠的编码器
    # 尝试使用多种编码器，从最可靠的开始
    codecs_to_try = [
        ('mp4v', 'mp4'),  # MPEG-4 编码，最广泛支持的格式
        ('XVID', 'avi'),  # XVID 编码，AVI 容器
        ('MJPG', 'avi')   # Motion JPEG 编码，AVI 容器
    ]
    
    output_base = os.path.splitext(args.output)[0]
    success = False
    
    for codec, ext in codecs_to_try:
        try:
            temp_output = f"{output_base}.{ext}"
            print(f"Trying encoder {codec} with output {temp_output}")
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(temp_output), exist_ok=True)
            
            # 创建VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*codec)
            out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))
            
            if not out.isOpened():
                print(f"Warning: Could not open VideoWriter with codec {codec}, trying next codec")
                continue
            
            # 添加每一帧到视频
            print(f"Creating video at {width}x{height} resolution using {codec} codec")
            
            # 使用已经排序好的帧
            for frame_file in tqdm(frame_files, desc="Processing frames"):
                # 读取帧
                frame = cv2.imread(frame_file)
                if frame is not None:
                    out.write(frame)
                else:
                    print(f"Warning: Could not read frame {frame_file}")
            
            # 释放VideoWriter
            out.release()
            
            # 检查输出文件是否有效
            if os.path.exists(temp_output) and os.path.getsize(temp_output) > 100000:  # 确保文件足够大
                print(f"Successfully created video with {codec} codec")
                # 如果需要，重命名为请求的输出文件名
                if temp_output != args.output:
                    if os.path.exists(args.output):
                        os.remove(args.output)
                    os.rename(temp_output, args.output)
                
                success = True
                break
            else:
                print(f"Failed to create valid video with {codec} codec")
        except Exception as e:
            print(f"Error with {codec} codec: {e}")
    
    # 清理临时文件
    print("Cleaning up temporary files...")
    for f in temp_files:
        try:
            os.remove(f)
        except:
            pass
    
    if not success:
        print("ERROR: Failed to create video with any codec")
        return
    
    # 打印最终信息
    output_size_mb = os.path.getsize(args.output) / (1024 * 1024)
    print(f"\nVideo created successfully: {args.output}")
    print(f"Video size: {output_size_mb:.2f} MB")
    print(f"Duration: {len(frame_files) / fps:.2f} seconds at {fps} fps")
    print(f"Resolution: {width}x{height}")

if __name__ == "__main__":
    create_video_from_frames() 