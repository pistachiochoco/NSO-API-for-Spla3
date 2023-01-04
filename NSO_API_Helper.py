import NSO_API
import os, sys, json
import requests
from bs4 import BeautifulSoup

SPLA3_API_URL = NSO_API.SPLA3_API_URL
self_path = os.path.dirname(__file__)
data_path = os.path.dirname(__file__) + '/Data'
try:
    os.mkdir(data_path)
except (FileExistsError):
    pass

config_path = os.path.join(self_path, "config.txt")

try:
    config_file = open(config_path, "r")
    config_data = json.load(config_file)
    config_file.close()
except (IOError, ValueError):
    print("No tokens available. Please generate tokens first.")
    sys.exit(1)

WEB_SERVICE_TOKEN = config_data["web_service_token"]


def get_main_js_file(web_service_token):
    '''
    Uses web service token(gtoken) to fetch main.js file for getting the queries' names and corresponding hashed codes.
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
        print(f"{file_name} file created.")
    return

if __name__ == '__main__':
    get_main_js_file(WEB_SERVICE_TOKEN)
    sys.exit(0)