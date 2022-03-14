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
            await self.conn.hset("active_codes", code, "AVAIL")

    async def check(self, user: str, code: str) -> bool:
        if await self.conn.hincrby("user_guesses", user, 1) > 3:
            return False
        if await self.conn.hget("active_codes", code.upper()):
            await self.conn.hset("active_codes", code.upper(), "USED")
            return True
        return False
