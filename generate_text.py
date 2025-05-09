import json
import os
import re
import requests


brainrot_words_with_definitions = {}
with open("brainrot_words.txt", "r", encoding="utf-8") as f:
    for line in f:
        if "–" in line:  # Ensure the line contains a definition
            word, definition = map(str.strip, line.split("–", 1))
            brainrot_words_with_definitions[word] = definition

SYSTEM_PROMPT: str = f"""Transform any input into true brainrot style for study purposes:
- Use chaotic, surreal, and meme-infused language
- Incorporate Gen Alpha and Gen Z slang / Brainrot-words (e.g., rizz, skibidi, sigma, NPC, gyatt, delulu)
- Do not include '***' to emphasize the usage of brainrot-words.
- Maintain a balance-avoid overuse of any single term
- Ensure the core meaning remains intact
- Avoid overusing any single term; maintain a balance.
- Ensure the core meaning remains intact.
- Embrace disjointed, exaggerated, and emotionally charged phrasing
- Skip structure; add randomness and disjointedness.
- Include internet slang abbreviations (like "LOL" or "LMAO")
- Do not combine words with hypens or "-"
- No Emojis
- Do not generate any markdown formatting. Avoid bold (**), italics (*), code (`), headings (##), or links ([text](url)).
- Avoid special symbols (like ***, ###, ---, ===), or hyperlink formatting.
- Keep it in English only

Brainrot Words with Definitions:
{chr(10).join([f"- {word}: {definition}" for word, definition in brainrot_words_with_definitions.items()])}

Example Input:
"I think the project is too ambitious for our current timeline."
Example Output:
"We're not built for this. Way too much, not enough time."
"""

API_R1 = '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'
MODEL_V3 = "deepseek/deepseek-v3-base:free"
MODEL_R1 = "deepseek/deepseek-r1:free"
MODEL_R3 = "deepseek/deepseek-chat:free"


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
    return text


def createText(input_file_path: str, output_file_dir: str) -> str:
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
