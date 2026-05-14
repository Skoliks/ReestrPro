from sentence_transformers import SentenceTransformer


def main() -> None:
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    print("Загружаю модель...")
    model = SentenceTransformer(model_name)

    texts = [
        "детская одежда",
        "одежда для детей",
        "электрический кабель",
    ]

    print("Создаю embeddings...")
    embeddings = model.encode(texts)

    print("Model:", model_name)
    print("Embeddings shape:", embeddings.shape)
    print("Vector dimension:", len(embeddings[0]))
    print("First 10 values:", embeddings[0][:10])


if __name__ == "__main__":
    main()