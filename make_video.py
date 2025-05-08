from pydub.utils import mediainfo  # type: ignore
import subprocess


# Step 1: Get audio duration in seconds
def get_audio_duration(audio_path):
    info = mediainfo(audio_path)
    return float(info['duration'])


# Step 2: Build ffmpeg command
def make_video_with_subs(audio_path, srt_path, output_path="output.mp4", resolution="640x360", font_size=24):
    duration = get_audio_duration(audio_path)
    ffmpeg_cmd = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", f"color=c=black:s={resolution}:d={duration}",
        "-i", audio_path,
        "-vf", f"subtitles={srt_path}:force_style='FontSize={font_size},Alignment=10,MarginV=0'",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    print(f"✅ Video created: {output_path}")


if __name__ == "__main__":
    make_video_with_subs("outputeTTS.mp3", "subtitles.srt")
