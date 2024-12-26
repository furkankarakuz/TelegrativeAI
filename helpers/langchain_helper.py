"""
This file contains the implementation of the LangChainHelper class, which facilitates document-based question answering using LangChain's capabilities for text splitting, vector storage, and retrieval.

The class provides methods to:
- Load and process documents in various formats (e.g., PDF, TXT).
- Split documents into manageable chunks for analysis.
- Store and retrieve document vectors for context-based Q&A.
- Integrate with an OpenAI model to generate responses based on retrieved document content.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document


class LangChainHelper():
    """A helper class for handling document-based Q&A with LangChain."""

    def __init__(self, model, embed_model):
        """
        Initialize the LangChainHelper class.

        Args:
            model: The OpenAI model used for generating responses.
            embed_model: The embedding model used for vectorizing document content.

        Returns:
            None
        """
        self.model = model
        self.embed_model = embed_model

    def rag_with_documents(self, filepath, prompt) -> str:
        """
        Perform retrieval-augmented generation (RAG) using the provided document and prompt.

        Args:
            filepath (str): Path to the document file.
            prompt (str): The user query or question.

        Returns:
            str: The AI-generated response based on retrieved document content.

        Raises:
            KeyError: If the provided file_type is not supported.
        """

        loader = PyPDFLoader(filepath)
        raw_documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0, length_function=len)
        splitted_documents = text_splitter.split_documents(raw_documents)

        vector_store = FAISS.from_documents(splitted_documents, self.embed_model)
        retriever = vector_store.as_retriever()
        relevant_documents = retriever.get_relevant_documents(prompt)

        context_data = ""
        for document in relevant_documents:
            context_data += document.page_content

        final_prompt = f""""Here is your question: {prompt}
        We have the following information to answer it: {context_data}.
        Use only the information provided here to answer the question. Do not go beyond this."
        """

        return self.model.chat_message(final_prompt)

    def rag_with_documents_from_text(self, text_content, prompt) -> str:
        """
        Perform retrieval-augmented generation (RAG) using the provided text content and prompt. This method is for text content (e.g., from a .txt file).

        Args:
            text_content (str): The raw text content of the document.
            prompt (str): The user query or question.

        Returns:
            str: The AI-generated response based on retrieved document content.
        """
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0, length_function=len)

        raw_documents = [Document(page_content=text_content)]
        splitted_documents = text_splitter.split_documents(raw_documents)

        texts = []
        for doc in splitted_documents:
            if isinstance(doc, Document):
                texts.append(doc.page_content)
            else:
                print(f"Unexpected document format: {doc}")

        vector_store = FAISS.from_documents(splitted_documents, self.embed_model)
        retriever = vector_store.as_retriever()
        relevant_documents = retriever.get_relevant_documents(prompt)

        context_data = ""
        for document in relevant_documents:
            context_data += document.page_content

        final_prompt = f""""Here is your question: {prompt}
        We have the following information to answer it: {context_data}.
        Use only the information provided here to answer the question. Do not go beyond this."
        """

        return self.model.chat_message(final_prompt)
