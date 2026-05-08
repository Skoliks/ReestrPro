from sqlalchemy.orm import Session

from backend.db.models import ImportBatch


class ImportBatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, batch: ImportBatch) -> ImportBatch:
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def update(self, batch: ImportBatch) -> ImportBatch:
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def get_by_id(self, batch_id: int) -> ImportBatch | None:
        return (
            self.db.query(ImportBatch)
            .filter(ImportBatch.id == batch_id)
            .first()
        )