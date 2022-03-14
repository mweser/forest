import aioredis

from forest import utils


def regularize(code: str) -> str:
    text = "".join(code.upper()).encode("ascii", errors="ignore").decode()
    return "".join(c if (c.isalpha()) else "" for c in text)


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
        regular_code = regularize(code)
        if await self.conn.hget("active_codes", regular_code):
            await self.conn.hset("active_codes", regular_code, "USED")
            return True
        return False
