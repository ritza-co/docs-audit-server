# A server blueprint to define arbitrary long running tasks
#
# The server will farm out submitted tasks to one or more workers
# and save their results in its own database.

from flask import Flask
from flask import request, jsonify, redirect, url_for
from flask import render_template, make_response
from uuid import uuid4

from forms import CreateUrlForm
from flask_wtf.csrf import CSRFProtect

import task_manager
import controller
import os
import datetime

app = Flask(__name__)
app.secret_key = os.environ['secret_key']
csrf = CSRFProtect(app)
task_manager.initialise_db()


@app.route("/")
@app.route("/task", methods=["GET", "POST"])
@csrf.exempt
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


@app.route("/task-request", methods=["GET", "POST"])
@csrf.exempt
def task_request():
    if request.method == 'GET':
        print("getting task requestse")
        task_requests = task_manager.get_tasks_requests()
        print("got task requests")
        return jsonify(task_requests)
    elif request.method == 'POST':
        print("Posting task request")
        worker_id = request.json["worker_id"]
        requested_task_type = request.json.get("task_type")
        task_manager.create_task_request(worker_id)
        print("Created task request")
        task = task_manager.assign_task(requested_task_type)
        print(f"Requested task type is {requested_task_type}")
        if task:
            print(f"Assigned task {task['task_id']} to {worker_id}")
        else:
            print("No task was assigned")
        return task


@app.route("/result", methods=["GET", "POST"])
@csrf.exempt
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
        try:
          first_task = request.json["first_task"]
        except Exception as e:
          print(e)
          first_task = False
        output = request.json["output"]

        print(
            f"Worker {worker_id} submitting {task_type} task results with id {task_id}"
        )

        task_manager.create_result(worker_id, task_id, task_type, task_url, first_task, output)
        return {}


@app.route("/status", methods=["GET", "POST"])
def status():
    # worker bots POST the status, workers and humans GET the status
    pass


# @app.route("/", methods=["GET", "POST"]
# @app.route("/dashboard", methods=["GET", "POST"]

# if get
## ## show the dashboard

# if post

#### create the tasks
##### set message variable
##### return the dashboard with message=


@app.route("/queue")
def queue():
    tasks = task_manager.get_incomplete_tasks()
    return render_template("tasks.html", tasks=tasks)

@app.route("/projects")
def projects():
    tasks = task_manager.get_incomplete_tasks()
    projects = controller.get_projects()
    form = CreateUrlForm()

    return render_template("projects.html",form=form,tasks=tasks,
                          projects=projects)


@app.route("/dashboard/<user_id>", methods=["GET", "POST"])
@csrf.exempt
def dashboard_user(user_id):
    if request.method == 'GET':
        if user_id:
          collection = controller.get_user_project(user_id)
        else:
          collection = {}
        form = CreateUrlForm()

        return render_template("dashboard.html",form=form,collection=collection)
    elif request.method == 'POST':
        form = CreateUrlForm(request.form)
        if form.validate_on_submit():
          input_data = form.url.data.strip()
          #input_data = request.form['input_data'].strip()
          clean_urls_list = controller.remove_id_ref_from_url(input_data)
          previously_audited = controller.check_if_site_exists(
              clean_urls_list[0])
          if previously_audited:
              resp = make_response(redirect(url_for('details', page_url=clean_urls_list[0])))
              if user_id is None:
                user_id = str(uuid4())
              resp.set_cookie('userID', user_id, expires=datetime.datetime.now() + datetime.timedelta(days=30))
              controller.set_cookie_project(user_id,clean_urls_list[0])
              return resp
          else:
              task_manager.handle_task_creation(clean_urls_list)
              resp = make_response(render_template('dashboard.html',form=CreateUrlForm(),message="Data Submitted"))
              if user_id is None:
                user_id = str(uuid4())
              resp.set_cookie('userID', user_id, expires=datetime.datetime.now() + datetime.timedelta(days=30))
              controller.set_cookie_project(user_id,clean_urls_list[0])
              return resp
        else:
          tasks = task_manager.get_incomplete_tasks()
          projects = controller.get_projects()
          form = CreateUrlForm()

          return render_template("dashboard.html",
                                form=form,
                                tasks=tasks,
                                projects=projects)

@app.route("/dashboard", methods=["GET", "POST"])
@csrf.exempt
def dashboard():
    if request.method == 'GET':
        # try:
        #   user_id = request.cookies.get('userID')
        # except Exception as e:
        #   print(e)
        # if user_id:
        #   collection = controller.get_user_project(user_id)
        # else:
        #   collection = {}        
        return render_template("dashboard.html",form=CreateUrlForm())
    elif request.method == 'POST':
        try:
          user_id = request.cookies.get('userID')
        except Exception as e:
          user_id = str(uuid4())
          print(e)

        form = CreateUrlForm(request.form)
        if form.validate_on_submit():
          input_data = form.url.data.strip()
          #input_data = request.form['input_data'].strip()
          clean_urls_list = controller.remove_id_ref_from_url(input_data)
          previously_audited = controller.check_if_site_exists(
              clean_urls_list[0])
          if previously_audited:
              resp = make_response(redirect(url_for('details', page_url=clean_urls_list[0])))
              if user_id is None:
                user_id = str(uuid4())
              resp.set_cookie('userID', user_id, expires=datetime.datetime.now() + datetime.timedelta(days=30))
              controller.set_cookie_project(user_id,clean_urls_list[0])
              return resp
          else:
              task_manager.handle_task_creation(clean_urls_list)
              resp = make_response(render_template('dashboard.html',form=CreateUrlForm(),message="Data Submitted"))
              if user_id is None:
                user_id = str(uuid4())
              resp.set_cookie('userID', user_id, expires=datetime.datetime.now() + datetime.timedelta(days=30))
              controller.set_cookie_project(user_id,clean_urls_list[0])
              return resp
        else:
          tasks = task_manager.get_incomplete_tasks()
          projects = controller.get_projects()
          form = CreateUrlForm()

          return render_template("dashboard.html",
                                form=form,
                                tasks=tasks,
                                projects=projects)
        #urls_list = controller.separate_urls(input_data)
        #print(urls_list)
        #clean_urls_list = controller.remove_id_ref_from_url(urls_list)




@app.route('/collection')
def view_results_collection():
    return render_template('view-results-collection.html')


@app.route('/view')
def view_audit_results():
    return render_template('view-results.html')


@app.route('/recrawl', methods=['POST', 'GET'])
@csrf.exempt
def recrawl():
    if request.method == 'GET':
        return f"Use the '/' url to submit form"
    if request.method == 'POST':
        task_ids = request.form['task_ids']
        print(task_ids, 'trailing slash weirdly added here')
        task_manager.recrawl_tasks(task_ids)
        return redirect("/dashboard")


@app.route('/project_details', methods=['POST', 'GET'])
def project_details():
    if request.method == 'GET':
        docs = request.args.get("docs_base_url")
        audit_results = controller.collection_results(docs)
        return render_template('display-collection.html',
                               url=docs,
                               collection=audit_results)
    if request.method == 'POST':
        form_data = request.form['Url']

        if 'http' in form_data:
            url = form_data.split("//")[1]
        else:
            url = form_data

        clean_url = controller.remove_id_ref_and_trailing_slash(url)
        base_url = clean_url.split("/")[0]
        audit_results = controller.collection_results(base_url)
        return render_template('display-collection.html',
                               url=form_data,
                               collection=audit_results)


@app.route('/view-or-audit', methods=['POST', 'GET'])
def view_or_audit():
    if request.method == 'GET':
        url = request.args.get("page_url").split("__")[0]
        previous_page = request.args.get("page_url").split("__")[1]
        audit_results = controller.get_result_for_url(url)
        if audit_results:
            return redirect(url_for('details', page_url=url))
        else:
            url_list = [url]
            task_manager.handle_task_creation(url_list)
            return redirect(
                url_for('details',
                        page_url=previous_page,
                        message="Page Added!"))
    elif request.method == 'POST':
        # Do nothing
        return redirect("/dashboard")


@app.route('/details', methods=['POST', 'GET'])
def details():
    if request.method == 'GET':
        url = request.args.get("page_url")
        try:
            message = request.args.get("message")
        except Exception as e:
            print(e)
            message = None

        audit_results = controller.get_result_for_url(url)
        print("_____")
        print(audit_results['task_ids'])
        print("***")

        if message:
            return render_template('display.html',
                                   url=url,
                                   images=audit_results['images'],
                                   results=audit_results,
                                   total_images=audit_results['image_count'],
                                   task_ids=audit_results['task_ids'],
                                   message=message)
        else:
            return render_template('display.html',
                                   url=url,
                                   images=audit_results['images'],
                                   results=audit_results,
                                   total_images=audit_results['image_count'],
                                   task_ids=audit_results['task_ids'])
    if request.method == 'POST':
        form_data = request.form['Url']

        if 'http' in form_data:
            url = form_data.split("//")[1]
        else:
            url = form_data

        clean_url = controller.remove_id_ref_and_trailing_slash(url)
        audit_results = controller.get_result_for_url(clean_url)
        return render_template('display.html',
                               url=clean_url,
                               images=audit_results['images'],
                               links=audit_results,
                               total_images=audit_results['image_count'],
                               task_ids=audit_results['task_ids'])


@app.route('/delete-project', methods=['DELETE'])
def delete_project():
    if request.method == 'DELETE':
        project_base_url = request.get_json()["project_base_url"]
        controller.delete_project(project_base_url)
        print(f"Project {project_base_url} deleted!")

        #projects = controller.get_projects()
        return jsonify({
          "url": url_for('projects')
        })



##############################

@app.route("/progress", methods=["GET"])
def progress():
    return jsonify({
        "progress": len(task_manager.get_incomplete_tasks()) 
    })


@app.route('/audit_page', methods=['POST'])
def audit_page():
    if request.method == 'POST':
      try:
        user_id = request.cookies.get('userID')
      except Exception as e:
        user_id = str(uuid4())
        print(e)

      url = request.get_json()
      url_list = []
      url_list.append(url)
      task_manager.handle_task_creation(url_list)
      resp = make_response( jsonify({'msg':'auditing'}))
      if user_id is None:
        user_id = str(uuid4())
      resp.set_cookie('userID', user_id, expires=datetime.datetime.now() + datetime.timedelta(days=30))
      controller.set_cookie_project(user_id,url)
      return resp


@app.route("/myprojects", methods=["GET"])
def myprojects():
    if request.method == 'GET':
        try:
          user_id = request.cookies.get('userID')
        except Exception as e:
          print(e)
        if user_id:
          collection = controller.get_user_project(user_id)
        else:
          collection = {}

        return jsonify(collection)


@app.route("/submittask", methods=["POST"])
def submittask():
    if request.method == 'POST':
        try:
          user_id = request.cookies.get('userID')
        except Exception as e:
          user_id = str(uuid4())
          print(e)

        form = CreateUrlForm(request.form)
        if form.validate_on_submit():
          input_data = form.url.data.strip()
          clean_urls_list = controller.remove_id_ref_from_url(input_data)
          previously_audited = controller.check_if_site_exists(
              clean_urls_list[0])
          if previously_audited:
              resp = make_response( jsonify({'formValid':'yes','previouslyAudited': 'yes', 'pageUrl': url_for('details') +'?page_url='+clean_urls_list[0]}))
              if user_id is None:
                user_id = str(uuid4())
              resp.set_cookie('userID', user_id, expires=datetime.datetime.now() + datetime.timedelta(days=30))
              controller.set_cookie_project(user_id,clean_urls_list[0])
              return resp
          else:
              task_manager.handle_task_creation(clean_urls_list)
              resp = make_response( jsonify({'formValid':'yes','previouslyAudited': 'no', 'pageUrl': ''}))
              if user_id is None:
                user_id = str(uuid4())
              resp.set_cookie('userID', user_id, expires=datetime.datetime.now() + datetime.timedelta(days=30))
              controller.set_cookie_project(user_id,clean_urls_list[0])
              return resp
        else:
          resp = make_response( jsonify({'formValid':'no','previouslyAudited': 'no', 'pageUrl': ''}))
          return resp


@app.route("/reset-project", methods=["DELETE"])
def reset_project():
    # resp =  make_response(jsonify({'deleted': 'yes'}))
    # resp.set_cookie('userID', '', expires = datetime.datetime.now())
    # return resp
    try:
      url= request.get_json()["project_base_url"]
      user_id = request.cookies.get('userID')
      controller.remove_key(user_id,url)
      return jsonify({'deleted': 'yes'})
    except Exception as e:
      print('tatenda')
      print(e)
    return jsonify({'deleted': 'no'})
    


def sandbox():
    from replit import db
    from datetime import datetime
    print(task_manager.get_oldest_incomplete_task())


if __name__ == '__main__':
    #app.run("0.0.0.0")
    app.run("0.0.0.0", debug=True)
