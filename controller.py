import task_manager

def separate_urls(form_input):
    urls_list = form_input.split("\r\n")
    return urls_list

def create_result_dict(task_results):
    audit_results = {}
    for task_result in task_results:
      if task_result['task_type'] == 'link_audit':
        audit_results['total_links'] = task_result['output']['total_links']
        audit_results['broken_links'] = task_result['output']['all_links'][0]
        audit_results['working_links'] = task_result['output']['all_links'][1]
      elif task_result['task_type'] == 'image_audit':
        audit_results['images'] = task_result['output']['oversize_images']
        audit_results['image_count'] = task_result['output']['image_count']
    return audit_results

def get_result_for_url(url):
    url_task_results = []
    results = task_manager.get_results()
    for result in results:
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
    if task_results['task_type'] == 'image_audit':
      pages_sum = current_project_count['count'] + 0.5
      images_sum = current_project_count['images'] + task_results['output']['image_count']
      links_sum = current_project_count['links']
      oversize_images_sum = current_project_count['oversize_images'] + len(task_results['output']['oversize_images'])
      broken_links_sum = current_project_count['broken_links']
    elif task_results['task_type'] == 'link_audit':
      pages_sum = current_project_count['count'] + 0.5
      images_sum = current_project_count['images']
      links_sum = current_project_count['links'] + task_results['output']['total_links']
      oversize_images_sum = current_project_count['oversize_images']
      broken_links_sum = current_project_count['broken_links'] + len(task_results['output']['all_links'][0])

    new_project_count = {'count': pages_sum,'images':images_sum,'links': links_sum,'oversize_images':oversize_images_sum,'broken_links':broken_links_sum}

    return new_project_count

def get_projects():
    results = task_manager.get_results()
    project_dictionaries = {}
    for result in results:
      url_list = result['task_url'].split("//")[1]
      doc_site_url = url_list.split("/")[0]
      if doc_site_url not in project_dictionaries:
        if result['task_type'] == 'image_audit':
          project_dictionaries[doc_site_url] = {'count': 0.5, 'images': result['output']['image_count'], 'links': 0, 'oversize_images': len(result['output']['oversize_images']), 'broken_links': 0}
        elif result['task_type'] == 'link_audit':
          project_dictionaries[doc_site_url] = {'count': 0.5, 'images': 0, 'links': result['output']['total_links'], 'oversize_images': 0, 'broken_links': len(result['output']['all_links'][0])}
      else:
        new_sums = calculate_project_sums(project_dictionaries[doc_site_url],result)
        project_dictionaries[doc_site_url] = new_sums

    return project_dictionaries

def calculate_collection_sums(current_project_count, task_results):
    if task_results['task_type'] == 'image_audit':
      images_sum = task_results['output']['image_count']
      links_sum = current_project_count['total_links']
      oversize_images_sum = len(task_results['output']['oversize_images'])
      broken_links_sum = current_project_count['broken_links']
    elif task_results['task_type'] == 'link_audit':
      images_sum = current_project_count['image_count']
      links_sum = task_results['output']['total_links']
      oversize_images_sum = current_project_count['oversize_images']
      broken_links_sum = len(task_results['output']['all_links'][0])

    collection_count = {'total_links': links_sum,'broken_links': broken_links_sum, 'image_count': images_sum, 'oversize_images':oversize_images_sum}

    return collection_count

def collection_results(url):
    collection_dictionaries = {}
    results = task_manager.get_results()

    for result in results:
      url_list = result['task_url'].split("//")[1]
      doc_site_url = url_list.split("/")[0]
      if doc_site_url == url:
        if url_list not in collection_dictionaries:
          if result['task_type'] == 'image_audit':
            collection_dictionaries[url_list] = {'total_links': 0, 'broken_links': 0, 'image_count': result['output']['image_count'], 'oversize_images': len(result['output']['oversize_images'])}
          elif result['task_type'] == 'link_audit':
            collection_dictionaries[url_list] = {'total_links': result['output']['total_links'], 'broken_links': len(result['output']['all_links'][0]), 'image_count': 0, 'oversize_images': 0}
        else:
          new_sum = calculate_collection_sums(collection_dictionaries[url_list],result)
          collection_dictionaries[url_list] = new_sum
      
    return collection_dictionaries
