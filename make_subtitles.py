import os
import re
from typing import Tuple
import warnings
from fuzzywuzzy import fuzz  # type: ignore
import whisper  # type: ignore

# Suppress known harmless warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")


def clean_word(word: str) -> str:
    """
    Cleans a word by removing non-alphanumeric characters, stripping whitespace, and converting to lowercase.

    Args:
        word: The word to clean.

    Returns:
        The cleaned word.
    """
    return re.sub(r'[^\w\s]', '', word).strip().lower()


def format_time(seconds: float) -> str:
    """
    Formats time in seconds to HH:MM:SS,milliseconds format.

    Args:
        seconds: Time in seconds.

    Returns:
        Formatted time string.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def format_ssa_time(seconds: float) -> str:
    """Formats time in seconds to HH:MM:SS.cc (centiseconds) for SSA subtitles."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int((seconds - int(seconds)) * 100)  # Centiseconds
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"


def find_best_match(word: str, candidates: list, min_score: int = 60) -> Tuple[str, int, int]:
    """
    Finds the best matching word in a list of candidates using fuzzy matching.

    Args:
        word: The word to match.
        candidates: A list of candidate words.
        min_score: Minimum fuzzy match score.

    Returns:
        A tuple containing the best matching word, its index, and the match score.
    """
    best_score = -1
    best_word = word
    best_index = 0
    for i, candidate in enumerate(candidates):
        score = fuzz.ratio(clean_word(word), clean_word(candidate))
        if score > best_score:
            best_score = score
            best_word = candidate
            best_index = i
    if best_score < min_score:
        return word, -1, best_score  # Return -1 for index if no good match
    return best_word, best_index, best_score


def generateSubtitlesSSA(audio_file_path: str, text_file_path: str) -> str:
    """
    Generates SSA subtitles from an audio file and a text file, with improved word matching.

    Args:
        audio_file_path: Path to the audio file.
        text_file_path: Path to the text file.

    Returns:
        Path to the generated SSA subtitle file.
    """
    SUBTITLE_DIR = "output/subtitles"
    os.makedirs(SUBTITLE_DIR, exist_ok=True)

    model = whisper.load_model("base")
    transcript = model.transcribe(audio_file_path, word_timestamps=True)

    with open(text_file_path, 'r', encoding='utf-8') as file:
        content = file.read().replace('-', ' ')
    words = content.split()

    base_name = "subtitle_"
    ext = ".ssa"
    counter = 1
    while os.path.exists(os.path.join(SUBTITLE_DIR, f"{base_name}{counter}{ext}")):
        counter += 1
    ssa_path = os.path.join(SUBTITLE_DIR, f"{base_name}{counter}{ext}")

    # SSA header
    header = """[Script Info]
Title: Word-by-Word Subtitles
ScriptType: v4.00+
PlayResX: 640
PlayResY: 360

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,52,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,4,0,1,3,0,2,10,10,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    word_index = 0
    events = []
    previous_end_time = 0  # Track end time of previous word
    text_length = len(words)
    audio_words = []

    for segment in transcript['segments']:
        for word_info in segment.get('words', []):
            audio_words.append({
                'word': word_info['word'],
                'start': word_info['start'],
                'end': word_info['end']
            })
    audio_index = 0

    # Create a mapping of audio words to their times
    audio_timing = {}
    for aw in audio_words:
        audio_timing[clean_word(aw['word'])] = {
            'start': aw['start'], 'end': aw['end']}

    for i, text_word in enumerate(words):
        text_word_cleaned = clean_word(text_word)

        if text_word_cleaned in audio_timing:
            start_time = audio_timing[text_word_cleaned]['start']
            end_time = audio_timing[text_word_cleaned]['end']
        else:
            # If the word is not found, try to find the closest match in the audio
            best_match, _, similarity = find_best_match(
                text_word, [w['word'] for w in audio_words])
            if similarity >= 60:  # tune this threshold
                start_time = audio_timing[clean_word(best_match)]['start']
                end_time = audio_timing[clean_word(best_match)]['end']
            else:
                # Handle the case where no match is found.  You might need to do more sophisticated handling
                #  like interpolating from surrounding words, or using a default duration.
                if i > 0 and i < len(words) - 1:
                  # get the average of the surrounding words
                    start_time = (
                        previous_end_time + audio_timing[clean_word(words[i+1])]['start'])/2
                    end_time = (audio_timing[clean_word(
                        words[i+1])]['end'] + audio_timing[clean_word(words[i+1])]['end'])/2
                elif i == 0 and len(words) > 1:
                    start_time = 0
                    end_time = audio_timing[clean_word(words[i+1])]['start']
                elif i == len(words) - 1 and len(words) > 1:
                    start_time = previous_end_time
                    end_time = previous_end_time + 0.5  # Arbitrary duration

                else:  # only word
                    start_time = 0
                    end_time = 1

        # Ensure no overlap
        start = max(start_time, previous_end_time)
        end = end_time
        if start >= end:
            continue

        start_ssa = format_ssa_time(start)
        end_ssa = format_ssa_time(end)
        events.append(
            f"Dialogue: 0,{start_ssa},{end_ssa},Default,,0,0,0,,{text_word}")
        previous_end_time = end

    with open(ssa_path, 'w', encoding='utf-8') as ssa_file:
        ssa_file.write(header)
        ssa_file.write("\n".join(events))

    print(f"✅ SSA subtitle file saved to: {ssa_path}")
    return ssa_path
