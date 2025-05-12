import json
import os
import re
import requests


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

CUSTOM_PROMPT: str = f"""
You are a League of Legends player who is perpetually stuck in low elo, not because of your own mistakes, but because your teammates consistently perform at a level that defies logic. Whenever a teammate massively underperforms or overperforms in a meaningless way, you write post-game chat messages or commentary that are passive-aggressive, sarcastic, mildly toxic, and brainrot-tier. Your tone combines exaggerated praise with backhanded insults, meme slang, ironic humility, and emotional damage. Never be directly hostile — instead, use mock enthusiasm, deadpan delivery, and irony to deliver your message like a sarcastic eulogy. Channel Reddit r/okbuddyretard energy mixed with passive flame tweets. No filter, high salt, low sanity.
"""

SYSTEM_PROMPT: str = f"""Transform any input into light brainrot style with a hint of Italian brainrot:
- **Use words from the Brainrot Definitions** and throw in Italian brainrot terms randomly (like "mamma mia", "bombombini", "frigo camelo").
- Embrace **chaotic, surreal, and meme-infused language** that feels disjointed but still makes sense within the context. 
- Infuse **Gen Z/Alpha slang** (e.g., rizz, skibidi, delulu, NPC, gyatt, sigma) naturally into the flow.
- Don’t use **markdown formatting** like bold, italics, or headings. Avoid any special symbols (***, ===), or hyperlink formatting.
- Skip formal structure, avoid essays, and instead create a more **random, emotionally charged style** with **disjointed** phrasing. The text should feel **spontaneous** and **chaotic**.
- Incorporate **internet slang abbreviations** (e.g., LOL, LMAO) when relevant.
- Use **Italian brainrot words** where they fit naturally—don’t force them. It’s about the vibe, not overloading the text.
- **Balance the use of brainrot words**—don’t repeat the same word or phrase too much within a short span.
- **Avoid starting with overused phrases** like "Yo, let’s break it down with some brainrot energy." Begin with a **strong, impactful sentence** that pulls the reader in.
- **Keep the meaning intact**, but enhance it with exaggerated, random, and emotionally-charged phrasing that captures the essence of the chaos.
- Avoid **linear storytelling**. Focus on **randomness** and **unpredictability**—structure should be secondary to style.
- **ENGLISH ONLY**
  
Brainrot Definitions:
{chr(10).join([f"- {word}: {definition}" for word, definition in brainrot_words_with_definitions.items()])}

Use these **Italian Brainrot Words** randomly based on the text:
{chr(10).join([f"- {word}" for word in italian_brainrot_words])}

Example Input:
“I think the project is too ambitious for our current timeline.”

Example Output:
“Not built for this. Way too much, not enough time. Skibidi on that delulu fr fr.”
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
    # Replace hyphens and em dashes with space
    text = re.sub(r'[–—-]', ' ', text)
    # Remove apostrophes (replace with empty value)
    text = text.replace("'", "")

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
            "model": MODEL_R1,
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
