#!/usr/bin/env python3
import asyncio
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer

async def init_database():
    data_layer = SQLAlchemyDataLayer(conninfo="sqlite+aiosqlite:///./chainlit.db")
    # Initialize the data layer which creates tables
    await data_layer.build_debug_url()
    print("Database initialized successfully")

if __name__ == "__main__":
    asyncio.run(init_database())