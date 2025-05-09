import asyncio
import os
import time
from generate_text import createText
from generate_audio import generateAudio
from make_subtitles import generateSubtitles
from make_video import make_video_with_subs


async def main():
    input_file_path = "input.txt"
    output_audio_dir = "output/audio"
    output_brainrot_text_dir = "output/brainrot_texts"
    os.makedirs(output_audio_dir, exist_ok=True)

 # ⏱️ Generate brainrot text
    start = time.time()
    print("🧠 Generating brainrot text...")
    brainrot_text_path = createText(input_file_path, output_brainrot_text_dir)
    end = time.time()
    print(f"✅ Brainrot text done in {end - start:.2f}s\n")

    # brainrot_text = ""
    # with open(f"{output_brainrot_text_dir}/output_1.txt", "r", encoding="utf-8") as file:
    #     brainrot_text = file.read()

    # ⏱️ Generate audio
    start = time.time()
    print("🔊 Generating audio...")
    audio_file_path = await generateAudio(output_audio_dir, brainrot_text_path)
    end = time.time()
    print(f"✅ Audio done in {end - start:.2f}s\n")

    # ⏱️ Generate subtitles
    start = time.time()
    print("📝 Generating subtitles...")
    subtitle_file_path = generateSubtitles(audio_file_path, brainrot_text_path)
    end = time.time()
    print(f"✅ Subtitles done in {end - start:.2f}s\n")

    # ⏱️ Make final video
    start = time.time()
    print("🎞️ Creating final video...")
    final_video_path = make_video_with_subs(
        audio_file_path, subtitle_file_path)
    end = time.time()
    print(f"Final video created in {end - start:.2f}s\n")

    print(f"🎉 Final path: {final_video_path}")

if __name__ == "__main__":
    asyncio.run(main())
