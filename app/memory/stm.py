from typing import List
from app.models import ChatMessage

class ShortTermMemory:
    """
    ShortTermMemory (STM) class is responsible for storing and managing
    chat messages during a user's session. STM is cleared when the session ends
    or the page is refreshed.

    Attributes:
        sessions (dict): A dictionary where keys are user IDs and values are lists of `ChatMessage` objects.
    """

    def __init__(self):
        """
        Initializes the ShortTermMemory class. This creates an empty dictionary
        to store sessions for users, with each user identified by their user ID.
        """
        self.sessions = {}  # user_id: List[ChatMessage]

    def get_session(self, user_id: str) -> List['ChatMessage']:
        """
        Retrieves the session (chat history) for a given user ID.

        Args:
            user_id (str): The ID of the user whose chat history is to be retrieved.

        Returns:
            List[ChatMessage]: A list of `ChatMessage` objects representing the user's chat history. 
                                If no session exists, an empty list is returned.
        """
        return self.sessions.get(user_id, [])

    def add_message(self, user_id: str, message: 'ChatMessage'):
        """
        Adds a new message to the session for the given user ID.

        If the user does not have a session yet, a new session is created.

        Args:
            user_id (str): The ID of the user to add the message for.
            message (ChatMessage): The `ChatMessage` object representing the message to be added.
        """
        if user_id not in self.sessions:
            self.sessions[user_id] = []
        self.sessions[user_id].append(message)

    def clear_session(self, user_id: str):
        """
        Clears the session (chat history) for the given user ID.

        This method deletes the user's entire chat history from the STM.

        Args:
            user_id (str): The ID of the user whose session is to be cleared.
        """
        if user_id in self.sessions:
            del self.sessions[user_id]
