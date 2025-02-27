import cv2
import os
import glob
from tqdm import tqdm

def create_video_from_frames(frames_dir='output/frames', output_path='output/evolution_of_online_travel.mp4', fps=8):
    """
    Create a video from PNG frames
    
    Args:
        frames_dir (str): Directory containing the PNG frames
        output_path (str): Path where the output video will be saved
        fps (int): Frames per second for the output video (lower fps = slower video)
    """
    # Get all PNG files in the frames directory
    frames = sorted(glob.glob(os.path.join(frames_dir, 'frame_*.png')))
    
    if not frames:
        print(f"No frames found in {frames_dir}")
        return
    
    # Read the first frame to get dimensions
    first_frame = cv2.imread(frames[0])
    height, width, layers = first_frame.shape
    
    # Try different codecs in order of preference
    codecs = [
        ('avc1', '.mp4'),  # H.264 codec
        ('mp4v', '.mp4'),  # Default MP4 codec
        ('XVID', '.avi'),  # XVID codec (more compatible)
    ]
    
    out = None
    for codec, ext in codecs:
        try:
            # Update output path with correct extension
            current_output = os.path.splitext(output_path)[0] + ext
            
            # Try to create VideoWriter with current codec
            fourcc = cv2.VideoWriter_fourcc(*codec)
            test_out = cv2.VideoWriter(current_output, fourcc, fps, (width, height))
            
            # If VideoWriter is created successfully, use this codec
            if test_out.isOpened():
                out = test_out
                output_path = current_output
                print(f"Using {codec} codec")
                break
            else:
                test_out.release()
        except Exception as e:
            print(f"Codec {codec} failed: {e}")
            continue
    
    if out is None:
        print("Error: Could not find a working codec")
        return
    
    print(f"\nCreating video from {len(frames)} frames...")
    
    # Write frames to video
    for frame_path in tqdm(frames, desc="Processing frames"):
        frame = cv2.imread(frame_path)
        # No color space conversion needed
        out.write(frame)
    
    # Release the video writer
    out.release()
    print(f"\nVideo created successfully at: {output_path}")
    print(f"Video properties:")
    print(f"- Resolution: {width}x{height}")
    print(f"- FPS: {fps}")
    print(f"- Total frames: {len(frames)}")
    print(f"- Duration: {len(frames)/fps:.2f} seconds")

if __name__ == "__main__":
    # You can adjust the fps here to control video speed
    # Lower fps = slower video
    # fps=8  -> about 4x slower than normal
    # fps=12 -> about 2x slower than normal
    # fps=24 -> normal speed
    create_video_from_frames(fps=8)  # Using 8 fps for slower playback  