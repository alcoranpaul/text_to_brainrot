
import os
import asyncio
import random

import edge_tts
from edge_tts import VoicesManager


async def generateAudio(output_dir: str, brainrot_file_path: str) -> str:
    """Main function"""
    base_name = "audio_"
    ext = ".mp3"
    counter = 1

    # Find next available filename
    while os.path.exists(os.path.join(output_dir, f"{base_name}{counter}{ext}")):
        counter += 1

    output_path = os.path.join(output_dir, f"{base_name}{counter}{ext}")

    try:
        voices = await VoicesManager.create()
        voice = voices.find(Gender="Male", Language="en")
        with open(brainrot_file_path, "r", encoding="utf-8") as file:
            brainrot_text = file.read()

            communicate = edge_tts.Communicate(
                brainrot_text, random.choice(voice)["Name"])
            await communicate.save(output_path)
            print(f"✅ Audio saved to: {output_path}")
            return output_path

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    output_dir = "output/audio"
    os.makedirs(output_dir, exist_ok=True)

    asyncio.run(generateAudio(output_dir))
