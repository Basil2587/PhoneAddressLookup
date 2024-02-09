import re
import logging
from fastapi import FastAPI, HTTPException, Depends
from redis import Redis
from pydantic import BaseModel, validator
import aioredis

app = FastAPI(title="PhoneAddressLookup", version="1.0", description="Описание методов API приложения")
redis_client = Redis(host='redis', port=6379)  # Подключение к Redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UpdatedAddressInfo(BaseModel):
    phone: str
    address: str

    @validator("phone")
    def validate_phone(cls, phone):
        # Проверка, что номер телефона состоит из 11 цифр и начинается с "8" или "+7"
        if not re.match(r'^(\+7|8)\d{10}$', phone):
            raise ValueError('Неверный формат номера телефона')
        return phone


async def get_redis_client():
    # создает и возвращает асинхронный клиент Redis
    return await aioredis.from_url(
        f"redis://{redis_client.connection_pool.connection_kwargs['host']}:"
        f"{redis_client.connection_pool.connection_kwargs['port']}/0")


@app.get("/check_data", summary="Получить адрес по номеру телефона")
async def check_data(phone: str, redis: aioredis.Redis = Depends(get_redis_client)):
    # Получение данных
    address = await redis.get(phone)

    if not address:
        raise HTTPException(status_code=404, detail="Адрес не найден")

    return {"address": address}


@app.post("/write_data", summary="Записать адрес по номеру телефона")
async def write_data(address_request: UpdatedAddressInfo, redis: aioredis.Redis = Depends(get_redis_client)):
    # Проверка валидности модели
    if not address_request.address:
        return {"message": "❌ Укажите адрес"}

    phone = address_request.phone
    address = address_request.address
    existing_phone = await redis.get(phone)

    if existing_phone:
        # Если номер уже существует, обновляем адрес
        await redis.set(phone, address)
        return {"message": "⚠ Номер уже существовал. Адрес успешно изменен"}

    await redis.set(phone, address)
    return {"message": "✅ Данные успешно записаны"}


@app.put("/write_data", summary="Обновить адрес по номеру телефона")
async def update_address(address_request: UpdatedAddressInfo, redis: aioredis.Redis = Depends(get_redis_client)):
    # Обновляем данные
    phone = address_request.phone
    address = address_request.address
    existing_phone = await redis.get(phone)

    if not existing_phone:
        raise HTTPException(status_code=404, detail="Номер не найден")

    await redis.set(phone, address)
    return {"message": "✅ Адрес успешно обновлен"}
