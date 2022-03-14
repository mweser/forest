import aioredis

from forest import utils


class Redeem:
    def __init__(self) -> None:
        self.conn = aioredis.Redis(
            host=utils.get_secret("REDIS_URL"),
            port=36272,
            password=utils.get_secret("REDIS_PASSWORD"),
            ssl=True,
        )

    async def init(self, codes: list[str]) -> None:
        for code in codes:
            await self.conn.set(code, "unredeemed")

    async def check(self, user: str, code: str) -> bool:
        if await self.conn.incr(user) > 3:
            return False
        if await self.conn.get(code.upper()):
            await self.conn.set(code.upper(), "redeemed")
            return True
        return False
