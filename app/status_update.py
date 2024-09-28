from aiohttp import web
from supabase import create_client, Client
import os

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

async def update_job_status(request):
    try:
        data = await request.json()
        job_type = data.get('type')
        shop_id = data.get('shopId')
        job_ids = data.get('job_ids')

        if job_type == 'JOB_RECEIVED':
            await handle_job_received(job_ids, shop_id)
        elif job_type == 'JOB_COMPLETED':
            await handle_job_completed(job_ids, shop_id)
        elif job_type == 'JOB_FAILED':
            await handle_job_failed(job_ids, shop_id)
        else:
            return web.Response(status=400, text="Invalid job status update type.")

        print(f"Job status update received for shop {shop_id}: {job_type}")
        return web.Response(status=200, text="Job status update processed.")
    except Exception as e:
        print(f"Error processing job status update: {e}")
        return web.Response(status=500, text="Error processing job status update.")

async def handle_job_received(job_ids, shop_id):
    print(f"Shop {shop_id} confirmed receipt of jobs: {', '.join(job_ids)}")

    response = supabase.table('jobs').update({'status': 'IN_PROGRESS'}).in_('job_id', job_ids).execute()

    if response.get('error'):
        print(f"Error updating job status to IN_PROGRESS: {response['error']}")

async def handle_job_completed(job_ids, shop_id):
    print(f"Shop {shop_id} confirmed job completion: {', '.join(job_ids)}")

    response = supabase.table('jobs').update({'status': 'COMPLETED'}).in_('job_id', job_ids).execute()

    if response.get('error'):
        print(f"Error updating job status to COMPLETED: {response['error']}")

async def handle_job_failed(job_ids, shop_id):
    print(f"Shop {shop_id} reported job failure: {', '.join(job_ids)}")

    response = supabase.table('jobs').update({'status': 'FAILED'}).in_('job_id', job_ids).execute()

    if response.get('error'):
        print(f"Error updating job status to FAILED: {response['error']}")
