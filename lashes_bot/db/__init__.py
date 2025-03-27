from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, declared_attr

from config.config import config


# Base = declarative_base()
class ModelBase(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False)


# Вывод сгенерированных запросов в логи: echo=True
_asyncio_engine = create_async_engine(config.postgres_url, echo=config.pg_engine_echo)

pg_async_session = async_sessionmaker(
    bind=_asyncio_engine, autoflush=False, expire_on_commit=False
)
