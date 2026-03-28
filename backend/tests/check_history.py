import asyncio
from backend.clients.postgres import AsyncSessionLocal
from backend.core.foliopp_core.database.models import ChatMessage
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(ChatMessage).order_by(ChatMessage.timestamp.desc()))
        messages = res.scalars().all()
        print(f"Total Messages: {len(messages)}")
        for m in messages:
            print(f"[{m.session_id}] {m.role}: {m.content[:50]}... (Thoughts: {len(m.thoughts) if m.thoughts else 0})")

if __name__ == "__main__":
    asyncio.run(check())
