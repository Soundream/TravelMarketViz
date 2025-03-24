import os
import cv2
import glob
import argparse
import numpy as np
import re
from tqdm import tqdm
from PIL import Image
import subprocess
import shutil
import sys

# Add argument parser
parser = argparse.ArgumentParser(description='Create video from PNG frames')
parser.add_argument('--fps', type=int, help='Frames per second (default: auto-calculated for 120 second video)')
parser.add_argument('--output', type=str, default='output/airline_revenue.mp4', help='Output video file path')
parser.add_argument('--quality', type=str, choices=['high', 'medium', 'low'], default='high', 
                    help='Video quality: high, medium, or low (default: high)')
parser.add_argument('--normalize', action='store_true', help='Normalize frame sizes if they differ')
parser.add_argument('--preserve-colors', action='store_true', default=True, 
                    help='Preserve original PNG colors (default: True)')
parser.add_argument('--auto-duration', action='store_true', default=True,
                    help='Automatically calculate FPS for longer video duration (default: True)')
parser.add_argument('--simple', action='store_true', default=True,
                    help='Use simple direct FFmpeg method (default: True)')
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

def simple_ffmpeg_video_creation(frame_files, output_path, fps):
    """使用简单直接的FFmpeg命令创建视频，最大程度保证可靠性和颜色准确性"""
    print("\n正在使用简单的FFmpeg模式创建视频...")
    
    # 检查是否安装了FFmpeg
    try:
        subprocess.check_output(['ffmpeg', '-version'], stderr=subprocess.STDOUT)
        print("FFmpeg已检测到，正在使用FFmpeg创建视频...")
    except (FileNotFoundError, subprocess.SubprocessError) as e:
        print("错误：未检测到FFmpeg。此模式需要安装FFmpeg。")
        print(f"错误详情: {str(e)}")
        return False
    
    # 准备临时目录用于顺序帧文件
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(frame_files[0])), 'temp_frames')
    os.makedirs(temp_dir, exist_ok=True)
    
    # 清空临时目录
    for f in glob.glob(os.path.join(temp_dir, '*.png')):
        try:
            os.remove(f)
        except:
            pass
    
    # 将帧文件复制到临时目录并按顺序命名
    print("正在创建顺序帧文件...")
    for i, src_file in enumerate(tqdm(frame_files, desc="处理帧")):
        dst_file = os.path.join(temp_dir, f'{i+1:04d}.png')
        try:
            # 使用PIL打开和保存图像，确保PNG格式正确
            img = Image.open(src_file)
            img.save(dst_file, format='PNG', optimize=True)
            img.close()
        except Exception as e:
            print(f"处理帧 {src_file} 时出错: {e}")
            # 如果处理失败，尝试直接复制
            try:
                shutil.copy2(src_file, dst_file)
            except:
                print(f"无法复制帧 {src_file} 到 {dst_file}")
    
    # 检查临时目录中的文件
    temp_files = sorted(glob.glob(os.path.join(temp_dir, '*.png')))
    print(f"创建了 {len(temp_files)} 个顺序文件")
    
    if not temp_files:
        print("错误：没有找到帧文件！")
        return False
    
    # 获取第一帧的尺寸信息
    try:
        first_img = Image.open(temp_files[0])
        width, height = first_img.size
        first_img.close()
        print(f"帧尺寸: {width}x{height}")
    except Exception as e:
        print(f"无法获取帧尺寸: {e}")
        return False
    
    # 设置FFmpeg命令参数
    if args.quality == 'high':
        crf = '17'
        preset = 'slow'
    elif args.quality == 'medium':
        crf = '23'
        preset = 'medium'
    else:  # low
        crf = '28'
        preset = 'fast'
    
    # 构建FFmpeg命令 - 使用最简单和最可靠的方式
    frames_pattern = os.path.join(temp_dir, '%04d.png')
    
    # 尝试使用简单命令直接创建视频
    try:
        print("正在使用FFmpeg创建视频...")
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-framerate', str(fps),
            '-i', frames_pattern,
            '-vf', f'format=yuv420p',  # 使用兼容性最好的格式
            '-c:v', 'libx264',
            '-preset', preset,
            '-crf', crf,
            output_path
        ]
        
        print(f"执行命令: {' '.join(ffmpeg_cmd)}")
        subprocess.run(ffmpeg_cmd, check=True)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
            output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"\n视频创建成功: {output_path}")
            print(f"视频大小: {output_size_mb:.2f} MB")
            print(f"时长: {len(frame_files) / fps:.2f} 秒 ({len(frame_files) / fps / 60:.2f} 分钟)")
            print(f"分辨率: {width}x{height}")
            return True
        else:
            print("警告：生成的视频文件太小或不存在，可能创建失败")
            return False
    except Exception as e:
        print(f"使用FFmpeg创建视频时出错: {e}")
        return False
    finally:
        # 清理临时文件
        print("正在清理临时文件...")
        for f in temp_files:
            try:
                os.remove(f)
            except:
                pass

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
    
    # 如果设置了自动时长且未指定fps，计算fps使视频至少为120秒
    if args.auto_duration and args.fps is None:
        target_duration = 120  # 目标2分钟时长
        fps = max(1, len(frame_files) / target_duration)  # 至少1fps
        print(f"Auto-calculated FPS: {fps:.2f} for {target_duration}s video duration")
    else:
        # 使用用户指定的fps，如果未指定则使用较低的默认值以获得更长时长
        fps = args.fps or 10  # 默认使用10fps
    
    # 计算估计视频时长
    estimated_duration = len(frame_files) / fps
    print(f"Using {fps:.2f} fps")
    print(f"Estimated video duration: {estimated_duration:.2f} seconds ({estimated_duration/60:.2f} minutes)")
    
    # 创建输出目录
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    output_path = os.path.abspath(args.output)
    
    # 使用简单模式
    if args.simple:
        if simple_ffmpeg_video_creation(frame_files, output_path, fps):
            print("\n成功使用简单模式创建视频！")
            return
        else:
            print("\n简单模式失败，尝试使用标准模式...")
    
    # 如果简单模式失败或未使用简单模式，继续使用标准流程
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
            shutil.copy2(src_file, dst_file)
    
    # 检查临时目录中的文件
    temp_files = glob.glob(os.path.join(temp_dir, '*.png'))
    print(f"Created {len(temp_files)} sequential files in {temp_dir}")
    if len(temp_files) != len(frame_files):
        print(f"WARNING: Number of temporary files ({len(temp_files)}) doesn't match number of source files ({len(frame_files)})")
    
    # 检查是否安装了FFmpeg
    try:
        subprocess.check_output(['ffmpeg', '-version'])
        has_ffmpeg = True
        print("FFmpeg detected - will use direct FFmpeg encoding for best quality")
    except (FileNotFoundError, subprocess.SubprocessError):
        has_ffmpeg = False
        print("FFmpeg not detected - will use OpenCV encoding")
    
    # 使用FFmpeg直接从图像创建视频（最可靠的方法）
    if has_ffmpeg:
        try:
            # 准备FFmpeg命令
            if args.quality == 'high':
                crf = '17'  # 更低的CRF值意味着更高质量
                preset = 'slow'
                bitrate = '12M'  # 高比特率以保持质量
            elif args.quality == 'medium':
                crf = '22'
                preset = 'medium'
                bitrate = '8M'
            else:  # low
                crf = '27'
                preset = 'fast'
                bitrate = '4M'
            
            # 使用序列化的文件命名模式
            frames_pattern = os.path.join(temp_dir, '%04d.png')
            
            # 选择编码器和像素格式，以保持原始颜色
            if args.preserve_colors:
                # 使用更高质量的像素格式以保持颜色准确性
                pix_fmt = 'yuv444p'  # 无色度子采样，更好的色彩保留
                # 对于支持的播放器，也可以使用RGB像素格式
                # pix_fmt = 'rgb24'  # 直接使用RGB，但兼容性较差
            else:
                pix_fmt = 'yuv420p'  # 标准格式，但会有色度子采样
            
            # 构建基本FFmpeg命令
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-framerate', str(fps),
                '-i', frames_pattern,
                '-c:v', 'libx264',
                '-profile:v', 'high444',  # 支持yuv444p
                '-pix_fmt', pix_fmt,
                '-preset', preset,
                '-crf', crf,
                '-b:v', bitrate,
                '-movflags', '+faststart',  # 优化网络播放
                '-colorspace', 'bt709',     # 使用标准色彩空间
                '-color_primaries', 'bt709',
                '-color_trc', 'bt709',
                output_path
            ]
            
            print(f"Running FFmpeg command: {' '.join(ffmpeg_cmd)}")
            subprocess.run(ffmpeg_cmd, check=True)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
                output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"\nVideo created successfully with FFmpeg: {output_path}")
                print(f"Video size: {output_size_mb:.2f} MB")
                print(f"Duration: {len(frame_files) / fps:.2f} seconds ({len(frame_files) / fps / 60:.2f} minutes) at {fps:.2f} fps")
                
                # 获取视频尺寸
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
    first_frame = cv2.imread(frame_files[0], cv2.IMREAD_UNCHANGED)  # 读取全部通道
    if first_frame is None:
        print(f"Error: Could not read first frame: {frame_files[0]}")
        return
    
    height, width = first_frame.shape[:2]
    channels = first_frame.shape[2] if len(first_frame.shape) > 2 else 1
    
    print(f"Frame dimensions: {width}x{height}, {channels} channels")
    
    # 使用最可靠的编码器
    # 尝试使用多种编码器，从最可靠的开始
    codecs_to_try = [
        ('H264', 'mp4'),  # H.264 编码，MP4 容器
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
                # 读取帧，保持原色
                frame = cv2.imread(frame_file, cv2.IMREAD_UNCHANGED)
                if frame is None:
                    print(f"Warning: Could not read frame {frame_file}")
                    continue
                
                # 确保帧是BGR格式（OpenCV要求）
                if len(frame.shape) > 2 and frame.shape[2] == 4:  # RGBA格式
                    # 转换RGBA到BGR，保持颜色准确性
                    # 首先转换到RGB
                    rgb = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
                    # 然后转换到BGR
                    frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                elif len(frame.shape) > 2 and frame.shape[2] == 3:  # RGB格式
                    # 转换RGB到BGR（如果需要）
                    pass  # cv2.imread默认已经是BGR
                
                out.write(frame)
            
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
    print(f"Duration: {len(frame_files) / fps:.2f} seconds ({len(frame_files) / fps / 60:.2f} minutes)")
    print(f"Resolution: {width}x{height}")

if __name__ == "__main__":
    create_video_from_frames() 