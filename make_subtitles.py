import re
import warnings
from fuzzywuzzy import fuzz  # type: ignore
import whisper  # type: ignore

# Suppress known harmless warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

# Load Whisper model
model = whisper.load_model("base")

# Input audio
AUDIO = "outputeTTS.mp3"

# Transcribe with word-level timestamps
transcript = model.transcribe(AUDIO, word_timestamps=True)

# Load cleaned or brainrot-edited input text
with open('output.txt', 'r', encoding='utf-8') as file:
    content = file.read().replace('-', ' ')
words = content.split()


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


# Generate SRT
srt_counter = 1
index = 0
with open('subtitles.srt', 'w', encoding='utf-8') as srt:
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
                    window = words[max(0, index - 3)                                   :min(len(words), index + 3)]
                    best_match, rel_idx = find_best_match(audio_word, window)
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
