
import requests
import json

import asyncio
import random

import edge_tts
from edge_tts import VoicesManager


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
- No Emojis
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


def createText() -> str:
    # Read user input from input.txt
    with open("input.txt", "r", encoding="utf-8") as f:
        user_input = f.read().strip()

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

    # Enhanced error checking
    if (
        "choices" in result and result["choices"] and
        "message" in result["choices"][0] and
        "content" in result["choices"][0]["message"]
    ):
        message = result["choices"][0]["message"]["content"]
        # Write the message to output.txt
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(message)
        return message
    elif (
        "choices" in result and result["choices"] and
        "error" in result["choices"][0]
    ):
        raise ValueError(
            f"API Error: {result['choices'][0]['error']['message']}")
    else:
        raise ValueError("Error: No valid response from API.")


async def amain() -> None:
    """Main function"""
    try:
        text = createText()

        voices = await VoicesManager.create()
        voice = voices.find(Gender="Male", Language="en")

        communicate = edge_tts.Communicate(text, random.choice(voice)["Name"])
        await communicate.save("outputeTTS.mp3")
        print("Done")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(amain())
