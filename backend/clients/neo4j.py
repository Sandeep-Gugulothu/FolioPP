from neo4j import AsyncGraphDatabase
from backend.config import settings

class Neo4jClient:
    def __init__(self, uri, user, password):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        await self.driver.close()

    async def execute_query(self, query, parameters=None):
        async with self.driver.session() as session:
            result = await session.execute_read(self._run_query, query, parameters)
            return result

    @staticmethod
    async def _run_query(tx, query, parameters):
        result = await tx.run(query, parameters)
        return [record.data() for record in await result.list()]

neo4j_client = Neo4jClient(
    settings.NEO4J_URI, 
    settings.NEO4J_USER, 
    settings.NEO4J_PASSWORD
)
