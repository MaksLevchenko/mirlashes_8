from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped
from db import ModelBase


# Модель клиент
class Client(ModelBase):
    """Модель клиента"""

    telega_id: Mapped[int] = Column(Integer, nullable=False)
    name: Mapped[str] = Column(String, nullable=False)
    phone: Mapped[str] = Column(String, nullable=False)
    comment: Mapped[str] = Column(String, nullable=True)
    # course: list[int]


# Модель сервиса
class Service:
    id: int
    name: str
    description: str
    price: int
    foto: str


# Модель мастер
class Master:
    id: int
    name: str
    foto: str
    title: str
    rating: float
    massages_ids: list
