from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class FileRecord(Base):
    __tablename__ = "file_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    output_file = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Инициализация базы данных
def init_db(db_url="sqlite:///db.sqlite"):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
