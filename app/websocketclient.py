import os
import json
import asyncio
import websockets
from supabase import create_client, Client

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

async def connect_websocket():
    ws_url = os.getenv('WS_SERVER_URL', 'ws://localhost:8080')
    async with websockets.connect(ws_url) as websocket:
        print("Connected to WebSocket server")
        await handle_websocket(websocket)

async def handle_websocket(websocket):
    try:
        async for message in websocket:
            await handle_websocket_message(message)
    except websockets.ConnectionClosed:
        print("WebSocket connection closed")
        await asyncio.sleep(5)
        await connect_websocket()

async def handle_websocket_message(message):
    data = json.loads(message)
    print("Message from WebSocket server:", data)

    if data.get('type') == 'job_status_update':
        await update_job_status_from_shop(data['jobIds'], data['status'])

async def send_to_websocket(websocket, payload):
    if websocket.open:
        await websocket.send(json.dumps(payload))
        print(f"Sent payload to WebSocket server: {json.dumps(payload)}")
    else:
        print("WebSocket is not open. Failed to send message.")

async def update_job_status_from_shop(job_ids, status):
    response = supabase.table('jobs').update({'status': status}).in_('job_id', job_ids).execute()

    if response.get('error'):
        print(f"Error updating job status from WebSocket message: {response['error']}")
    else:
        print(f"Successfully updated job statuses for jobs: {', '.join(job_ids)}")
