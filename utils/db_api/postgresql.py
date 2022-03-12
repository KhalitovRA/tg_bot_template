from typing import Union

import asyncpg
from asyncpg.pool import Pool

from data import config


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        pool = asyncpg.create_pool(
            user=config.PG_USER,
            password=config.PG_PASS,
            host=config.IP,
            database='postgres'
        )
        self.pool = pool

    async def create_table_users(self):
        sql = ""

