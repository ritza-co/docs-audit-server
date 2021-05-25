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
    if 'work-queue' not in db:
        db['work-queue'] = []

def get_task(task_id):
    return dict(db['tasks'][task_id])

def get_result(task_id):
    print(f"getting result for {task_id}")
    results = dict(db['results'][task_id])
    return results

def get_results():
    print("Getting results")
    t1 = datetime.now()
#     results = [dict(db['results'][result]) for result in db['results']]
    results = dict(db['results'])
    t2 = datetime.now()
    print("calculation took", t2 - t1)
    return results

'''
def get_tasks():
    tasks = [dict(db['tasks'][task]) for task in db['tasks']]
    return tasks
'''

'''
def get_recrawl_tasks():
    # tasks_to_recrawl = [dict(db['tasks'][task]) for task in db['tasks'] if db['tasks'][task]['status'] == STATUS_RECRAWL]
    tasks_to_recrawl = [db[task] for task in db['tasks'] if db['tasks'][task]['status'] == STATUS_SUBMITTED]
    return tasks_to_recrawl
'''

def get_incomplete_tasks():
    # incomplete_tasks = [dict(db['tasks'][task]) for task in db['tasks'] if db['tasks'][task]['status'] == STATUS_SUBMITTED]
    print("getting incopmlete tasks")
    incomplete_tasks = [db[task] for task in db['tasks'] if db['tasks'][task]['status'] in ( STATUS_SUBMITTED, STATUS_RECRAWL)]
    print("got, getting recrawl tasks")
    return incomplete_tasks

def create_task(task_type, input_data):
    task_id = str(uuid4())
    db['tasks'][task_id] = {
        "task_id": task_id,
        "task_type": task_type,
        "input_data": input_data,
        "status": STATUS_SUBMITTED,
        "created_at": str(datetime.utcnow())
    } #comment

def recrawl_tasks(task_ids):
    print(task_ids)
    task_ids_list = task_ids.split("//")
    print("task ids list is ", task_ids_list)
    for task_id in task_ids_list:
      print("looping ", task_id)
      task = get_task(task_id)
      task['status'] = STATUS_RECRAWL
      db['tasks'][task_id] = task

def update_task():
    #del db['tasks']['24d306cc-27b8-4bea-84ec-d15f85dffa91']
    print("Updated task")

def handle_task_creation(input_list):
    for url in input_list:
        create_task("image_audit", url)
        create_task("link_audit", url)
        print("creating lighthouse task")
        create_task("lighthouse", url)

def get_oldest_incomplete_task(requested_task_type):
    tasks = db['tasks']
    if requested_task_type:
        tasks_by_date = sorted(
            [(tasks[task]['created_at'], tasks[task]['task_id']) for task in tasks if tasks[task]['status'] in (STATUS_SUBMITTED, STATUS_RECRAWL) and tasks[task]['task_type'] == requested_task_type]
        )
    else:
        # don't give lighthouse tasks unless worker explicitly asks for them
        tasks_by_date = sorted(
            [(tasks[task]['created_at'], tasks[task]['task_id']) for task in tasks if tasks[task]['status'] in (STATUS_SUBMITTED, STATUS_RECRAWL) and tasks[task]['task_type'] != 'lighthouse']
        )
    if tasks_by_date:
        task_id = tasks_by_date[0][1]
        return dict(tasks[task_id])
    return None

def get_oldest_recrawl_task():
    tasks = db['tasks']
    tasks_by_date = sorted(
        [(tasks[task]['created_at'], tasks[task]['task_id']) for task in tasks if tasks[task]['status'] == STATUS_RECRAWL]
    )
    if tasks_by_date:
        task_id = tasks_by_date[0][1]
        return dict(tasks[task_id])
    return None

def assign_task(requested_task_type=None):
    task = get_oldest_incomplete_task(requested_task_type)
    if task:
        task_id = task['task_id']
        db['tasks'][task_id]['status'] = STATUS_PROCESSING
        db['tasks'][task_id]['assigned_at'] = str(datetime.utcnow())
        return task
    return {}

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