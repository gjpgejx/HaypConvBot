from sqlalchemy import Column, Integer, String, DateTime, create_engine, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

# Создание базы данных
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    subscription_status = Column(String, default='free')  # 'free', 'active', 'expired'
    created_at = Column(DateTime, server_default=func.now())

    # file_stats = relationship("FileStat", back_populates="user_id")


class FileStat(Base):
    __tablename__ = 'file_stats'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    file_count = Column(Integer, default=0)
    last_used = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # user = relationship("User", back_populates="file_stats")

# Инициализация базы данных
def init_db(db_url="sqlite:///db.sqlite"):
    engine = create_engine(db_url)
    # Проверяем корректность мапперов
    try:
        print(User.__mapper__)
        print(FileStat.__mapper__)
    except Exception as e:
        print(f"Ошибка при настройке мапперов: {e}")

    # Создаем таблицы
    try:
        Base.metadata.create_all(bind=engine)
        print("Таблицы успешно созданы!")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")
        raise

    return sessionmaker(bind=engine)

SessionLocal = init_db()
