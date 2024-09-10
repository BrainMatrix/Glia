from duckduckgo_search import DDGS

import requests
import html2text
import json

import logging

def webpage_post_process(text):
    lines = text.split("\n")
    lines = [line for line in lines if not line.startswith("![]") and len(line) > 10]
    return "\n".join(lines)

def get_web_contents(topic:str, num:int=5, max_try_count:int=None):
    """
    Get {num} best records from Internet Search Engine with the {topic} you specified.
    Will grab {max_try_count} records from duck duck go, and try to fetch their contents.
    If this function cannot fetch contents from a record, this record will be ignored. 
    So you might get less than {num} records.
    """
    
    if max_try_count is None:
        max_try_count = num * 4
    
    with DDGS() as search:
        result = list(search.text(topic, max_results=max_try_count))
        logging.debug(f"SE result for topic = {topic}: {result}")
        
    doc_to_add = []
    for res in result:
        if len(doc_to_add) >= num:
            break
        
        #print(res)
        url = res["href"]
        
        resp = requests.get(url)
        text = html2text.html2text(resp.content.decode(), bodywidth=5000)
        text = webpage_post_process(text)
        
        logging.debug(f"Document found for topic = {topic}: {text}")
        
        if len(text) > 10:
            res["full_text"] = text
            doc_to_add.append(res)
            
    return doc_to_add


def get_web_contents_proxy(topic:str, num:int=5, max_try_count:int=None):
    """
    Get {num} best records from Internet Search Engine with the {topic} you specified.
    Will grab {max_try_count} records from duck duck go, and try to fetch their contents.
    If this function cannot fetch contents from a record, this record will be ignored. 
    So you might get less than {num} records.
    """
    
    url = 'http://103.149.200.4:3535/get_web_contents'
    data = {
        "text": topic
    }
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        result = response.json()
    else:
        result = {}
        result['duckduckgo_return'] = 'error'
            
    return result['duckduckgo_return']