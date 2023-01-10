import NSO_API, NSO_API_Helper
import os, sys, json, re
import requests
from bs4 import BeautifulSoup

SPLA3_API_URL = NSO_API.SPLA3_API_URL
self_path = os.path.dirname(__file__)
data_path = os.path.join(self_path + '/SampleData')
try:
    os.mkdir(data_path)
except(FileExistsError):
    pass

WEB_SERVICE_TOKEN = ""
BULLET_TOKEN = ""
USER_LANGUAGE = 'ja-JP'  # For fetching sample data I use Japanese for convenience.
WEB_VIEW_VERSION = "2.0.0-bd36a652"  # Can be loaded from ./Data/web_view_ver.json.

QUERY_ID = {}

def load_tokens():
    '''
    Loads web service token and bullet token and save them globally.
    '''

    config_path = os.path.join(self_path, "config.txt")
    try:
        print("Loading tokens...")
        config_file = open(config_path, "r")
        config_data = json.load(config_file)
        config_file.close()
    except (IOError, ValueError):
        print("No tokens available. Please run NSO_API.py to generate tokens first.")
        sys.exit(1)

    web_service_token = config_data["web_service_token"]
    bullet_token = config_data["bullet_token"]

    if not NSO_API.is_valid(web_service_token, bullet_token):
        print("Tokens expired. Please run NSO_API.py to generate new tokens.")
        sys.exit(1)

    global WEB_SERVICE_TOKEN, BULLET_TOKEN
    WEB_SERVICE_TOKEN = web_service_token
    BULLET_TOKEN = bullet_token
    return


def load_query_ids():
    '''
    Loads query-id pairs from json file generated by NSO_API_Helper.py.
    '''

    try:
        query_file = open("./Data/query_id_data.json", "r")
        query_data = query_file.read()
        query_file.close()
    except (IOError, ValueError):
        print("query_id_data.json file doesn't exist. Please run NSO_API_Helper.py to generate it.")
        sys.exit(1)

    global QUERY_ID
    QUERY_ID = json.loads(query_data)
    return

def get_sample_data():
    '''
    Fetches Spla3 API responses with all available requests and save them locally.
    TODO: Queries whose query name with "Detailed" need specific ids for fetching data.
    '''

    url = f"{SPLA3_API_URL}/api/graphql"
    user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    header = {
        'User-Agent': user_agent,
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': USER_LANGUAGE,
        'Content-Type': 'application/json',
        'Origin': SPLA3_API_URL,
        'X-Web-View-Ver': WEB_VIEW_VERSION,
        'Authorization': f'Bearer {BULLET_TOKEN}'
    }
    cookie = {
        '_dnt': "0",
        '_gtoken': WEB_SERVICE_TOKEN
    }
    body = {
        'extensions': {
            'persistedQuery': {
                'sha256Hash': '',
                'version': '1'
            }
        },
        'variables': {}
    }

    for query_name, query_id in QUERY_ID.items():
        if "Refetch" in query_name:
            continue
        body["extensions"]["persistedQuery"]["sha256Hash"] = query_id
        response = requests.post(url, headers=header, cookies=cookie, json=body)
        if response.status_code != 200:
            print("Request failed.")
            sys.exit(1)
        text = json.loads(response.text)
        NSO_API_Helper.save_data(text, f"{query_name}.json", data_path)
    return


if __name__ == '__main__':
    load_tokens()
    load_query_ids()
    get_sample_data()
    sys.exit(0)
