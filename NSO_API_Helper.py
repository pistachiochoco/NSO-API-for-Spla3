import NSO_API
import os, sys, json, re
import requests
from bs4 import BeautifulSoup

class Query:
    def __init__(self, name, hashid, operation):
        self.name = name
        self.id = hashid
        self.opr = operation

    def __str__(self):
        return f"{self.name}, {self.id}, {self.opr}"

    def __repr__(self):
        return self.__str__()

SPLA3_API_URL = NSO_API.SPLA3_API_URL
self_path = os.path.dirname(__file__)
data_path = os.path.join(self_path + '/Data')
try:
    os.mkdir(data_path)
except(FileExistsError):
    pass

def load_tokens():
    config_path = os.path.join(self_path, "config.txt")
    try:
        print("Loading tokens...")
        config_file = open(config_path, "r")
        config_data = json.load(config_file)
        config_file.close()
    except (IOError, ValueError):
        print("No tokens available. Please generate tokens first.")
        sys.exit(1)

    web_service_token = config_data["web_service_token"]
    return web_service_token


def get_main_js_file(web_service_token):
    '''
    Uses web service token(gtoken) to fetch main.js file for getting the queries' names and corresponding hash ids.
    '''

    cookie = {
        '_dnt': '1',
        '_gtoken': web_service_token
    }

    response = requests.get(SPLA3_API_URL, cookies=cookie)
    if response.status_code != 200:
        print("Token is invalid.")
        sys.exit(1)

    soup = BeautifulSoup(response.text, "html.parser")
    main_js = soup.select_one("script[src*='static']")
    main_js_url = SPLA3_API_URL + main_js.attrs["src"]
    main_js_response = requests.get(main_js_url, cookies=cookie)

    file_name = main_js.attrs["src"][main_js.attrs["src"].find("main"):]
    main_js_path = os.path.join(data_path, file_name)
    try:
        main_js_file = open(main_js_path, "r")
        main_js_file.close()
        print(f"{file_name} file exists.")
    except (IOError, ValueError):
        main_js_file = open(main_js_path, "w")
        main_js_file.seek(0)
        main_js_file.write(main_js_response.text)
        main_js_file.close()
        print(f"{file_name} file is created.")
    return file_name


def get_query_data(file_name):
    '''
    Fetches all query-id pairs and saves them locally for accessing Spla3 API.
    '''

    main_js_file = open(os.path.join(data_path, file_name), "r")
    content = main_js_file.read()
    main_js_file.close()

    pattern = r"\{id:\"(?P<id>[0-9a-z]{32})\",metadata:\{\},name:\"(?P<name>\w+)\",operationKind:\"(?P<operation>\w+)\""
    match = re.findall(pattern, content)
    match.sort(key=lambda m: (m[2], m[1]))

    # query = {m[1]: Query(m[1], m[0], m[2]) for m in match}
    query_name_id = {m[1]: m[0] for m in match}
    # query_name_operation = {m[1]: m[2] for m in match}
    query_data = {m[1]: {"id": m[0], "type": m[2]} for m in match}

    save_data(query_name_id, "query_id_data.json", data_path)
    save_data(query_data, "query_data.json", data_path)

    return

def save_data(data, name, path):
    '''
    A helper function for saving data locally.
    '''

    save_path = os.path.join(path, name)
    try:
        data_file = open(save_path, "r")
        data_file.close()
        print(f"{name} file exists.")
    except (IOError, ValueError):
        data_file = open(save_path, "w")
        data_file.seek(0)
        data_file.write(json.dumps(data, indent=4, separators=(',', ': ')))
        data_file.close()
        print(f"{name} file is created.")
    return



def get_webview_ver(file_name):
    '''
    TODO: Fetches web view version from main.js file.
    '''


if __name__ == '__main__':
    web_service_token = load_tokens()
    file_name = get_main_js_file(web_service_token)
    # file_name = "main.ef47d560.js"
    get_query_data(file_name)
    # get_webview_ver()

    sys.exit(0)