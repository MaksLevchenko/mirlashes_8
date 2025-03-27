from sqlalchemy import insert, select, update
from pydantic import BaseModel

from db import ModelBase
from db.models.models import Client


def select_client_to_id_telegram(tele_id: int):
    """По id телеграмм-пользователя формирует нужный запрос в базу"""
    q = select()
    q = q.add_columns(Client).where(Client.telega_id == tele_id)
    return q


def add_new_client(schema: BaseModel, model: ModelBase):
    """Добавляет нового клиента в базу"""
    q = insert(model).values(schema.model_dump())
    return q


def update_model_q(schema: BaseModel, model: ModelBase):
    print(schema.model_dump())
    q = (
        update(model)
        .where(model.telega_id == schema.telega_id)
        .values(**schema.model_dump())
    )
    return q
