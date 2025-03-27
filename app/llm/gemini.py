import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiLLM:
    """
    GeminiLLM class interacts with Google's Gemini API to generate responses
    for a given chat history. The class uses the API key stored in the environment
    variable `GOOGLE_API_KEY` to authenticate and use the model.
    
    Attributes:
        model (google.generativeai.GenerativeModel): The instantiated Gemini model object for generating responses.
    """

    def __init__(self, model_name="gemini-2.0-flash"):
        """
        Initializes the GeminiLLM class, loads the API key from environment variables,
        and configures the Gemini model. If the API key is missing, it raises an exception.
        
        Args:
            model_name (str): The name of the model to use. Defaults to "gemini-2.0-flash".
        
        Raises:
            ValueError: If the GOOGLE_API_KEY environment variable is not set.
            Exception: If the model cannot be initialized.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)
        try:
            self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            print(f"Error initializing the model: {e}")
            self.model = None  # Set the model to None if initialization fails

    def generate_response(self, messages: list) -> str:
        """
        Generates a response using the Gemini model based on the provided chat history.

        Args:
            messages (list): A list of messages representing the chat history. Each message should have a "role" 
                             and "content" field. Messages with the role "system" are excluded from the history.
        
        Returns:
            str: The generated response text from the model. If the model is not initialized, a default message is returned.
        
        Raises:
            Exception: If there is an error in generating the response using the model.
        """
        if self.model is None:
            return "Model could not be initialized, please check your API key."

        try:
            # Filter out messages with the "system" role as they're not needed for the conversation history
            filtered_messages = [msg for msg in messages if msg["role"] != "system"]
            chat = self.model.start_chat(history=filtered_messages)

            # Get the user's latest message
            user_message = filtered_messages[-1]["parts"][0]["text"]

            # Send the user's message to the model and get a response
            response = chat.send_message(user_message)
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return "An error occurred while generating a response."
