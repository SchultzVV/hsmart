import qdrant_client

def get_qdrant_client():
    return qdrant_client.QdrantClient(host="vector_db", port=6333)
