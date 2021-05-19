# A server blueprint to define arbitrary long running tasks
# 
# The server will farm out submitted tasks to one or more workers 
# and save their results in its own database.

from flask import Flask
from flask import request, jsonify, redirect
from flask import render_template

import task_manager
import controller

app = Flask(__name__)
task_manager.initialise_db()

@app.route("/")
@app.route("/task", methods=["GET","POST"])
def task():
    if request.method == 'GET':
        return redirect("/dashboard")
    elif request.method == 'POST':
        input_data = request.form['input_data'].strip()
        urls_list = controller.separate_urls(input_data)
        print(urls_list)
        clean_urls_list = controller.remove_id_ref_from_url(urls_list)
        task_manager.handle_task_creation(clean_urls_list)
        return redirect("/dashboard-submit")

@app.route("/task-request",methods=["GET","POST"])
def task_request():
    if request.method == 'GET':
        task_requests = task_manager.get_tasks_requests()
        return jsonify(task_requests) 
    elif request.method == 'POST':
        worker_id = request.json["worker_id"]
        task_manager.create_task_request(worker_id)
        task = task_manager.assign_task()
        return task
     
@app.route("/result", methods=["GET", "POST"])
def result():
    # worker bots POST results, humans GET results
    if request.method == "GET":
        task_id = request.args.get("task_id")
        task = task_manager.get_task(task_id)
        result = task_manager.get_result(task_id)
        return render_template("result.html", task=task, result=result)
    elif request.method == "POST":
        worker_id = request.json["worker_id"]
        task_id = request.json["task_id"]
        task_url = request.json["task_url"]
        task_type = request.json["task_type"]
        output = request.json["output"]

        task_manager.create_result(worker_id, task_id, task_type, task_url, output)
        return {}

@app.route("/status", methods=["GET", "POST"])
def status():
    # worker bots POST the status, workers and humans GET the status
    pass

@app.route("/dashboard")
def dashboard():
    tasks = task_manager.get_tasks()
    projects = controller.get_projects()
    print(tasks)
    return render_template("dashboard.html", tasks=tasks, projects=projects)

@app.route("/dashboard-submit")
def dashboard_submit():
    tasks = task_manager.get_tasks()
    projects = controller.get_projects()
    print(tasks)
    return render_template("dashboard.html", tasks=tasks, projects=projects, message="Data Submitted")

@app.route('/collection')
def view_results_collection():
    return render_template('view-results-collection.html')

@app.route('/view')
def view_audit_results():
    return render_template('view-results.html')

@app.route('/recrawl', methods = ['POST', 'GET'])
def recrawl():
    if request.method == 'GET':
        return f"Use the '/' url to submit form"
    if request.method == 'POST':
        form_data = request.form['Url']
        print(f"Running link audit for {form_data} ...")
        print(form_data)
        if not form_data.startswith("http"):
            form_data = "https://" + form_data
        return redirect("/dashboard")

@app.route('/results-collection', methods = ['POST', 'GET'])
def collection():
    if request.method == 'GET':
        return f"Use the '/' url to submit form"
    if request.method == 'POST':
        form_data = request.form['Url']
        audit_results = controller.collection_results(form_data.split("//")[1])
        return render_template('display-collection.html', url = form_data, collection=audit_results)

@app.route('/project_details', methods = ['POST', 'GET'])
def project_details():
    if request.method == 'GET':
        docs = request.args.get("docs_base_url")
        audit_results = controller.collection_results(docs)
        return render_template('display-collection.html', url = docs, collection=audit_results)
    if request.method == 'POST':
        form_data = request.form['Url']
        audit_results = controller.collection_results(form_data)
        return render_template('display-collection.html', url = form_data, collection=audit_results)

@app.route('/details', methods = ['POST', 'GET'])
def details():
    if request.method == 'GET':
        url = request.args.get("page_url")
        audit_results = controller.get_result_for_url(url)
        return render_template('display.html', url = url, images=audit_results['oversized_images'], links=audit_results, total_images=audit_results['image_count'])
    if request.method == 'POST':
        form_data = request.form['Url']
        task_id = 'test'
        print(form_data)
        audit_results = task_manager.get_result(task_id)
        return render_template('display.html', url = form_data, images=audit_results['oversized_images'], links=audit_results, total_images=audit_results['image_count'])

@app.route('/search', methods = ['POST', 'GET'])
def search():
    if request.method == 'GET':
        return f"Use the '/' url to submit form"
    if request.method == 'POST':
        form_data = request.form['Url']
        no_id_ref_url = form_data.split('#')
        audit_results = controller.search_url(no_id_ref_url)
        #audit_results = db[no_id_ref_url[0].split("//")[1]]
        return render_template('display.html', url = form_data, images=audit_results['oversized_images'], links=audit_results, total_images=audit_results['image_count'])
        
def sandbox():
    from replit import db
    from datetime import datetime
    print(task_manager.get_oldest_incomplete_task())


if __name__ == '__main__':
    app.run("0.0.0.0")