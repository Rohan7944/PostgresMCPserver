from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

import asyncpg
from mcp.server.fastmcp import FastMCP, Context

# Async PostgreSQL wrapper using asyncpg
class Database:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    @classmethod
    async def connect(cls) -> "Database":
        pool = await asyncpg.create_pool(
            user="postgres",
            password="rohan",
            database="company",
            host="localhost",
            port=5432,
        )
        return cls(pool)

    async def disconnect(self):
        await self.pool.close()

    async def query(self, query: str) -> list:
        async with self.pool.acquire() as conn:
            try:
                return await conn.fetch(query)
            except Exception as e:
                print(f"Query error: {e}")
                return []

    async def fetch_schema(self) -> list:
        query = """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        """
        return await self.query(query)


@dataclass
class AppContext:
    db: Database


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    db = await Database.connect()
    try:
        yield AppContext(db=db)
    finally:
        await db.disconnect()


mcp = FastMCP("PostgresMCPServer", lifespan=app_lifespan)

@mcp.tool("fetch_schema")
async def fetch_schema(ctx: Context) -> str:
    db = ctx.request_context.lifespan_context.db
    schema = await db.fetch_schema()
    return str([record["table_name"] for record in schema])


@mcp.tool("fetch_all_tables")
async def fetch_all_tables(ctx: Context) -> str:
    db = ctx.request_context.lifespan_context.db
    query = "SELECT * FROM information_schema.tables WHERE table_schema='public'"
    tables = await db.query(query)
    return str(tables)


@mcp.tool("run_query")
async def run_query(ctx: Context, query: str) -> str:
    db = ctx.request_context.lifespan_context.db
    result = await db.query(query)
    return str(result)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run()
