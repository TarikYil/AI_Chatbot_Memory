import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GoogleEmbeddings:
    """
    GoogleEmbeddings class interacts with Google's Generative AI API to generate embeddings
    for given text. It uses the API key stored in the environment variable `GOOGLE_API_KEY`
    to authenticate and make requests to the embedding model.

    Attributes:
        None
    """

    def __init__(self):
        """
        Initializes the GoogleEmbeddings class and configures the Google API client by loading
        the API key from environment variables. If the API key is missing, it raises a ValueError.

        Raises:
            ValueError: If the GOOGLE_API_KEY environment variable is not set.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)

    def get_embedding(self, text: str):
        """
        Generates an embedding for the provided text using Google's Generative AI API.

        Args:
            text (str): The text content for which to generate the embedding.

        Returns:
            list: The embedding vector representing the text, or None if an error occurs.

        Raises:
            ValueError: If the provided text is empty or only contains whitespace.
            Exception: If there is an error during the embedding generation process.
        """
        if not text.strip():
            raise ValueError("Embedding cannot be created for empty content.")
        try:
            response = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return response["embedding"]
        except Exception as e:
            print(f"Error occurred while creating embedding: {e}")
            return None
