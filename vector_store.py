from typing import List

class VectorStoreManager:
    """Wrapper around OpenAI vector store operations."""

    def __init__(self, client, vector_store_id: str):
        self.client = client
        self.vector_store_id = vector_store_id

    def _upsert_vectors(self, vectors):
        """Internal helper to upsert vectors using available API."""
        if hasattr(self.client, "beta") and hasattr(self.client.beta, "vector_stores"):
            self.client.beta.vector_stores.vectors.upsert(
                vector_store_id=self.vector_store_id,
                vectors=vectors,
            )
        elif hasattr(self.client, "vector_stores"):
            # fallback for clients exposing vector_stores at the root
            self.client.vector_stores.vectors.upsert(
                vector_store_id=self.vector_store_id,
                vectors=vectors,
            )
        else:
            raise AttributeError("Vector store API not available in OpenAI client")

    def store_embedding(self, video_id: int, embedding: List[float]) -> None:
        """Store a single embedding in the vector store."""
        try:
            self._upsert_vectors([{"id": str(video_id), "values": embedding}])
        except Exception as e:
            print(f"Error storing embedding: {e}")

    def query_embeddings(self, embedding: List[float], top_n: int = 5) -> List[int]:
        """Return IDs of the most similar vectors."""
        try:
            if hasattr(self.client, "beta") and hasattr(self.client.beta, "vector_stores"):
                resp = self.client.beta.vector_stores.query(
                    vector_store_id=self.vector_store_id,
                    embedding=embedding,
                    top_k=top_n,
                )
            elif hasattr(self.client, "vector_stores"):
                resp = self.client.vector_stores.query(
                    vector_store_id=self.vector_store_id,
                    embedding=embedding,
                    top_k=top_n,
                )
            else:
                raise AttributeError("Vector store API not available in OpenAI client")

            return [int(item["id"]) for item in resp.data]
        except Exception as e:
            print(f"Error querying vector store: {e}")
            return []
