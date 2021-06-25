import task_manager
from datetime import datetime
from replit import db

def separate_urls(form_input):
    urls_list = form_input.split("\r\n")
    return urls_list

def get_result_for_url(url):
    url_task_results = get_task_results(url)
    if len(url_task_results) > 0:
      audit_results = create_result_dict(url_task_results)
      return audit_results
    else:
      return {'total_links':0,'broken_links':[],'working_links':[],'link_audit_time':"Not available",'broken_status_codes':[],'total_link_issues':0,'images':[],'right_size_images':[],'broken_images':[],'image_broken_status_codes':[],'total_image_issues':[],'image_count':0,'lighthouse':[]}

def remove_key(user_id, url):
    try:
      existing_urls = get_user_base_url(user_id)
      if url in existing_urls:
        existing_urls.remove(url)
        db['user-ids'][user_id] = existing_urls
        #del db['user-ids'][user_id][url]
    except Exception as e:
      print(e)

def get_user_base_url(user_id):
    return db['user-ids'][user_id]

def get_user_project(user_id):
    user_urls = get_user_base_url(user_id)
    if type(user_urls) == type(""):
      project_dict = collection_results(user_urls)
    else: #type(user_urls) == type([])
      project_dict = user_id_projects(user_urls)
    return project_dict

def set_cookie_project(user_id, url):
    try:
      user_url = url.split('//')[1]
    except Exception as e:
      print(e)
      user_url = url

    user_base_url = user_url.split('/')[0]

    try:
      existing_urls = get_user_base_url(user_id)
    except Exception as e:
      print(e)
      db['user-ids'][user_id] = []
      existing_urls = db['user-ids'][user_id]

    if str(type(existing_urls)) == "<class 'replit.database.database.ObservedList'>":
      # DO nothing if the url is already assigned to that user
      if user_base_url not in existing_urls:
        existing_urls.append(user_base_url)
      db['user-ids'][user_id] = existing_urls

    elif type(existing_urls) == type("string"):
      if user_base_url != existing_urls:
        user_urls = [existing_urls,user_base_url]
      else:
        user_urls = [existing_urls]
      db['user-ids'][user_id] = user_urls

    else:
      db['user-ids'][user_id] = [user_base_url]


def remove_trailing_slash(url):
    if len(url) > 0 and url[-1] == '/':
      clean_url = url[:-1]
    else:
      clean_url = url
    return clean_url

def remove_id_ref_from_url(urls_list):
    urls_list_with_no_ref = []

    if type(urls_list) == type([]):
      for url in urls_list:
        no_ref_url = url.split('#')
        no_slash_url = remove_trailing_slash(no_ref_url[0])
        urls_list_with_no_ref.append(no_slash_url)
    else:
      no_ref_url = urls_list.split('#')
      no_slash_url = remove_trailing_slash(no_ref_url[0])
      urls_list_with_no_ref.append(no_slash_url)
    print("Returning url list with no ref")
    return urls_list_with_no_ref

def remove_id_ref_and_trailing_slash(url):
    no_ref_url = url.split('#')[0]
    clean_url = remove_trailing_slash(no_ref_url)
    return clean_url

def delete_project(base_url):
    results = task_manager.get_results()
    print("got results")
    for r in results:
      result = results[r]
      #print("==")
      url_list = result['task_url'].split("//")[1]
      result_base_url = url_list.split("/")[0]
      if result_base_url == base_url:
        del db['results'][r]

def check_if_site_exists(input_url):
    results = task_manager.get_results()
    print("got results")
    for r in results:
      result = results[r]
      #print("==")
      result_url = result['task_url']
      if result_url == input_url:
        return True
      elif result_url.split("//")[1] == input_url:
        return True
    return False

def check_if_project_exists(input_url):
    results = task_manager.get_results()
    print("got results")
    if 'http' in input_url:
      short_url = input_url.split("//")[1]
      input_base_url = short_url.split("/")[0]
    else:
      input_base_url = input_url.split("/")[0]

    for r in results:
      result = results[r]
      #print("==")
      result_url = result['task_url'].split("//")[1]
      result_base_url = result_url.split("/")[0]
      if input_base_url == result_base_url:
        return True

    return False

def get_task_completion_time(task_id):
    task = task_manager.get_task(task_id)
    try:
      datetime_string = task['completed_at']
      date_string_formatted = datetime_string.split(".")[0]
      completion_date_object = datetime.strptime(date_string_formatted, '%Y-%m-%d %H:%M:%S')
      completion_time = completion_date_object.strftime("%A %d %B %Y at %H:%M")
      #print(completion_date_object.strftime("%A %d %B %Y %H %M"))
    except Exception as e:
      print(e)
      completion_time = "Not available"
    return completion_time

def create_result_dict(task_results):
    audit_results = {'total_links':0,'broken_links':[],'working_links':[],'link_audit_time':"Not available",'broken_status_codes':[],'total_link_issues':0,'images':[],'right_size_images':[],'broken_images':[],'image_broken_status_codes':[],'total_image_issues':[],'image_count':0,'lighthouse':[]}
    task_ids = []
    for task_result in task_results:
      if task_result['task_type'] == 'link_audit':
        print(f"Link task id {task_result['task_id']}")
        audit_results['total_links'] = task_result['output']['total_links']
        audit_results['broken_links'] = task_result['output']['all_links'][0]
        audit_results['working_links'] = task_result['output']['all_links'][1]
        audit_results['link_audit_time'] = get_task_completion_time(task_result['task_id'])
        task_ids.append(task_result['task_id'])

        try:
          audit_results['broken_status_codes'] = task_result['output']['all_links'][2]
          audit_results['total_link_issues'] = len(audit_results['broken_status_codes']) + len(audit_results['broken_links'])
        except Exception as e:
          print(e)

      elif task_result['task_type'] == 'image_audit':
        print(f"Image task id {task_result['task_id']}")
        audit_results['images'] = task_result['output']['oversize_images']
        audit_results['right_size_images'] = task_result['output']['right_size_images']
        try:
          audit_results['broken_images'] = task_result['output']['broken_images']
          audit_results['image_broken_status_codes'] = task_result['output']['broken_status_codes']
          audit_results['total_image_issues'] = len(audit_results['images']) + len(audit_results['broken_images']) + len(audit_results['image_broken_status_codes'])
        except Exception as e:
          print(e)
        
        audit_results['image_count'] = task_result['output']['image_count']
        #audit_results['image_audit_time'] = get_task_completion_time(task_result['task_id'])
        task_ids.append(task_result['task_id'])
        
      elif task_result['task_type'] == 'lighthouse':
        print(f"Lighthouse task id {task_result['task_id']}")
        try:
          audit_results['lighthouse'] = [{'category': 'Performance', 'score': float(task_result['output']['performance'])*100}, {'category': 'Seo', 'score': float(task_result['output']['seo'])*100}, {'category': 'Accessibility', 'score': float(task_result['output']['accessibility'])*100}, {'category': 'Best-practices', 'score': float(task_result['output']['best-practices'])*100}]
        except Exception as e:
          print(e)
        #print("Lighthouse task id")
        #print(task_result['task_id'])
        task_ids.append(task_result['task_id'])
    try:
      audit_results['task_ids'] = task_ids[0] + "//" + task_ids[1] + "//" + task_ids[2]
    except Exception as e:
      audit_results['task_ids'] = ""
      print(e)
    print(audit_results['task_ids'])
    return audit_results

def get_task_results(url):
    url_task_results = []
    results = task_manager.get_results()
    
    if 'http' in url:
      for r in results:
        result = results[r]
        if result['task_url'] == url:
          url_task_results.append(result)
    else:
      for r in results:
        result = results[r]
        if result['task_url'].split("//")[1] == url:
          url_task_results.append(result)

    return url_task_results

def calculate_project_sums(current_project_count, task_results):
    #print(current_project_count)
    #print(task_results['task_url'])
    #print(task_results['task_id'])
    #print("======")
    if task_results['task_type'] == 'image_audit':
      pages_sum = current_project_count['count'] + 0.5
      images_sum = current_project_count['images'] + task_results['output']['image_count']
      links_sum = current_project_count['links']
      oversize_images_sum = current_project_count['oversize_images'] + len(task_results['output']['oversize_images'])
      broken_links_sum = current_project_count['broken_links']
      worst_performance = current_project_count['worst_performance']
    elif task_results['task_type'] == 'link_audit':
      pages_sum = current_project_count['count'] + 0.5
      images_sum = current_project_count['images']
      links_sum = current_project_count['links'] + task_results['output']['total_links']
      oversize_images_sum = current_project_count['oversize_images']


      all_links_1 = 0
      all_links_2 = 0
      try:
        all_links_1 = len(task_results['output']['all_links'][0])
      except Exception as e:
        print(e)

      try:
        all_links_2 = len(task_results['output']['all_links'][2])
      except Exception as e:
        print(e)

      broken_links_sum = all_links_1 + all_links_2

      #broken_links_sum = current_project_count['broken_links'] + len(task_results['output']['all_links'][0]) + len(task_results['output']['all_links'][2])
      worst_performance = current_project_count['worst_performance']
      
    elif task_results['task_type'] == 'lighthouse':
      pages_sum = current_project_count['count']
      images_sum = current_project_count['images']
      links_sum = current_project_count['links']
      oversize_images_sum = current_project_count['oversize_images']
      broken_links_sum = current_project_count['broken_links']
      # check if performance isn't an empty string or None
      try:
        if float(task_results['output']['performance']) < current_project_count['worst_performance']:
          worst_performance = float(task_results['output']['performance'])*100
        else:
          worst_performance = current_project_count['worst_performance']
      except Exception as e:
        print(e)
        worst_performance = current_project_count['worst_performance']

    new_project_count = {'count': pages_sum,'images':images_sum,'links': links_sum,'oversize_images':oversize_images_sum,'broken_links':broken_links_sum,'worst_performance':worst_performance}

    return new_project_count

def get_projects():
    print("Getting projects")
    print("...")
    results = task_manager.get_results()
    print("got results")
    project_dictionaries = {}
    for r in results:
      #print(f"looping result {r}")
      result = results[r]
      #print("==")
      
      try:
        url_list = result['task_url'].split("//")[1]
      except Exception as e:
        print(e)
        del db['results'][result['task_id']]
        print(f"Deleted problematic result! {r}")
        continue

      doc_site_url = url_list.split("/")[0]
      if doc_site_url not in project_dictionaries:
        if result['task_type'] == 'image_audit':
          project_dictionaries[doc_site_url] = {'count': 0.5, 'images': result['output']['image_count'], 'links': 0, 'oversize_images': len(result['output']['oversize_images']), 'broken_links': 0, 'worst_performance': 101}
        elif result['task_type'] == 'link_audit':
          project_dictionaries[doc_site_url] = {'count': 0.5, 'images': 0, 'links': result['output']['total_links'], 'oversize_images': 0, 'broken_links': len(result['output']['all_links'][0]) + len(result['output']['all_links'][2]), 'worst_performance': 101}
        elif result['task_type'] == 'lighthouse':
          try:
            project_dictionaries[doc_site_url] = {'count': 0, 'images': 0, 'links': 0, 'oversize_images': 0, 'broken_links': 0, 'worst_performance': float(result['output']['performance'])*100}
          except Exception as e:
            print(e) #if result['output']['performance'] cant be converted to a float ie None or empty
            project_dictionaries[doc_site_url] = {'count': 0, 'images': 0, 'links': 0, 'oversize_images': 0, 'broken_links': 0, 'worst_performance': 101}
      else:
        #print("calculating sums")
        new_sums = calculate_project_sums(project_dictionaries[doc_site_url],result)
        project_dictionaries[doc_site_url] = new_sums

    sorted_projects_list = sorted(project_dictionaries.items(), key=lambda x:x[1]["broken_links"], reverse=True)
    sorted_projects_dict = dict(sorted_projects_list)

    return sorted_projects_dict

def calculate_collection_sums(current_project_count, task_results):
    links_sum = current_project_count['total_links']
    broken_links_sum = current_project_count['broken_links']
    images_sum = current_project_count['image_count']
    oversize_images_sum = current_project_count['oversize_images']
    performance = current_project_count['performance']
    if task_results['task_type'] == 'image_audit':
      images_sum = task_results['output']['image_count']
      oversize_images_sum = len(task_results['output']['oversize_images'])+len(task_results['output']['broken_images'])+len(task_results['output']['broken_status_codes'])
    elif task_results['task_type'] == 'link_audit':
      links_sum = task_results['output']['total_links']

      all_links_1 = 0
      all_links_2 = 0
      try:
        all_links_1 = len(task_results['output']['all_links'][0])
      except Exception as e:
        print(e)

      try:
        all_links_2 = len(task_results['output']['all_links'][2])
      except Exception as e:
        print(e)

      broken_links_sum = all_links_1 + all_links_2

      #broken_links_sum = len(task_results['output']['all_links'][0]) + len(task_results['output']['all_links'][2])
    elif task_results['task_type'] == 'lighthouse':
      #print(f"ligh id is {task_results['task_id']}")
      try:
        performance = float(task_results['output']['performance'])*100
      except Exception as e:
        performance = 0
        print(e)
    collection_count = {'total_links': links_sum,'broken_links': broken_links_sum, 'image_count': images_sum, 'oversize_images':oversize_images_sum, 'performance': performance}

    return collection_count

def collection_results(url):
    collection_dictionaries = {}
    results = task_manager.get_results()

    for r in results:
      result = results[r]
      url_list = result['task_url'].split("//")[1]
      doc_site_url = url_list.split("/")[0]
      if doc_site_url == url:
        if url_list not in collection_dictionaries:
          if result['task_type'] == 'image_audit':
            #print(f"image id is {result['task_id']}")
            #print(f"image result is {result}")
            collection_dictionaries[url_list] = {'total_links': 0, 'broken_links': 0, 'image_count': result['output']['image_count'], 'oversize_images': len(result['output']['oversize_images'])+len(result['output']['broken_images'])+len(result['output']['broken_status_codes']), 'performance': 0}
          elif result['task_type'] == 'link_audit':
            #print(f"link id is {result['task_id']}")
            #print(f"link result is {result}")
            collection_dictionaries[url_list] = {'total_links': result['output']['total_links'], 'broken_links': len(result['output']['all_links'][0]) + len(result['output']['all_links'][2]), 'image_count': 0, 'oversize_images': 0, 'performance': 0}
          elif result['task_type'] == 'lighthouse':
            #print(f"lighthouse id is {result['task_id']}")
            #print(f"lighthouse result is {result}")
            try:
              collection_dictionaries[url_list] = {'total_links': 0, 'broken_links': 0, 'image_count': 0, 'oversize_images': 0, 'performance': float(result['output']['performance'])*100}
            except Exception as e:
              print(e)
              collection_dictionaries[url_list] = {'total_links': 0, 'broken_links': 0, 'image_count': 0, 'oversize_images': 0, 'performance': 0}
        else:
          new_sum = calculate_collection_sums(collection_dictionaries[url_list],result)
          collection_dictionaries[url_list] = new_sum
      
    sorted_collections_list = sorted(collection_dictionaries.items(), key=lambda x:x[1]["broken_links"], reverse=True)
    sorted_collection_dict = dict(sorted_collections_list)
    
    return sorted_collection_dict

def collection_sums(collection_dict):
    urls_audited = len(collection_dict)
    image_count = 0
    oversize_images = 0
    broken_links = 0
    total_links = 0
    performance = 101
    for site_result in collection_dict:
      total_links += collection_dict[site_result]['total_links']
      broken_links += collection_dict[site_result]['broken_links']
      image_count += collection_dict[site_result]['image_count']
      oversize_images += collection_dict[site_result]['oversize_images']
      if collection_dict[site_result]['performance'] < performance:
        performance = collection_dict[site_result]['performance']

    project_count = {'count': urls_audited,'images':image_count,'links': total_links,'oversize_images':oversize_images,'broken_links':broken_links,'worst_performance':performance}

    return project_count

def user_id_projects(url_list):
    project_dictionaries = {}
    for base_url in url_list:
      collection_dict = collection_results(base_url)
      project_sums = collection_sums(collection_dict)
      project_dictionaries[base_url] = project_sums
    return project_dictionaries