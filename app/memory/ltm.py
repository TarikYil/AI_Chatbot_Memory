import os
import psycopg2
from typing import List
from datetime import datetime

class LongTermMemory:
    """
    LongTermMemory (LTM) class is responsible for storing, retrieving, and managing
    long-term memory in a PostgreSQL database using embeddings to represent content.

    Attributes:
        conn (psycopg2.extensions.connection): Database connection object.
        cursor (psycopg2.extensions.cursor): Database cursor object.
    """

    def __init__(self):
        """
        Initializes the LongTermMemory class by establishing a connection to the PostgreSQL database.
        It also creates the necessary database extension (pgvector) and the long_term_memory table if they don't exist.
        """
        self.conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=os.environ.get("POSTGRES_PORT", "5432"),
            database=os.environ.get("POSTGRES_DB", "mydatabase"),
            user=os.environ.get("POSTGRES_USER", "myuser"),
            password=os.environ.get("POSTGRES_PASSWORD", "mypassword")
        )
        self.cursor = self.conn.cursor()
        self._create_extension()
        self._create_table()

    def _create_extension(self):
        """
        Creates the 'pgvector' extension in the PostgreSQL database if it doesn't already exist.
        This extension is required to work with vector data types.
        """
        self.cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        self.conn.commit()

    def _create_table(self):
        """
        Creates the 'long_term_memory' table if it doesn't already exist.
        This table stores the content, embedding (vector), and timestamp of each memory.
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector(768),
                timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def store_memory(self, content: str, embedding: List[float]):
        """
        Stores a new memory in the long_term_memory table with the provided content and its embedding.

        Args:
            content (str): The content to be stored.
            embedding (List[float]): The embedding (vector representation) of the content.
        """
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
        self.cursor.execute("""
            INSERT INTO long_term_memory (content, embedding)
            VALUES (%s, %s::vector)
        """, (content, embedding_str))
        self.conn.commit()

    def retrieve_memory(self, query_embedding: List[float], limit: int = 5):
        """
        Retrieves the most relevant memories from the database by comparing the query embedding 
        with the stored embeddings using cosine similarity.

        Args:
            query_embedding (List[float]): The embedding of the query content.
            limit (int): The number of matching memories to return (default is 5).

        Returns:
            List[dict]: A list of dictionaries containing the 'content' and 'embedding' of the most relevant memories.
        """
        if not query_embedding:
            return []

        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        self.cursor.execute("""
            SELECT content, embedding
            FROM long_term_memory
            ORDER BY embedding <-> %s::vector
            LIMIT %s
        """, (embedding_str, limit))

        results = self.cursor.fetchall()
        print(f"[LTM] {len(results)} matching memories found.")
        return [{"content": res[0], "embedding": res[1]} for res in results]

    def delete_all_memories(self):
        """
        Deletes all records from the long_term_memory table.

        This will remove all stored memories from the database.
        """
        self.cursor.execute("DELETE FROM long_term_memory")
        self.conn.commit()

    def close(self):
        """
        Closes the database connection and cursor.

        This should be called when the application is shutting down to clean up resources.
        """
        self.cursor.close()
        self.conn.close()
