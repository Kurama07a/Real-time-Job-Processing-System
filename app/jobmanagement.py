import os
from datetime import datetime
from supabase import create_client, Client
from websocketclient import send_to_websocket

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

async def process_jobs(websocket):
    try:
        jobs = await fetch_jobs_by_status('UPLOADED')

        if not jobs:
            print('No jobs to process.')
            return

        grouped_jobs = group_jobs_by_shop(jobs)

        for shop_id, shop_jobs in grouped_jobs.items():
            await send_jobs_to_websocket(websocket, shop_id, shop_jobs)

        print('Job processing completed.')
    except Exception as e:
        print(f"Error in job processing: {e}")

async def fetch_jobs_by_status(status):
    response = supabase.table('jobs').select('*').eq('status', status).order('created_at', asc=True).execute()
    if response.get('error'):
        raise Exception(f"Error fetching jobs: {response['error']['message']}")
    return response['data']

def group_jobs_by_shop(jobs):
    grouped_jobs = {}
    for job in jobs:
        if job['shop_id'] not in grouped_jobs:
            grouped_jobs[job['shop_id']] = []
        grouped_jobs[job['shop_id']].append(job)
    return grouped_jobs

async def send_jobs_to_websocket(websocket, shop_id, jobs):
    payload = {
        'type': 'new_jobs',
        'shopId': shop_id,
        'jobs': [{
            'job_id': job['job_id'],
            'shop_id': job['shop_id'],
            'size': job['size'],
            'copies': job['copies'],
            'start_page': job['start_page'],
            'end_page': job['end_page'],
            'file': job['files'],
            'color_mode': job['color_mode'],
            'orientation': job['orientation'],
            'paper_size': job['paper_size'],
            'duplex': job['duplex'],
            'source': job['source'],
        } for job in jobs]
    }

    await send_to_websocket(websocket, payload)

    for job in jobs:
        await assign_job(job)
        await update_job_status(job['job_id'], 'IN TRANSITION')
        await update_shop_workload(job['shop_id'], job['size'], job['copies'])

async def assign_job(job):
    response = supabase.table('job_assignment').insert({
        'job_id': job['job_id'],
        'shop_id': job['shop_id'],
        'uid': job['uid'],
        'created_at': datetime.utcnow().isoformat()
    }).execute()

    if response.get('error'):
        raise Exception(f"Error inserting job assignment: {response['error']['message']}")

async def update_job_status(job_id, status):
    response = supabase.table('jobs').update({'status': status}).eq('job_id', job_id).execute()

    if response.get('error'):
        raise Exception(f"Error updating job status: {response['error']['message']}")

async def update_shop_workload(shop_id, job_size, copies):
    response = supabase.table('institute_print_shops').select('current_workload').eq('shop_id', shop_id).single().execute()

    if response.get('error'):
        raise Exception(f"Error fetching shop data: {response['error']['message']}")

    new_workload = response['data']['current_workload'] + job_size * copies

    update_response = supabase.table('institute_print_shops').update({'current_workload': new_workload}).eq('shop_id', shop_id).execute()

    if update_response.get('error'):
        raise Exception(f"Error updating shop workload: {update_response['error']['message']}")
