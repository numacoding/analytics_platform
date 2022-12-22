import requests
import json

def run_query(uri, query, status_code):
    request = requests.post(uri, json={'query': query})
    if request.status_code == status_code:
        return request.json()
    else:
        raise Exception(f"Unexpected status code returned: {request.status_code}")

zeitgeist_uri = 'https://processor.rpc-0.zeitgeist.pm/graphql'
status_code = 200
