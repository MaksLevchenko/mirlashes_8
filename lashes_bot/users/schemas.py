from pydantic import BaseModel


class ClientSchema(BaseModel):
    """Схема клиента"""

    telega_id: int
    name: str
    phone: str
    comment: str
