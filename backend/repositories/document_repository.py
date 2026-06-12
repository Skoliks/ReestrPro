from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import RegistryDocument


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, document: RegistryDocument) -> RegistryDocument:
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def create_many(self, documents: list[RegistryDocument]) -> None:
        self.db.add_all(documents)
        await self.db.commit()

    async def get_by_id(self, document_id: int) -> RegistryDocument | None:
        result = await self.db.execute(
            select(RegistryDocument).where(RegistryDocument.id == document_id)
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        query: str | None = None,
        document_type: str | None = None,
        status: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[RegistryDocument], int]:
        filters = []

        if document_type:
            filters.append(RegistryDocument.document_type == document_type)

        if status:
            filters.append(RegistryDocument.status == status)

        if query:
            pattern = f"%{query}%"
            filters.append(
                or_(
                    RegistryDocument.document_number.ilike(pattern),
                    RegistryDocument.applicant_name.ilike(pattern),
                    RegistryDocument.manufacturer_name.ilike(pattern),
                    RegistryDocument.product_full_name.ilike(pattern),
                    RegistryDocument.product_codes.ilike(pattern),
                    RegistryDocument.technical_regulations.ilike(pattern),
                )
            )

        total_result = await self.db.execute(
            select(func.count()).select_from(RegistryDocument).where(*filters)
        )
        total = total_result.scalar_one()

        items_result = await self.db.execute(
            select(RegistryDocument)
            .where(*filters)
            .order_by(RegistryDocument.id.desc())
            .offset(offset)
            .limit(limit)
        )
        items = list(items_result.scalars().all())

        return items, total

    async def get_documents_for_embeddings(self, limit: int = 10):
        result = await self.db.execute(
            select(RegistryDocument)
            .where(RegistryDocument.search_text.isnot(None))
            .order_by(RegistryDocument.id.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_documents_for_embeddings_by_batch(
        self,
        import_batch_id: int,
        limit: int | None = None,
    ):
        query = (
            select(RegistryDocument)
            .where(RegistryDocument.import_batch_id == import_batch_id)
            .where(RegistryDocument.search_text.isnot(None))
            .order_by(RegistryDocument.id.asc())
        )

        if limit is not None:
            query = query.limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_document_number_and_type(
        self,
        document_number: str,
        document_type: str,
    ) -> RegistryDocument | None:
        result = await self.db.execute(
            select(RegistryDocument).where(
                RegistryDocument.document_number == document_number,
                RegistryDocument.document_type == document_type,
            )
        )
        return result.scalar_one_or_none()
