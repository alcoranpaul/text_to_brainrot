# Text to Brain Rot Video Generator

This Python script takes a plain text file as input, transforms it into "brain rot" style text, generates audio from it using various TTS options, creates stylized subtitles, and finally combines everything with a random background video to produce a final "brain rot" video.

## Prerequisites

Before running the script, ensure you have the following installed:

* **Python 3.7+**
* **pip** (Python package installer)
* **FFmpeg** (for audio and video processing). Make sure the `ffmpeg` executable is in your system's PATH.
* **OpenAI Whisper** (for audio transcription). This will be installed as a dependency.
* **Microsoft TTS (Speech SDK)** (optional, for alternative audio generation). Installation instructions can be found in the [Microsoft Azure Speech SDK documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/quickstart-python).
* **DeepSeek Model Key** Taken from OpenRouter's models.
* **OpenRouter API Key** (for accessing various language models, potentially including DeepL and others). You'll need to sign up for an OpenRouter account and obtain an API key.

## Installation

1.  **Clone the repository** 

2.  **Install the required Python libraries:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the `main.py` script:**

    ```bash
    python main.py
    ```

2.  **Follow the prompts:**
    * The script will first generate "brain rot" text based on the content of `input.txt`.
    * You will be prompted to confirm the generated text:
        * Enter `y` to accept the text and proceed.
        * Enter `n` to discard the current text and generate a new version.
        * Enter `x` to exit the application.
    * Once the text is confirmed, the script will generate audio from it (potentially using Whisper, Microsoft TTS, or other options accessible via OpenRouter), then create subtitles, and finally combine everything into a video.

3.  **Create a `.env` file:**

    * In the same directory as your Python scripts (e.g., where `main.py` is located), create a new file named exactly `.env`.
    * Open the `.env` file in a text editor.
    * Add your OpenRouter API key to the file using the following format:

        ```dotenv
        OPEN_ROUTER_API=YOUR_OPENROUTER_API_KEY
        ```

        Replace `YOUR_OPENROUTER_API_KEY` with your actual API key.
    * Save the `.env` file.

4.  **Create an input text file:**

    * In the same directory as your Python scripts, create a new text file named `input.txt`.
    * Open the `input.txt` file in a text editor.
    * Enter the text you want to use as input for the brain rot video. This is the text that will be transformed, converted to audio, and used to generate subtitles.
    * Save the `input.txt` file.

5.  **Prepare input video files:** Place background video files in a directory named `output/background_videos` in the same directory as the scripts.

    > [!note] When there is no video found in the output/background_videos, you will be a prompt to download a YT video from the channel [@OrbitalNCG](https://www.youtube.com/@OrbitalNCG/videos)

## Warnings
- Cancelling during runtime may prematurely cause errors in api requests!
- Do not open any generated files during runtime!
- Subtitle generation may be inconsistent due to the nature of MS-TTS's generated audio
- Translation may be inconsistent due to free usage of DeepSeek API. Consider switching to a more premium version of Content generated AI.

## Script Descriptions

* **`main.py`**: The main entry point of the application. It orchestrates the entire process: generating text, audio, subtitles, and the final video.
* **`generate_text.py`**: Contains the `createText` function responsible for transforming the input text into "brain rot" style. The `_generateText` function in `main.py` handles the user confirmation loop for this generated text.
* **`generate_audio.py`**: Contains the `generateAudio` function, which handles text-to-speech. It likely has logic to use different TTS engines (e.g., Whisper for direct audio generation if capable, Microsoft TTS, or models accessible through the OpenRouter API). The `_generateAudio` function in `main.py` manages the audio generation process.
* **`make_subtitles.py`**: Contains the `generateSubtitlesSSA` function, which transcribes the audio and potentially uses fuzzy matching to align the generated subtitles with the original (or slightly modified) brain rot text, saving them in SSA format. The `_generateSubtitiles` function in `main.py` handles the subtitle generation.
* **`make_video.py`**: Contains the `make_video_with_subs` function, which takes the generated audio and subtitle files, a random video from the `videos` directory, and uses FFmpeg to combine them into a final video file with embedded subtitles. The `_generateFinalVideo` function in `main.py` manages the final video creation.

## Configuration

The script relies on environment variables loaded from the `.env` file for API keys and potentially other configuration settings. Ensure you have created this file and populated it with the necessary keys.

* **`OPENROUTER_API_KEY`**: Your API key for accessing models through the OpenRouter API.
* **`DEEPL_API_MODEL`**: The specific DeepL model ID to use via OpenRouter (if you intend to use DeepL).

Refer to the individual script files for any specific parameters or logic related to the chosen TTS engine and other processing steps.

## Troubleshooting

* **FFmpeg not found:** Ensure FFmpeg is installed correctly and its `bin` directory is added to your system's PATH environment variable.
* **Missing Python libraries:** If you encounter `ModuleNotFoundError`, ensure you have installed all the requirements using `pip install -r requirements.txt`.
* **API Key errors:** Double-check that your API keys in the `.env` file are correct.
* **Errors during audio/video processing:** Check the console output for error messages from the respective libraries (e.g., Whisper, FFmpeg, the TTS engine you are using). You might need to adjust input files or parameters.
* **OpenRouter/DeepL issues:** Ensure your OpenRouter API key is valid and that the specified DeepL model is supported. Check your OpenRouter API usage limits.
* **Microsoft TTS issues:** Verify your key and region are correct and that the Microsoft Speech SDK is installed properly.

## Contributing

If you'd like to contribute to this project, feel free to fork the repository and submit pull requests with your improvements.

## License

MIT License