import asyncio
import websockets
import httpx
import json

async def test_ws():
    # Hit seed endpoint
    async with httpx.AsyncClient() as client:
        r = await client.post('http://localhost:8000/api/seed')
        print("Seed response:", r.json())
        
    # Connect to WS and wait for a few events
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        print("Connected to WS.")
        for _ in range(10):
            msg = await ws.recv()
            data = json.loads(msg)
            print("Received event:", data['type'], "for plate:", data['data'].get('plate', 'unknown'))
            if data['type'] == 'alert':
                print(">>> WATCHLIST ALERT FIRED <<<", data['data']['message'])
            
asyncio.run(test_ws())
