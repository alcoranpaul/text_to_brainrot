import os
import re
from typing import Tuple
import warnings
from fuzzywuzzy import fuzz  # type: ignore
import whisper  # type: ignore

# Suppress known harmless warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")


def clean_word_for_comparison(word: str) -> str:
    """Cleans a word for comparison by removing non-alphanumeric characters, stripping whitespace, and converting to lowercase."""
    word = re.sub(r'[^\w\s]', '', word)
    return word.strip().lower()


def format_ssa_time(seconds: float) -> str:
    """Formats time in seconds to H:MM:SS.cc (centiseconds) for SSA subtitles."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int((seconds - int(seconds)) * 100)  # Centiseconds
    return f"{hours}:{minutes:02}:{secs:02}.{cs:02}"


def find_best_match(current_word: str, context_words: list) -> Tuple[str, int]:
    """Finds the best matching word in a list of candidates using fuzzy matching."""
    cleaned_current_word = clean_word_for_comparison(current_word)

    best_match = current_word
    best_index = 0
    highest_similarity = 0

    for i, candidate in enumerate(context_words):
        cleaned_candidate = clean_word_for_comparison(candidate)

        similarity = fuzz.ratio(cleaned_current_word, cleaned_candidate)
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = candidate
            best_index = i
    return best_match, best_index


def generateSubtitlesSSA(audio_file_path: str, text_file_path: str, special_words: bool = True) -> str:
    """
    Generates SSA subtitles from an audio file and a text file, incorporating custom matching logic.

    Args:
        audio_file_path: Path to the audio file.
        text_file_path: Path to the text file.
        special_words: Flag to enable special word matching logic.

    Returns:
        Path to the generated SSA subtitle file.

    Raises:
        FileNotFoundError: If the audio file or text file does not exist.
        Exception: If an error occurs during the subtitle generation process.
    """
    SUBTITLE_DIR = "output/subtitles"
    os.makedirs(SUBTITLE_DIR, exist_ok=True)

    try:
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        if not os.path.exists(text_file_path):
            raise FileNotFoundError(f"Text file not found: {text_file_path}")

        model = whisper.load_model("base")
        transcript = model.transcribe(audio_file_path, word_timestamps=True)

        with open(text_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        content = ''.join(lines)
        content = content.replace('-', ' ')
        words = content.split()
        num_words = len(words)

        base_name = "subtitle_"
        ext = ".ssa"
        counter = 1
        while os.path.exists(os.path.join(SUBTITLE_DIR, f"{base_name}{counter}{ext}")):
            counter += 1
        ssa_path = os.path.join(SUBTITLE_DIR, f"{base_name}{counter}{ext}")

        # SSA header
        header = """[Script Info]
Title: Custom Matched Subtitles
ScriptType: v4.00+
PlayResX: 640
PlayResY: 360

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,52,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,4,0,1,3,0,2,10,10,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        events = []
        list_index = 0

        for segment in transcript['segments']:
            for word_info in segment['words']:
                start_time = word_info['start']
                end_time = word_info['end']
                word_text = word_info['word']

                cleaned_word_text = clean_word_for_comparison(word_text)

                if special_words and list_index < num_words:
                    original_text = words[list_index]
                    cleaned_original_text = clean_word_for_comparison(
                        original_text)

                    threshold = 20 if len(word_text) < 4 else 30

                    if cleaned_word_text != cleaned_original_text:
                        similarity = fuzz.ratio(
                            cleaned_word_text, cleaned_original_text)
                        if similarity < threshold:
                            context_window = [clean_word_for_comparison(w) for w in words[max(
                                0, list_index - 3):min(num_words, list_index + 4)]]
                            best_match_from_context, relative_index = find_best_match(
                                cleaned_word_text, context_window)
                            list_index = max(
                                0, list_index - 3) + relative_index
                            word_text = best_match_from_context  # Use the best match
                        else:
                            word_text = original_text
                    else:
                        word_text = original_text  # Use original if cleaned forms match

                    list_index += 1

                start_ssa = format_ssa_time(start_time)
                end_ssa = format_ssa_time(end_time)
                events.append(
                    f"Dialogue: 0,{start_ssa},{end_ssa},Default,,0,0,0,,{word_text}")

        with open(ssa_path, 'w', encoding='utf-8') as ssa_file:
            ssa_file.write(header)
            ssa_file.write("\n".join(events))

        print(f"✅ SSA subtitle file saved to: {ssa_path}")
        return ssa_path

    except FileNotFoundError as e:
        print(f"Error: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred during subtitle generation: {e}")
        raise
