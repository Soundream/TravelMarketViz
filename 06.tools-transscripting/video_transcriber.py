import os
import json
from datetime import datetime
import whisper
from moviepy.editor import VideoFileClip

def extract_audio_from_video(video_path, audio_path):
    """Extract audio from video file"""
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)
    audio.close()
    video.close()

def transcribe_audio(audio_path, model_name="base"):
    """Transcribe audio using Whisper"""
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path)
    return result

def process_video(video_path, output_dir):
    """Process a video file and generate JSON output"""
    os.makedirs(output_dir, exist_ok=True)
    
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = os.path.join(output_dir, f"{video_name}.wav")
    json_path = os.path.join(output_dir, f"{video_name}.json")
    
    # Extract audio
    print(f"Extracting audio from {video_path}...")
    extract_audio_from_video(video_path, audio_path)
    
    # Transcribe audio
    print("Transcribing audio...")
    transcription = transcribe_audio(audio_path)
    
    # Format output
    output = [{
        "title": video_name,
        "url": video_path,
        "date": datetime.now().strftime("%B %d, %Y"),
        "content": transcription["text"],
    }]
    
    # Save to JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # Clean up audio file
    os.remove(audio_path)
    
    print(f"Transcription saved to {json_path}")

def process_directory(input_dir, output_dir):
    """Process all MP4 files in a directory"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each MP4 file
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.mp4'):
            video_path = os.path.join(input_dir, filename)
            process_video(video_path, output_dir)

if __name__ == "__main__":
    # Example usage
    input_dir = "input_videos"  
    output_dir = "output"       # Directory for JSON output
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all videos in the input directory
    process_directory(input_dir, output_dir) 