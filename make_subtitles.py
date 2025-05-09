import os
import re
import warnings
from fuzzywuzzy import fuzz  # type: ignore
import whisper  # type: ignore

# Suppress known harmless warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")


def clean_word(word):
    return re.sub(r'[^\w\s]', '', word).strip().lower()


def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = round(seconds % 60, 3)
    return f"{h:02}:{m:02}:{s:06.3f}".replace('.', ',')


def find_best_match(target, candidates):
    target_clean = clean_word(target)
    best_word, best_score, best_idx = target, 0, 0
    for i, c in enumerate(candidates):
        score = fuzz.ratio(target_clean, clean_word(c))
        if score > best_score:
            best_word, best_score, best_idx = c, score, i
    return best_word, best_idx


def generateSubtitles(audio_file_path: str, text_file_path: str) -> str:
    # Ensure subtitle output directory exists
    SUBTITLE_DIR = "output/subtitles"
    os.makedirs(SUBTITLE_DIR, exist_ok=True)

    # Load Whisper model
    model = whisper.load_model("base")

    # Transcribe with word-level timestamps
    transcript = model.transcribe(audio_file_path, word_timestamps=True)

    # Load cleaned or brainrot-edited input text
    with open(text_file_path, 'r', encoding='utf-8') as file:
        content = file.read().replace('-', ' ')
    words = content.split()

    # Find next available subtitle filename (e.g., sub_1.srt, sub_2.srt)
    base_name = "subtitle_"
    ext = ".srt"
    srt_counter = 1
    while os.path.exists(os.path.join(SUBTITLE_DIR, f"{base_name}{srt_counter}{ext}")):
        srt_counter += 1

    str_path = os.path.join(SUBTITLE_DIR, f"{base_name}{srt_counter}{ext}")

    # Generate SRT
    index = 0
    with open(str_path, 'w', encoding='utf-8') as srt:
        for segment in transcript['segments']:
            for word_info in segment['words']:
                if index >= len(words):
                    break

                audio_word = word_info['word']
                audio_clean = clean_word(audio_word)
                text_word = words[index]
                text_clean = clean_word(text_word)

                # Try fuzzy matching if not a perfect match
                if audio_clean != text_clean:
                    similarity = fuzz.ratio(audio_clean, text_clean)
                    if similarity < 30:
                        window = words[max(0, index - 3):min(len(words), index + 3)]
                        best_match, rel_idx = find_best_match(
                            audio_word, window)
                        index = max(0, index - 3) + rel_idx
                        text_word = best_match
                    else:
                        text_word = words[index]
                    index += 1
                else:
                    index += 1

                # Write to SRT
                srt.write(f"{srt_counter}\n")
                srt.write(
                    f"{format_time(word_info['start'])} --> {format_time(word_info['end'])}\n")
                srt.write(f"{text_word}\n\n")
                srt_counter += 1

    print(f"✅ Subtitle file saved to: {str_path}")
    return str_path


if __name__ == "__main__":
    generateSubtitles("outputeTTS.mp3")
