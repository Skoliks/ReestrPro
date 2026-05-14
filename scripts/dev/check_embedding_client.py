from backend.external.embedding_client import EmbeddingClient


def main() -> None:
    client = EmbeddingClient()

    text = "детская одежда из хлопка"
    embedding = client.embed_text(text)

    print("Model:", client.model_name)
    print("Dimension:", client.get_dimension())
    print("Vector length:", len(embedding))
    print("First 10 values:", embedding[:10])


if __name__ == "__main__":
    main()