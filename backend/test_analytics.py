import asyncio
import httpx
import json

async def test_analytics():
    async with httpx.AsyncClient() as client:
        # First trigger seed to have data
        r = await client.post('http://localhost:8000/api/seed')
        await asyncio.sleep(2) # Wait for some simulation events
        f = await client.get('http://localhost:8000/api/analytics/flow')
        print("Flow:", len(f.json()), "nodes")
        c = await client.get('http://localhost:8000/api/analytics/congestion')
        print("Congestion:", json.dumps(c.json()[:2], indent=2))
            
asyncio.run(test_analytics())
