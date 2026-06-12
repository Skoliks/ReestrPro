import argparse
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.db.session import SessionLocal
from backend.services.embedding_service import EmbeddingService


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate embeddings for imported documents"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="How many documents to process",
    )

    args = parser.parse_args()

    async with SessionLocal() as db:
        service = EmbeddingService(db)
        result = await service.generate_for_documents(limit=args.limit)

        print("Embedding generation completed")
        print(f"Total documents selected: {result['total_documents']}")
        print(f"Created embeddings: {result['created']}")
        print(f"Skipped: {result['skipped']}")


if __name__ == "__main__":
    asyncio.run(main())
