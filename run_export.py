#!/usr/bin/env python
import os
import subprocess
import argparse
import webbrowser
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Run airline revenue visualization export')
    parser.add_argument('--format', type=str, choices=['png', 'mp4', 'both'], default='both',
                        help='Output format: png, mp4, or both (default: both)')
    parser.add_argument('--frames-dir', type=str, default='output/frames',
                        help='Directory to save PNG frames (default: output/frames)')
    parser.add_argument('--video-path', type=str, default='output/airline_revenue_video.mp4',
                        help='Path to save MP4 video (default: output/airline_revenue_video.mp4)')
    parser.add_argument('--frames-per-year', type=int, default=4,
                        help='Number of frames per year (default: 4 for quarterly data)')
    parser.add_argument('--height', type=int, default=800,
                        help='Height of visualization in pixels (default: 800)')
    parser.add_argument('--width', type=int, default=1200,
                        help='Width of visualization in pixels (default: 1200)')
    parser.add_argument('--max-airlines', type=int, default=15,
                        help='Maximum number of airlines to display (default: 15)')
    parser.add_argument('--fps', type=int, default=2,
                        help='Frames per second for video (default: 2)')
    args = parser.parse_args()
    
    # Create output directories if they don't exist
    frames_dir = Path(args.frames_dir)
    video_dir = Path(args.video_path).parent
    
    frames_dir.mkdir(parents=True, exist_ok=True)
    video_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Running airline revenue visualization export...")
    print(f"Format: {args.format}")
    print(f"Frames directory: {args.frames_dir}")
    print(f"Video path: {args.video_path}")
    
    # Build command to run the export script
    cmd = [
        "python3", "airline_plotly_export.py",
        "--output-dir", args.frames_dir,
        "--output-video", args.video_path,
        "--frames-per-year", str(args.frames_per_year),
        "--height", str(args.height),
        "--width", str(args.width),
        "--max-airlines", str(args.max_airlines),
        "--fps", str(args.fps),
        "--format", args.format
    ]
    
    # Run the export script
    try:
        subprocess.run(cmd, check=True)
        
        # Show success message
        if args.format in ['mp4', 'both']:
            print(f"\nVideo created successfully at: {args.video_path}")
        
        if args.format in ['png', 'both']:
            print(f"\nFrames saved successfully to: {args.frames_dir}")
            print(f"Total frames: {len(list(frames_dir.glob('*.png')))}")
            
    except subprocess.CalledProcessError as e:
        print(f"\nError running export script: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 