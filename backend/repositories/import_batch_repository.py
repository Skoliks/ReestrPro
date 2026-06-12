from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import ImportBatch


class ImportBatchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, batch: ImportBatch) -> ImportBatch:
        self.db.add(batch)
        await self.db.commit()
        await self.db.refresh(batch)
        return batch

    async def update(self, batch: ImportBatch) -> ImportBatch:
        self.db.add(batch)
        await self.db.commit()
        await self.db.refresh(batch)
        return batch

    async def get_by_id(self, batch_id: int) -> ImportBatch | None:
        result = await self.db.execute(
            select(ImportBatch).where(ImportBatch.id == batch_id)
        )
        return result.scalar_one_or_none()
