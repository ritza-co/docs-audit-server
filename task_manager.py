from replit import db
from uuid import uuid4
from datetime import datetime

STATUS_SUBMITTED = "submitted"
STATUS_RECRAWL = "recrawl"
STATUS_PROCESSING = "processing"
STATUS_DONE = "done"
STATUS_FAILED = "failed"

def initialise_db():
    if 'tasks' not in db:
        db['tasks'] = {}
    if 'task-requests' not in db:
        db['task-requests'] = {}
    if 'results' not in db:
        db['results'] = {}

def get_task(task_id):
    return dict(db['tasks'][task_id])

def get_result(task_id):
    return dict(db['results'][task_id])

def get_results():
    results = [dict(db['results'][result]) for result in db['results']]
    return results

def get_tasks():
    tasks = [dict(db['tasks'][task]) for task in db['tasks']]
    return tasks

def get_incomplete_tasks():
    incomplete_tasks = [dict(db['tasks'][task]) for task in db['tasks'] if db['tasks'][task]['status'] == STATUS_SUBMITTED]
    return incomplete_tasks

def create_task(task_type, input_data):
    task_id = str(uuid4())
    db['tasks'][task_id] = {
        "task_id": task_id,
        "task_type": task_type,
        "input_data": input_data,
        "status": STATUS_SUBMITTED,
        "created_at": str(datetime.utcnow())
    }

def recrawl_tasks(task_ids):
    print(task_ids)
    task_ids_list = task_ids.split(" // ")
    for task_id in task_ids_list:
      task = get_task(task_id)
      task['status'] = STATUS_RECRAWL
      db['tasks'][task_id] = task

def update_task():
    #db['tasks']['001f2a5e-2635-46ec-9050-f00fb37c5635']['status'] = STATUS_DONE
    print("Updated task")

def handle_task_creation(input_list):
    for url in input_list:
        create_task("image_audit", url)
        create_task("link_audit", url)

def get_oldest_incomplete_task():
    tasks = db['tasks']
    tasks_by_date = sorted(
        [(tasks[task]['created_at'], tasks[task]['task_id']) for task in tasks if tasks[task]['status'] == STATUS_SUBMITTED]
    )
    if tasks_by_date:
        task_id = tasks_by_date[0][1]
        return dict(tasks[task_id])
    return None

def assign_task():
    task = get_oldest_incomplete_task()
    if not task:
        return {}
    task_id = task['task_id']
    db['tasks'][task_id]['status'] = STATUS_PROCESSING
    db['tasks'][task_id]['assigned_at'] = str(datetime.utcnow())
    return task

def get_task_requests():
    return [dict(db['task-requests'][request]) for request in db['task-requests']]

def create_task_request(worker_id):
    request_id = str(uuid4())
    db['task-requests'][request_id] = {
        "request_id": request_id,
        "worker_id": worker_id,
        "created_at": str(datetime.now())
    }
    return request_id

def create_result(worker_id, task_id, task_type, task_url, output):
    db['results'][task_id] = {
        "task_id": task_id,
        "task_url": task_url,
        "task_type": task_type,
        "worker_id": worker_id,
        "output": output
    }

    db['tasks'][task_id]['status'] = STATUS_DONE
    db['tasks'][task_id]['completed_at'] = str(datetime.now())