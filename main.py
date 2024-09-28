import os
import asyncio
from aiohttp import web
from supabase import create_client, Client
import job_management
import websocketclient
import status_update

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

async def health_check(request):
    return web.json_response({"status": "API is running", "timestamp": datetime.utcnow().isoformat()})

async def fetch_jobs(request):
    try:
        jobs = supabase.table('jobs').select('*').execute()
        return web.json_response(jobs)
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return web.json_response({'error': 'Failed to fetch jobs'}, status=500)

async def process_jobs_handler(request):
    websocket = request.app['websocket']
    try:
        await job_management.process_jobs(websocket)
        return web.Response(text="Job processing started.")
    except Exception as e:
        print(f"Error processing jobs: {e}")
        return web.Response(text="Error processing jobs.", status=500)

app = web.Application()
app.router.add_get('/health', health_check)
app.router.add_get('/jobs', fetch_jobs)
app.router.add_get('/process-jobs', process_jobs_handler)
app.router.add_post('/update-job-status', status_update.update_job_status)

# Maintain WebSocket connection
app['websocket'] = await websocketclient.connect_websocket()

# Reconnect logic if WebSocket connection is lost
async def maintain_websocket_connection(app):
    while True:
        websocket = app['websocket']
        if not websocket or websocket.closed:
            print('Reconnecting to WebSocket server...')
            app['websocket'] = await websocketclient.connect_websocket()
        await asyncio.sleep(5)

app.on_startup.append(lambda app: asyncio.create_task(maintain_websocket_connection(app)))

web.run_app(app, port=os.getenv('PORT', 3000))
