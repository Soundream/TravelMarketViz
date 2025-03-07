import cv2
import os
import glob
from tqdm import tqdm
import argparse

def create_video_from_frames(frames_dir='output/frames', output_path='output/evolution_of_online_travel.mp4', fps=16, publish=False):
    """
    Create a video from PNG frames
    
    Args:
        frames_dir (str): Directory containing the PNG frames
        output_path (str): Path where the output video will be saved
        fps (int): Frames per second for the output video
        publish (bool): Whether to use high quality settings for publishing
    """
    # Get all PNG files in the frames directory and sort them properly
    frames = glob.glob(os.path.join(frames_dir, 'frame_*.png'))
    # Sort frames by their number to ensure correct order
    frames.sort(key=lambda x: int(x.split('frame_')[-1].split('.png')[0]))
    
    if not frames:
        print(f"No frames found in {frames_dir}")
        return
    
    # Print frame number range for debugging
    frame_numbers = [int(f.split('frame_')[-1].split('.png')[0]) for f in frames]
    print(f"\nFrame number range: {min(frame_numbers)} to {max(frame_numbers)}")
    print(f"Total frames found: {len(frames)}")
    
    # Find the most common frame dimensions
    print("\nAnalyzing frame dimensions...")
    dimensions = {}
    for frame_path in tqdm(frames, desc="Checking frame dimensions"):
        frame = cv2.imread(frame_path)
        if frame is not None:
            h, w = frame.shape[:2]
            dimensions[(w, h)] = dimensions.get((w, h), 0) + 1
    
    if not dimensions:
        print("Error: No valid frames found")
        return
        
    # Use the most common dimensions
    target_width, target_height = max(dimensions.items(), key=lambda x: x[1])[0]
    print(f"\nMost common frame dimensions: {target_width}x{target_height} ({dimensions[(target_width, target_height)]} frames)")
    
    # Set video quality parameters based on mode
    if publish:
        fps = 96  # Increased from 48 to 96 for even smoother playback
        bitrate = 12000000  # Increased to 12 Mbps for higher quality
    else:
        fps = 16   # Increased from 8 to 16 for smoother preview
        bitrate = 4000000  # Increased to 4 Mbps for better preview quality
    
    # Try different codecs in order of preference
    codecs = [
        ('avc1', '.mp4'),  # H.264 codec
        ('mp4v', '.mp4'),  # Default MP4 codec
        ('XVID', '.avi'),  # XVID codec (more compatible)
    ]
    
    out = None
    for codec, ext in codecs:
        try:
            # Update output path with correct extension and mode
            base_path = os.path.splitext(output_path)[0]
            current_output = f"{base_path}_{'publish' if publish else 'preview'}{ext}"
            
            # Try to create VideoWriter with current codec
            fourcc = cv2.VideoWriter_fourcc(*codec)
            test_out = cv2.VideoWriter(
                current_output, 
                fourcc, 
                fps, 
                (target_width, target_height),
                True  # isColor
            )
            
            if test_out.isOpened():
                out = test_out
                output_path = current_output
                print(f"\nUsing {codec} codec with {'high' if publish else 'standard'} quality settings")
                break
            else:
                test_out.release()
        except Exception as e:
            print(f"\nCodec {codec} failed: {e}")
            continue
    
    if out is None:
        print("Error: Could not find a working codec")
        return
    
    print(f"\nCreating video from {len(frames)} frames...")
    print(f"Mode: {'Publishing (High Quality)' if publish else 'Preview (Standard Quality)'}")
    print(f"FPS: {fps}")
    print(f"Bitrate: {bitrate/1000000:.1f} Mbps")
    print(f"Output resolution: {target_width}x{target_height}")
    
    # Write frames to video with progress bar
    skipped_frames = 0
    resized_frames = 0
    for frame_path in tqdm(frames, desc="Processing frames"):
        frame = cv2.imread(frame_path)
        if frame is None:
            print(f"\nWarning: Could not read frame: {frame_path}")
            skipped_frames += 1
            continue
            
        # Resize frame if dimensions don't match
        h, w = frame.shape[:2]
        if h != target_height or w != target_width:
            frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
            resized_frames += 1
            
        out.write(frame)
    
    # Release the video writer
    out.release()
    
    if skipped_frames > 0:
        print(f"\nWarning: Skipped {skipped_frames} frames due to errors")
    if resized_frames > 0:
        print(f"\nInfo: Resized {resized_frames} frames to match target dimensions")
    
    print(f"\nVideo created successfully at: {output_path}")
    print(f"Video properties:")
    print(f"- Resolution: {target_width}x{target_height}")
    print(f"- FPS: {fps}")
    print(f"- Total frames processed: {len(frames) - skipped_frames}")
    print(f"- Duration: {(len(frames) - skipped_frames)/fps:.2f} seconds")
    print(f"- Quality: {'High (Publishing)' if publish else 'Standard (Preview)'}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create video from frames')
    parser.add_argument('--publish', action='store_true', help='Generate high quality version for publishing')
    args = parser.parse_args()
    
    create_video_from_frames(publish=args.publish)  