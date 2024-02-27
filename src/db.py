from typing import Union

from redis.asyncio import Redis


class Database:
    def __init__(self, url: str):
        self.redis = Redis.from_url(url)

    async def get(self, key: Union[bytes, str], default: Union[bytes, str, int, float]):
        value = await self.redis.get(key)
        if value is None:
            await self.set(key, default)
            value = default

        return value

    async def set(self, key: Union[bytes, str], value: Union[bytes, str, int, float]):
        return await self.redis.set(key, value)
