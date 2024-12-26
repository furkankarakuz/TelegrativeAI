"""
This file contains the implementation of the OpenAIHelper class, which serves as a utility for interacting with various OpenAI models, including GPT for text generation, Whisper for audio transcription, and DALL-E for image generation.
The class provides methods to:
- Generate text-based responses for user prompts.
- Transcribe audio files to text.
- Create images from textual descriptions.
- Validate the provided OpenAI API key.
"""

from openai import OpenAI


class OpenAIHelper():
    """A helper class for interacting with OpenAI API"""

    def __init__(self, api_key: str, text_model_name: str = "gpt-3.5-turbo-0125", transcribe_model_name: str = "whisper-1", image_model_name: str = "dall-e-3", temperature: None | int = None, max_tokens: None | int = None):
        """
        Initialize the OpenAIHelper class.

        Args:
            api_key (str): API key for OpenAI.
            text_model_name (str, optional): Model name for text generation. Defaults to "gpt-3.5-turbo-0125".
            transcribe_model_name (str, optional): Model name for transcription. Defaults to "whisper-1".
            image_model_name (str, optional): Model name for image generation. Defaults to "dall-e-3".
            temperature (float | None, optional): Sampling temperature for text generation. Defaults to None.
            max_tokens (int | None, optional): Maximum number of tokens for text generation. Defaults to None.

        Returns:
            None
        """
        self.openai_client = OpenAI(api_key=api_key)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.text_model_name = text_model_name
        self.transcribe_model_name = transcribe_model_name
        self.image_model_name = image_model_name
        self.system = {"role": "system", "content": "You are a helpful assistant. You know every language, but your primary preference is to respond in English."}

    def chat_message(self, prompt: str) -> str:
        """
        Generate a chat response for a given prompt.

        Args:
            prompt (str): The user input or query.

        Returns:
            str: The AI-generated response.
        """
        text_response = self.openai_client.chat.completions.create(model=self.text_model_name, temperature=self.temperature, max_tokens=self.max_tokens, messages=[self.system, {"role": "user", "content": prompt}])
        return text_response.choices[0].message.content

    def transcribe_voice(self, audio: str, language: str = "eng") -> str:
        """
        Transcribe audio to text using OpenAI's Whisper model.

        Args:
            audio (str): Path to the audio file.
            language (str): Language code for transcription. Defaults to "eng".

        Returns:
            str: The transcribed text.
        """
        transcribe_response = self.openai_client.audio.transcriptions.create(model=self.transcribe_model_name, file=audio, language="en")
        return transcribe_response.text

    def create_image(self, prompt, size="1024x1024") -> tuple[str, str]:
        """
        Generate an image based on a given prompt.

        Args:
            prompt (str): Description of the image to generate.
            size (str, optional): Size of the image (e.g., "1024x1024"). Defaults to "1024x1024".

        Returns:
            tuple[str, str]: The URL of the generated image and the revised prompt.
        """
        AI_Response = self.openai_client.images.generate(prompt=prompt, model=self.image_model_name, size=size, quality="standard", n=1, response_format="url").data[0]

        return AI_Response.url, AI_Response.revised_prompt

    def check_api_key(self) -> None:
        """
        Verify the validity of the provided OpenAI API key.

        Raises:
            Exception: If the API key is invalid or cannot access the models list.
        """
        self.openai_client.models.list()
