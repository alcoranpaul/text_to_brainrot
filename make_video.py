import os
import random
import subprocess
from generate_bg_video import download_random_full_video
from pydub.utils import mediainfo  # type: ignore


VIDEO_DIR = "output/background_videos"
OUTPUT_PATH = "output/brainrot_videos"
TRIMMED_VIDEO_DIR = "output/trimmed_videos"


def get_audio_duration(audio_path):
    info = mediainfo(audio_path)
    return float(info['duration'])


def get_video_duration(video_path):
    info = mediainfo(video_path)
    return float(info['duration'])


def get_random_video(video_dir):
    video_files = [f for f in os.listdir(
        video_dir) if f.lower().endswith((".mp4", ".mov", ".mkv"))]
    if not video_files:
        user_choice = input(
            "❓ Do you want to download a YouTube video instead? (y/N): ").strip().lower()
        if user_choice == 'y':
            download_random_full_video()
            video_files = [f for f in os.listdir(
                video_dir) if f.lower().endswith((".mp4", ".mov", ".mkv"))]
        else:
            raise FileNotFoundError("No video files found in directory.")
    return os.path.join(video_dir, random.choice(video_files))


def trim_video_random(video_path, audio_duration, output_path):
    video_duration = get_video_duration(video_path)
    if audio_duration >= video_duration:
        raise ValueError("Audio is longer than video. Cannot trim.")

    max_start = video_duration - audio_duration
    start_time = round(random.uniform(0, max_start), 2)

    ffmpeg_cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-ss", str(start_time),
        "-i", video_path,
        "-t", str(audio_duration),
        "-c", "copy",
        output_path
    ]

    subprocess.run(ffmpeg_cmd, check=True)
    print(f"🎬 Trimmed video saved to {output_path}")


def make_video_with_subs(audio_path: str, subtitle_path: str, resolution="1080x1920", font_size=24, file_name=None) -> str:
    """
    Combines an audio file, subtitle file, and a randomly selected video into a final video with subtitles.

    Args:
        audio_path: Path to the audio file.
        subtitle_path: Path to the SSA subtitle file.
        resolution: The desired resolution of the output video (e.g., "1080x1920").
        font_size: The font size for the subtitles.
        file_name: The desired name for the output video file. If None, a dynamic name is generated.

    Returns:
        Path to the generated final video file, or None if an error occurred.
    """

    os.makedirs(OUTPUT_PATH, exist_ok=True)
    os.makedirs(TRIMMED_VIDEO_DIR, exist_ok=True)

    try:
        # Generate dynamic final output filename if not provided
        if file_name is None:
            base_name = "brainrot_"
            counter = 1
            while os.path.exists(os.path.join(OUTPUT_PATH, f"{base_name}{counter}.mp4")):
                counter += 1
            file_name = f"{base_name}{counter}.mp4"

        # Generate dynamic trimmed video filename
        trimmed_base = "trimmed_"
        trimmed_counter = 1

        while os.path.exists(os.path.join(TRIMMED_VIDEO_DIR, f"{trimmed_base}{trimmed_counter}.mp4")):
            trimmed_counter += 1

        trimmed_video_filename = f"{trimmed_base}{trimmed_counter}.mp4"
        trimmed_video_path = os.path.join(
            TRIMMED_VIDEO_DIR, trimmed_video_filename)

        final_output_path = os.path.join(OUTPUT_PATH, file_name)

        # Pick random video and get audio duration
        random_video = get_random_video(VIDEO_DIR)
        duration = get_audio_duration(audio_path)

        # Trim the video
        trim_video_random(random_video, duration, trimmed_video_path)

        subtitle_path = os.path.normpath(subtitle_path)

        # *** ENSURE subtitle_path is correct ***
        if not os.path.exists(subtitle_path):
            raise (f"Subtitle file not found at: {subtitle_path}")

        subtitle_path_ffmpeg = subtitle_path.replace('\\', '/')
        width, height = map(int, resolution.split('x'))

        ffmpeg_cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-i", trimmed_video_path,
            "-i", audio_path,
            "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-vf", f"scale=-1:{height},crop={width}:{height},subtitles='{subtitle_path_ffmpeg}':force_style='FontSize={font_size},Alignment=10,MarginV=0'",
            "-map", "0:v:0",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            final_output_path,
        ]

        subprocess.run(ffmpeg_cmd, check=True)

        # Remove the trimmed video file
        if os.path.exists(trimmed_video_path):
            os.remove(trimmed_video_path)
            print(f"🗑️ Removed trimmed video: {trimmed_video_path}")

        print(f"✅ Final video created: {final_output_path}")
        return final_output_path

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        return None
