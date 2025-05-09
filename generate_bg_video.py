import os
import random
import yt_dlp
from moviepy import AudioFileClip

# Constants
VIDEO_PATH = "output/background_videos/"
AUDIO_PATH = "outputeTTS.mp3"
CHANNEL_URL = "https://www.youtube.com/@OrbitalNCG/videos"


def get_audio_duration(audio_file_path):
    audio_clip = AudioFileClip(audio_file_path)
    duration = audio_clip.duration
    audio_clip.close()
    return duration


def get_random_video_url(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,  # Extract only video URLs (not full data)
        'cachedir': False
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)

        # Check if 'info' is a dictionary and has 'entries'
        if isinstance(info, dict) and 'entries' in info:
            video_entries = info['entries']
            urls = [entry['url']
                    for entry in video_entries if isinstance(entry, dict)]
            if not urls:
                raise Exception("No video URLs found.")
            return random.choice(urls)

        # If 'info' is not the expected type, raise an exception
        raise Exception(
            "Failed to retrieve video URLs. The response is not a dictionary with 'entries'.")


def download_full_video(video_url):
    # Use yt-dlp to get video metadata
    ydl_opts = {
        # Limit to 1080p resolution
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/mp4',
        'merge_output_format': 'mp4',
        'quiet': False,
        'noplaylist': True,
        'cachedir': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract metadata
        video_info = ydl.extract_info(video_url, download=False)

        # Ensure video_info is a dictionary and contains the 'title' key
        if isinstance(video_info, dict) and 'title' in video_info:
            video_title = video_info['title'].replace(
                ' ', '_')  # Replace spaces with underscores
        else:
            raise ValueError(
                "Video title not found or invalid video_info structure.")

        # Check if the video size exceeds 1 GB
        if 'filesize' in video_info and video_info['filesize'] is not None:
            filesize_gb = video_info['filesize'] / \
                (1024 * 1024 * 1024)  # Convert bytes to GB
            if filesize_gb >= 1:
                raise ValueError(
                    f"Video is too large ({filesize_gb:.2f} GB). Skipping download.")

        # Raise ValueError if "Vertical" is in the title
        if "Vertical" in video_title:
            raise ValueError(f"Video title contains 'Vertical': {video_title}")

        output_file = os.path.join(
            VIDEO_PATH, f"{video_title}.mp4")  # Set output file name

        # Update the output template to include the video title
        ydl_opts['outtmpl'] = output_file

        # Download the video using the already extracted metadata
        with yt_dlp.YoutubeDL(ydl_opts) as download_ydl:
            # Use the video ID instead of re-extracting
            download_ydl.download([video_info['id']])

    print(f"✅ Full video downloaded and saved as '{output_file}'")

    # Remove the .part file if it exists
    part_file = f"{output_file}.part"
    if os.path.exists(part_file):
        os.remove(part_file)
        print(f"🗑️ Removed temporary file: {part_file}")

    return output_file


def download_random_full_video():
    while (True):
        try:
            video_url = get_random_video_url(CHANNEL_URL)
            download_full_video(video_url)
            break
        except Exception as e:
            print(f"Failed with video: {e}")
            print("Trying another video...")


def main():
    # Retry loop in case a video fails to download
    while (True):
        try:
            video_url = get_random_video_url(CHANNEL_URL)
            download_full_video(video_url)
            break
        except Exception as e:
            print(f"Failed with video: {e}")
            print("Trying another video...")


if __name__ == "__main__":
    main()
