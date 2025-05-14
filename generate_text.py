import json
import os
import re
import requests


def strip_markdown(text):
    # Remove bold/italic markers
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # Remove inline code
    text = re.sub(r'`(.*?)`', r'\1', text)
    # Remove links
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1', text)
    # Remove heading markers and other markdown symbols
    text = re.sub(r'[#*_~`>]', '', text)
    # Replace hyphens and em dashes with space
    text = re.sub(r'[–—-]', ' ', text)
    # Remove apostrophes (replace with empty value)
    text = text.replace("'", "")

    return text


def createText(input_file_path: str, output_file_dir: str) -> str:
    brainrot_words_with_definitions = {}
    with open("brainrot_definitions.txt", "r", encoding="utf-8") as f:
        for line in f:
            if "–" in line:  # Ensure the line contains a definition
                word, definition = map(str.strip, line.split("–", 1))
                brainrot_words_with_definitions[word] = definition

    italian_brainrot_words = []

    with open("italian_brainrot_words.txt", "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip()  # Strip any surrounding whitespace
            if word:  # Only add non-empty lines
                italian_brainrot_words.append(word)

    SYSTEM_PROMPT: str = f"""Transform any input into expressive, emotionally-charged language with a light touch of brainrot and a sprinkle of Italian chaos:
    - Do not refer to the transformation, style, or prompt itself. Never say things like “let’s break it down,” “here’s the chaotic version,” or “with Gen Z rizz.” Just output the transformed content as if that’s the speaker’s natural voice.
    - Rewrite the input to sound **more exaggerated, impulsive, or emotionally intense**, while **keeping its meaning clear**.
    - Sprinkle in **Gen Z/Alpha slang** (e.g., rizz, skibidi, delulu, NPC, gyatt, sigma) and **internet speak** (e.g., LMAO, fr, OMG) where it fits naturally—but don’t overdo it.
    - Randomly insert **Italian brainrot words** (e.g., "bombombini", "frigo camelo", "mamma mia") to give it chaotic energy, but **don’t let them take over**.
    - Avoid markdown or special formatting like **bold, italics, or headings**.
    - *No emojies*
    - Don’t force structure—make it sound like a spontaneous brain-splatter or a dramatic reaction post.
    - Prioritize **humor, randomness, exaggeration**, but don’t lose the **core message**.
    - Avoid linear storytelling and overly tidy explanations. Let it feel **organic and reactive**.
    - **ENGLISH ONLY**

    Example Input:
    “I think the project is too ambitious for our current timeline.”

    Example Output:
    “Bro we tryna build the Eiffel Tower on a Monday morning not happening rn. Mamma mia, chill. This plan got zero rizz.”

    Brainrot Definitions:

    {chr(10).join([f"- {word}: {definition}" for word, definition in brainrot_words_with_definitions.items()])}

    Italian Brainrot Words to throw in randomly:

    {chr(10).join([f"- {word}" for word in italian_brainrot_words])}
    """

    API_R1 = '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'
    MODEL_V3 = "deepseek/deepseek-v3-base:free"
    MODEL_R1 = "deepseek/deepseek-r1:free"
    MODEL_R3 = "deepseek/deepseek-chat:free"
    # Read user input from input.txt
    with open(input_file_path, "r", encoding="utf-8") as f:
        user_input = f.read().strip()

    # Request Deepseek to convert input to brainrot
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_R1}",
            "Content-Type": "application/json",
            "X-Title": "Brainrot-TTS"
        },
        data=json.dumps({
            "model": MODEL_R3,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
        })
    )

    result = response.json()

    # Retrieve the content
    if (
        "choices" in result and result["choices"] and
        "message" in result["choices"][0] and
        "content" in result["choices"][0]["message"]
    ):
        message = strip_markdown(result["choices"][0]["message"]["content"])

        # Ensure output directory exists
        os.makedirs(output_file_dir, exist_ok=True)

        # Scan existing output_*.txt files
        existing_files = os.listdir(output_file_dir)
        output_numbers = [
            int(match.group(1)) for f in existing_files
            if (match := re.match(r"output_(\d+)\.txt", f))
        ]
        next_number = max(output_numbers, default=0) + 1

        output_path = os.path.join(
            output_file_dir, f"output_{next_number}.txt")

        # Save the brainrot text
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(message)

        print(f"✅ Text saved to: {output_path}")
        return output_path

    # Error handling - result returns and error
    elif (
        "choices" in result and result["choices"] and
        "error" in result["choices"][0]
    ):
        raise ValueError(
            f"API Error: {result['choices'][0]['error']['message']}")
    else:
        raise ValueError("Error: No valid response from API.")
