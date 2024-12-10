from sqlalchemy.orm import Session
from database.models import FileRecord

def add_file_record(session: Session, user_id: int, file_name: str, file_type: str, output_file: str):
    record = FileRecord(
        user_id=user_id,
        file_name=file_name,
        file_type=file_type,
        output_file=output_file
    )
    session.add(record)
    session.commit()

def get_user_statistics(session: Session, user_id: int):
    return session.query(FileRecord).filter_by(user_id=user_id).all()
