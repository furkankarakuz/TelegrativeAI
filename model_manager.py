"""
This file contains the implementation of the OpenAIModelManager class, which acts as a manager for OpenAI-based models.

The module provides functionalities for:
- Validating and managing OpenAI API keys.
- Initializing helpers for text-based and document-based interactions.
- Managing integrations with OpenAI and LangChain.
"""


from helpers.openai_helper import OpenAIHelper
from helpers.langchain_helper import LangChainHelper
from langchain_openai import OpenAIEmbeddings


class OpenAIModelManager():
    """
    A manager class for handling OpenAI models and associated functionalities.
    """
    def __init__(self, api_key):
        """
        Initialize the OpenAIModelManager class.

        Args:
            api_key (str): The OpenAI API key for authentication.

        Returns:
            None
        """
        self.model = OpenAIHelper(api_key)
        self.lang_model = LangChainHelper(self.model, OpenAIEmbeddings(api_key=api_key))

        self._validate_api_key()

    def _validate_api_key(self):
        """
        Validate the provided OpenAI API key.

        Raises:
            Exception: If the API key is invalid.

        Returns:
            None
        """
        self.model.check_api_key()
