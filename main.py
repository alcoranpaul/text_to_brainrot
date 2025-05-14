import asyncio
import os
import sys
import time
from generate_text import createText
from generate_audio import generateAudio
from make_subtitles import generateSubtitlesSSA
from make_video import make_video_with_subs


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def _generateText(input_file_path: str, output_brainrot_text_dir: str) -> str:
    """Generates brainrot text based on the input file and prompts the user for confirmation.

    This function repeatedly calls the `createText` function to generate brainrot text
    from the content of the `input_file_path`. It then presents the generated text
    (via the created file path) to the user for confirmation. The user can choose
    to accept the text ('y'), regenerate it ('n'), or exit the application ('x').

    Args:
        input_file_path: The path to the input file containing the text to be
            transformed into brainrot.
        output_brainrot_text_dir: The directory where the generated brainrot text
            file will be saved.

    Returns:
        The path to the confirmed brainrot text file.

    Raises:
        ValueError: If the final confirmed brainrot text file is empty.
        SystemExit: If the user chooses to exit the application by entering 'x'.
    """
    hasChosenBrainrotText: bool = False

    while (not hasChosenBrainrotText):
        start = time.time()
        print("🧠 Generating brainrot text...")
        brainrot_text_path = createText(
            input_file_path, output_brainrot_text_dir)
        end = time.time()
        print(f"✅ Brainrot text done in {end - start:.2f}s\n")
        user_choice = input("Confirm text? Y/N/X: ").strip().lower()
        print("")

        # Choice to make the user
        if user_choice == "y":
            hasChosenBrainrotText = True
        elif user_choice == "n":
            if os.path.exists(brainrot_text_path):
                os.remove(brainrot_text_path)
                print(f"🗑️ Removed brainrot_text: {brainrot_text_path}")
        elif user_choice == "x":
            sys.exit(0)

    if brainrot_text_path != "" and brainrot_text_path != None:
        with open(brainrot_text_path, "r", encoding="utf-8") as brainrot_file:
            brainrot_text = brainrot_file.read()
            if len(brainrot_text) <= 0:
                raise ValueError("brainrot_text has no contents")

    return brainrot_text_path


async def _generateAudio(output_audio_dir: str, brainrot_text_path: str) -> str:
    """Generates audio from the brainrot text.

    This asynchronous function calls the `generateAudio` function to create an
    audio file based on the content of the provided brainrot text file.

    Args:
        output_audio_dir: The directory where the generated audio file will be saved.
        brainrot_text_path: The path to the brainrot text file to be converted to audio.

    Returns:
        The path to the generated audio file.
    """
    # ⏱️ Generate audio
    start = time.time()
    print("🔊 Generating audio...")
    audio_file_path = await generateAudio(output_audio_dir, brainrot_text_path)
    end = time.time()

    if audio_file_path == None:
        sys.exit(0)
    print(f"✅ Audio done in {end - start:.2f}s\n")

    return audio_file_path


async def _generateSubtitiles(audio_file_path: str, brainrot_text_path: str) -> str:
    """Generates SSA subtitles from the audio and brainrot text.

    This asynchronous function calls the `generateSubtitlesSSA` function to create
    an SSA subtitle file synchronized with the provided audio and based on the
    content of the brainrot text file.

    Args:
        audio_file_path: The path to the audio file for which subtitles will be generated.
        brainrot_text_path: The path to the brainrot text file to be used as the basis for subtitles.

    Returns:
        The path to the generated SSA subtitle file.
    """
    # ⏱️ Generate subtitles
    start = time.time()
    print("📝 Generating subtitles...")
    subtitle_file_path = generateSubtitlesSSA(
        audio_file_path, brainrot_text_path)
    end = time.time()
    if subtitle_file_path == None:
        sys.exit(0)
    print(f"✅ Subtitles done in {end - start:.2f}s\n")

    return subtitle_file_path


def _generateFinalVideo(audio_file_path: str, subtitle_file_path: str) -> str:
    """Combines the audio, subtitles, and a background video into a final video.

    This function calls the `make_video_with_subs` function to merge the provided
    audio and subtitle files with a randomly selected background video to create
    the final output video.

    Args:
        audio_file_path: The path to the audio file to be included in the final video.
        subtitle_file_path: The path to the SSA subtitle file to be overlaid on the final video.

    Returns:
        The path to the generated final video file.
    """
    # ⏱️ Make final video
    start = time.time()
    print("🎞️ Creating final video...")
    final_video_path = make_video_with_subs(
        audio_file_path, subtitle_file_path)
    end = time.time()
    if final_video_path == None:
        sys.exit(0)
    print(f"Final video created in {end - start:.2f}s\n")

    return final_video_path


async def main():
    input_file_path = "input.txt"
    output_audio_dir = "output/audio"
    output_brainrot_text_dir = "output/brainrot_texts"
    try:
        os.makedirs(output_audio_dir, exist_ok=True)
        clear_console()

        start = time.time()

        brainrot_text_path: str = _generateText(
            input_file_path, output_brainrot_text_dir)

        audio_file_path: str = await _generateAudio(
            output_audio_dir, brainrot_text_path)

        subtitle_file_path: str = await _generateSubtitiles(
            audio_file_path, brainrot_text_path)

        final_video_path: str = _generateFinalVideo(
            audio_file_path, subtitle_file_path)

        end = time.time()
        print(
            f"🎉 Final path: {final_video_path} -- Program duration: {end - start:.2f}s")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
