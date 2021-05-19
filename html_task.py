# gets HTML from a URL

import requests

def get_html(url):
    try:
        html = requests.get(url).content
        return html
    except Exception as e:
        raise