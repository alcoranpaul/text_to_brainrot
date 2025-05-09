import os
import re
from typing import Tuple
import warnings
from fuzzywuzzy import fuzz  # type: ignore
import whisper  # type: ignore

# Suppress known harmless warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")


def clean_word(word):
    return re.sub(r'[^\w\s]', '', word).strip().lower()


def format_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def find_best_match(word: str, candidates: list) -> Tuple[str, int]:
    best_score = -1
    best_word = word
    best_index = 0
    for i, candidate in enumerate(candidates):
        score = fuzz.ratio(clean_word(word), clean_word(candidate))
        if score > best_score:
            best_score = score
            best_word = candidate
            best_index = i
    return best_word, best_index


def generateSubtitles(audio_file_path: str, text_file_path: str) -> str:
    SUBTITLE_DIR = "output/subtitles"
    os.makedirs(SUBTITLE_DIR, exist_ok=True)

    model = whisper.load_model("base")
    transcript = model.transcribe(audio_file_path, word_timestamps=True)

    with open(text_file_path, 'r', encoding='utf-8') as file:
        content = file.read().replace('-', ' ')
    words = content.split()

    base_name = "subtitle_"
    ext = ".srt"
    counter = 1
    while os.path.exists(os.path.join(SUBTITLE_DIR, f"{base_name}{counter}{ext}")):
        counter += 1
    srt_path = os.path.join(SUBTITLE_DIR, f"{base_name}{counter}{ext}")

    word_index = 0
    subtitle_index = 1

    with open(srt_path, 'w', encoding='utf-8') as srt:
        for segment in transcript['segments']:
            for word_info in segment['words']:
                if word_index >= len(words):
                    break

                audio_word = word_info['word']
                text_word = words[word_index]

                if clean_word(audio_word) != clean_word(text_word):
                    similarity = fuzz.ratio(clean_word(
                        audio_word), clean_word(text_word))
                    if similarity < 60:
                        window = words[max(0, word_index - 3)
                                           :min(len(words), word_index + 4)]
                        best_match, rel_idx = find_best_match(
                            audio_word, window)
                        word_index = max(0, word_index - 3) + rel_idx
                        text_word = best_match

                # Write subtitle entry
                srt.write(f"{subtitle_index}\n")
                srt.write(
                    f"{format_time(word_info['start'])} --> {format_time(word_info['end'])}\n")
                srt.write(f"{text_word}\n\n")

                word_index += 1
                subtitle_index += 1

    print(f"✅ Subtitle file saved to: {srt_path}")
    return srt_path


if __name__ == "__main__":
    generateSubtitles("outputeTTS.mp3")
