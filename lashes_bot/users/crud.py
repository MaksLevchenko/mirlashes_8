from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from db import pg_async_session, ModelBase
from db.models.models import Client
from users.schemas import ClientSchema
from users.query import add_new_client, select_client_to_id_telegram, update_model_q


async def update_model(user_info: dict, model: ModelBase):
    """
    Обновляет данные
    """
    schema = ClientSchema(**user_info)
    q = update_model_q(model=model, schema=schema)
    async with pg_async_session() as session:
        await session.execute(q)
        await session.commit()
    return schema


async def add_user(user_info: dict, model: ModelBase):
    """
    Добавляет нового клиента в БД
    """
    schema = ClientSchema(**user_info)
    q = add_new_client(schema=schema, model=model)
    async with pg_async_session() as session:
        await session.execute(q)
        await session.commit()
    return schema


async def get_user_to_telegram_id(tele_id: int):
    """По id находит нужного пользователя"""
    q = select_client_to_id_telegram(tele_id)
    async with pg_async_session() as session:
        user = await session.execute(q)
        return user.scalar()
