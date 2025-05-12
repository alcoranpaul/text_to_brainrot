import asyncio
import os
import time
from generate_text import createText
from generate_audio import generateAudio
from make_subtitles import generateSubtitles, generateSubtitlesSSA
from make_video import make_video_with_subs


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


async def main():
    input_file_path = "input.txt"
    output_audio_dir = "output/audio"
    output_brainrot_text_dir = "output/brainrot_texts"
    os.makedirs(output_audio_dir, exist_ok=True)

    clear_console()

    hasChosenBrainrotText: bool = False
    while (not hasChosenBrainrotText):
        # ⏱️ Generate brainrot text
        start = time.time()
        print("🧠 Generating brainrot text...")
        brainrot_text_path = createText(
            input_file_path, output_brainrot_text_dir)
        end = time.time()
        user_choice = input("Confirm text? Y/N: ").strip().lower()
        print(f"✅ Brainrot text done in {end - start:.2f}s\n")

        if user_choice == "y":
            hasChosenBrainrotText = True
        else:
            if os.path.exists(brainrot_text_path):
                os.remove(brainrot_text_path)
                print(f"🗑️ Removed trimmed video: {brainrot_text_path}")

    if brainrot_text_path != "" and brainrot_text_path != None:
        with open(brainrot_text_path, "r", encoding="utf-8") as brainrot_file:
            brainrot_text = brainrot_file.read()

        if len(brainrot_text) <= 0:
            print("Brainrot text is empty")
            return
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
    # subtitle_file_path = generateSubtitles(audio_file_path, brainrot_text_path)
    subtitle_file_path = generateSubtitlesSSA(
        audio_file_path, brainrot_text_path)
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
