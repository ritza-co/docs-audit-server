import task_manager

def separate_urls(form_input):
    urls_list = form_input.split("\r\n")
    return urls_list

def get_task_completion_time(task_id):
    task = task_manager.get_task(task_id)
    completion_time = task['completed_at']
    return completion_time

def create_result_dict(task_results):
    audit_results = {}
    task_ids = []
    for task_result in task_results:
      if task_result['task_type'] == 'link_audit':
        audit_results['total_links'] = task_result['output']['total_links']
        audit_results['broken_links'] = task_result['output']['all_links'][0]
        audit_results['working_links'] = task_result['output']['all_links'][1]
        audit_results['link_audit_time'] = get_task_completion_time(task_result['task_id'])
        task_ids.append(task_result['task_id'])
      elif task_result['task_type'] == 'image_audit':
        audit_results['images'] = task_result['output']['oversize_images']
        try:
          audit_results['right_size_images'] = task_result['output']['right_size_images']
        except Exception as e:
          print(e)
        audit_results['image_count'] = task_result['output']['image_count']
        audit_results['image_audit_time'] = get_task_completion_time(task_result['task_id'])
        task_ids.append(task_result['task_id'])

    audit_results['task_ids'] = task_ids[0] + "//" + task_ids[1]
    print(audit_results['task_ids'])
    return audit_results

def get_result_for_url(url):
    url_task_results = []
    results = task_manager.get_results()
    for r in results:
      result = results[r]
      if result['task_url'].split("//")[1] == url:
        url_task_results.append(result)
    audit_results = create_result_dict(url_task_results)
    return audit_results

def remove_trailing_slash(url):
    if len(url) > 0 and url[-1] == '/':
      clean_url = url[:-1]
    else:
      clean_url = url
    return clean_url

def remove_id_ref_from_url(urls_list):
    urls_list_with_no_ref = []
    for url in urls_list:
      no_ref_url = url.split('#')
      no_slash_url = remove_trailing_slash(no_ref_url[0])
      urls_list_with_no_ref.append(no_slash_url)
    return urls_list_with_no_ref

def remove_id_ref_and_trailing_slash(url):
    no_ref_url = url.split('#')[0]
    clean_url = remove_trailing_slash(no_ref_url)
    return clean_url

def calculate_project_sums(current_project_count, task_results):
    print(current_project_count)
    # print(task_results)
    print("======")
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
      broken_links_sum = current_project_count['broken_links'] + len(task_results['output']['all_links'][0])
      worst_performance = current_project_count['worst_performance']
    elif task_results['task_type'] == 'lighthouse':
      pages_sum = current_project_count['count']
      images_sum = current_project_count['images']
      links_sum = current_project_count['links']
      oversize_images_sum = current_project_count['oversize_images']
      broken_links_sum = current_project_count['broken_links']
      if float(task_results['output']['performance']) < current_project_count['worst_performance']:
        worst_performance = float(task_results['output']['performance'])*100
      else:
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
      print("looping results")
      result = results[r]
      print("==")
      url_list = result['task_url'].split("//")[1]
      doc_site_url = url_list.split("/")[0]
      if doc_site_url not in project_dictionaries:
        if result['task_type'] == 'image_audit':
          project_dictionaries[doc_site_url] = {'count': 0.5, 'images': result['output']['image_count'], 'links': 0, 'oversize_images': len(result['output']['oversize_images']), 'broken_links': 0, 'worst_performance': 101}
        elif result['task_type'] == 'link_audit':
          project_dictionaries[doc_site_url] = {'count': 0.5, 'images': 0, 'links': result['output']['total_links'], 'oversize_images': 0, 'broken_links': len(result['output']['all_links'][0]), 'worst_performance': 101}
        elif result['task_type'] == 'lighthouse':
          project_dictionaries[doc_site_url] = {'count': 0, 'images': 0, 'links': 0, 'oversize_images': 0, 'broken_links': 0, 'worst_performance': float(result['output']['performance'])*100}
      else:
        print("calculating sums")
        new_sums = calculate_project_sums(project_dictionaries[doc_site_url],result)
        project_dictionaries[doc_site_url] = new_sums

    return project_dictionaries

def calculate_collection_sums(current_project_count, task_results):
    links_sum = current_project_count['total_links']
    broken_links_sum = current_project_count['broken_links']
    images_sum = current_project_count['image_count']
    oversize_images_sum = current_project_count['oversize_images']
    performance = current_project_count['performance']
    if task_results['task_type'] == 'image_audit':
      images_sum = task_results['output']['image_count']
      oversize_images_sum = len(task_results['output']['oversize_images'])
    elif task_results['task_type'] == 'link_audit':
      links_sum = task_results['output']['total_links']
      broken_links_sum = len(task_results['output']['all_links'][0])
    elif task_results['task_type'] == 'lighthouse':
      performance = float(task_results['output']['performance'])*100

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
            collection_dictionaries[url_list] = {'total_links': 0, 'broken_links': 0, 'image_count': result['output']['image_count'], 'oversize_images': len(result['output']['oversize_images']), 'performance': 0}
          elif result['task_type'] == 'link_audit':
            collection_dictionaries[url_list] = {'total_links': result['output']['total_links'], 'broken_links': len(result['output']['all_links'][0]), 'image_count': 0, 'oversize_images': 0, 'performance': 0}
          elif result['task_type'] == 'lighthouse':
            collection_dictionaries[url_list] = {'total_links': 0, 'broken_links': 0, 'image_count': 0, 'oversize_images': 0, 'performance': float(result['output']['performance'])*100}
        else:
          new_sum = calculate_collection_sums(collection_dictionaries[url_list],result)
          collection_dictionaries[url_list] = new_sum
      
    return collection_dictionaries
