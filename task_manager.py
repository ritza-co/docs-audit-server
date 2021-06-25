from replit import db
from uuid import uuid4
from datetime import datetime
import controller

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
    if 'queued-tasks' not in db:
        db['queued-tasks'] = {}
    if 'failed-tasks' not in db:
        db['failed-tasks'] = {}
    if 'user-ids' not in db:
        db['user-ids'] = {}

def reset_db():
    db['tasks'] = {}
    db['results'] = {}
    db['queued-tasks'] = {}
    db['failed-tasks'] = {}
    db['user-ids'] = {}

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
    # return dict(db['queued-tasks'])
    try:
      return [dict(db['queued-tasks'][task]) for task in db['queued-tasks']]
    except Exception as e:
      print(e)
      return []
    '''
    # incomplete_tasks = [dict(db['tasks'][task]) for task in db['tasks'] if db['tasks'][task]['status'] == STATUS_SUBMITTED]
    print("getting incopmlete tasks")
    incomplete_tasks = [db[task] for task in db['tasks'] if db['tasks'][task]['status'] in ( STATUS_SUBMITTED, STATUS_RECRAWL)]
    print("got, getting recrawl tasks")
    return incomplete_tasks
    '''

def create_first_task(task_type, input_data):
    task_id = str(uuid4())
    task = {
        "task_id": task_id,
        "task_type": task_type,
        "input_data": input_data,
        "first_task": True,
        "status": STATUS_SUBMITTED,
        "created_at": str(datetime.utcnow())
    }
    db['tasks'][task_id] = task
    db['queued-tasks'][task_id] = task
    print(f"Created first task for {input_data}")

def create_task(task_type, input_data):
    task_id = str(uuid4())
    task = {
        "task_id": task_id,
        "task_type": task_type,
        "input_data": input_data,
        "first_task": False,
        "status": STATUS_SUBMITTED,
        "created_at": str(datetime.utcnow())
    }
    db['tasks'][task_id] = task
    db['queued-tasks'][task_id] = task

def recrawl_tasks(task_ids):
    print(task_ids)
    task_ids_list = task_ids.split("//")
    print("task ids list is ", task_ids_list)
    for task_id in task_ids_list:
      if task_id: #check if task_id isn't empty string
        print("looping ", task_id)
        task = get_task(task_id)
        task['status'] = STATUS_RECRAWL
        task['first_task'] = False
        db['tasks'][task_id] = task
        db['queued-tasks'][task_id] = task

def update_task():
    del db['tasks']['cd1c1ea5-fe79-4fad-a580-4f2cca5c24d3']
    del db['results']['cd1c1ea5-fe79-4fad-a580-4f2cca5c24d3']
    del db['tasks']['88e29a14-4c94-464f-8ba5-3e854b4e0a5f']
    del db['results']['88e29a14-4c94-464f-8ba5-3e854b4e0a5f']
    del db['tasks']['4b4e9f42-b4ea-45a2-8a6f-19a5c25eed56']
    del db['results']['4b4e9f42-b4ea-45a2-8a6f-19a5c25eed56']
    print("Updated task")

def handle_task_creation(input_list):
    for url in input_list:
        project_exists = controller.check_if_project_exists(url)
        if project_exists:
          create_task("image_audit", url)
          create_task("link_audit", url)
          create_task("lighthouse", url)
        else:
          create_task("image_audit", url)
          create_first_task("link_audit", url)
          create_task("lighthouse", url)

def handle_additional_task_creation(url):
    create_task("image_audit", url)
    create_task("link_audit", url)
    create_task("lighthouse", url)

def create_additional_tasks(first_task_url, link_audit_results):
    all_links = link_audit_results['all_links']
    working_links = all_links[1]

    for link in working_links:
      print(f"Looping {link['link']}")
      absolute = link['link']
      if first_task_url in absolute:
        print(f"Absolute {absolute} added")
        handle_additional_task_creation(absolute)

def get_oldest_incomplete_task(requested_task_type):
    tasks = db['queued-tasks']
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
        try:
          task_id = task['task_id']
          print(f"1 {task_id}")
          db['tasks'][task_id]['status'] = STATUS_PROCESSING
          print("2")
          db['tasks'][task_id]['assigned_at'] = str(datetime.utcnow())
          print("3")
          db['queued-tasks'][task_id] = task
          return task
        except Exception as e:
          task_id = task['task_id']
          print("2nd Exception")
          print(e)
          print("End of 2nd Exception")
          del db['queued-tasks'][task_id]
          print("Deleted!")
          return {}
    return {}

def get_task_requests():
    return [dict(db['task-requests'][request]) for request in db['task-requests']]

def create_task_request(worker_id):
    request_id = str(uuid4())
    req = {
        "request_id": request_id,
        "worker_id": worker_id,
        "created_at": str(datetime.now())
    }
    print(req)
    try:
      db['task-requests'][request_id] = req
    except Exception as e:
      print("===")
      print(e)
      print("===")
    return request_id

def create_result(worker_id, task_id, task_type, task_url, first_task, output):
    if type(output) == type({}):
      if task_id in db['results']:
        db['results'][task_id]['output'] = output
        print("Recrawl results submitted!")
      else:
        result = {
            "task_id": task_id,
            "task_url": task_url,
            "task_type": task_type,
            "worker_id": worker_id,
            "output": output
        }
        try:
          db['results'][task_id] = result
        except Exception as e:
            print("Couldn't save result")
            print(result)
            print(e)
      if task_id in db['queued-tasks']:
          del db['queued-tasks'][task_id]
          print(f"Queued tasks dict updated. {task_type} task with id {task_id} removed. Submitted by worker {worker_id}")
      db['tasks'][task_id]['status'] = STATUS_DONE
      db['tasks'][task_id]['completed_at'] = str(datetime.now())

      # Check if results submitted were a first task
      if first_task:
        create_additional_tasks(task_url, output)

    # Check if worker failed to complete the job
    elif type(output) == type(None):
      db['failed-tasks'][task_id] = {
            "task_id": task_id,
            "task_url": task_url,
            "task_type": task_type,
            "worker_id": worker_id,
            "output": output
      }
      if task_id in db['queued-tasks']:
          del db['queued-tasks'][task_id]
          print(f"Queued tasks dict updated. {task_type} task with id {task_id} removed. Failed by worker {worker_id}")
      db['tasks'][task_id]['status'] = STATUS_FAILED
      db['tasks'][task_id]['failed_at'] = str(datetime.now())