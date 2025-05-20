from sqlalchemy import Table, Column, Integer, ForeignKey
from app.db.base import Base 


document_categories_table = Table(
    "document_categories", Base.metadata,
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True)
)


document_tags_table = Table(
    "document_tags", Base.metadata,
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

document_historical_events_table = Table(
    "document_historical_events", Base.metadata,
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
    Column("historical_event_id", Integer, ForeignKey("historical_events.id"), primary_key=True)
)