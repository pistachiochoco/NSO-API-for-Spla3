import os, sys, json
import urllib.parse, hashlib, base64
import requests
from bs4 import BeautifulSoup


self_path = os.path.dirname(__file__)
config_path = os.path.join(self_path, "config.txt")

try:
    config_file = open(config_path, "r")
    config_data = json.load(config_file)
    config_file.close()
except (IOError, ValueError):
    print("Generating new config file...")
    config_data = {
        "session_token": "",
        "web_service_token": "",
        "bullet_token": "",
        "user_language": ""
    }
    config_file = open(config_path, "w")
    config_file.seek(0)
    config_file.write(json.dumps(config_data, indent=4, separators=(',', ': ')))
    config_file.close()

SESSION_TOKEN = config_data["session_token"]
WEB_SERVICE_TOKEN = config_data["web_service_token"]
BULLET_TOKEN = config_data["bullet_token"]
USER_LANGUAGE = config_data["user_language"]

NSO_APP_VERSION = "2.5.0"
WEB_VIEW_VERSION = "2.0.0-bd36a652"
SPLA3_WEB_SERVICE_ID = "4834290508791808"
SPLA3_API_URL = "https://api.lp1.av5ja.srv.nintendo.net"
CLIENT_ID = '71b963c1b7b6d119'

USER_COUNTRY = ""


session = requests.Session()

def get_nsoapp_version():
    '''
    Fetches the Nintendo Switch Online App Version from Apple App Store and set it globally.
    '''

    global NSO_APP_VERSION

    try:
        page = requests.get("https://apps.apple.com/jp/app/nintendo-switch-online/id1234806557")
        soup = BeautifulSoup(page.text, 'html.parser')
        content = soup.find(name='p', attrs={"class": "whats-new__latest__version"})
        version = content.get_text().replace("バージョン  ", "").strip()
        NSO_APP_VERSION = version
        return version
    except: # if web request gets error
        return NSO_APP_VERSION

def get_web_view_ver(gtoken=""):
    '''
    TODO
    Fetches the web view version and sets it globally.
    '''
    return "2.0.0-bd36a652"


def f_api(id_token, hash_method):
    '''
    Fetches f and requestId from https://api.imink.app/f.
    Reference: https://github.com/imink-app/f-API
    '''

    url = 'https://api.imink.app/f'
    header = {
        'User-Agent': f'Coral/{NSO_APP_VERSION}',
        'Content-Type': 'application/json; charset=utf-8'
    }
    body = {
        'token': id_token,
        'hash_method': hash_method
    }

    response = requests.post(url, headers=header, json=body)
    content = json.loads(response.text)

    f = content["f"]
    request_id = content["request_id"]
    timestamp = content["timestamp"]

    return f, request_id, timestamp


def get_web_service_id(login_token):
    '''Fetches Splatoon3 web service id and Spla3 API URL and set them globally.'''

    global SPLA3_WEB_SERVICE_ID
    global SPLA3_API_URL

    url = 'https://api-lp1.znc.srv.nintendo.net/v1/Game/ListWebServices'
    header = {
        'User-Agent': f'Coral/{NSO_APP_VERSION} (com.nintendo.znca; iOS 15.6.0)',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ja-JP;q=1.0, en-JP;q=0.9, zh-Hans-JP;q=0.8, ko-JP;q=0.7',
        'Content-Type': 'application/json',
        'X-ProductVersion': NSO_APP_VERSION,
        'X-Platform': 'iOS',
        'Authorization': f'Bearer {login_token}'
    }

    f, request_id, timestamp = f_api(login_token, 2)
    body = {
        'parameter': {},
        'requestId': request_id
    }

    try:
        response = requests.post(url, headers=header, json=body)
        content = json.loads(response.text)

        for result in content["result"]:
            if result["name"] == "スプラトゥーン3":
                web_service_id_spla3 = result["id"]
                web_service_uri_spla3 = result["uri"]
                global SPLA3_WEB_SERVICE_ID, SPLA3_API_URL
                SPLA3_WEB_SERVICE_ID = web_service_id_spla3
                SPLA3_API_URL = web_service_uri_spla3
            # elif result["name"] == "あつまれ どうぶつの森":
            # 	web_service_id_ac = result["id"]
            # 	web_service_uri_ac = result["uri"]
            # elif result["name"] == "大乱闘スマッシュブラザーズ SPECIAL":
            # 	web_service_id_smbr = result["id"]
            # 	web_service_uri_smbr = result["uri"]
            # elif result["name"] == "スプラトゥーン2":
            # 	web_service_id_spla2 = result["id"]
            # 	web_service_uri_spla2 = result["uri"]

            return SPLA3_WEB_SERVICE_ID, SPLA3_API_URL
    except:
        return SPLA3_WEB_SERVICE_ID, SPLA3_API_URL


def get_session_token():
    '''
    Fetches session_token from login url and sets it globally.
    '''

    '''
    Step1: Generate login url.
    Generates login url is like:
    'https://accounts.nintendo.com/connect/1.0.0/authorize
    ?client_id=71b963c1b7b6d119
    &interacted=1
    &redirect_uri=npf71b963c1b7b6d119%3A%2F%2Fauth
    &response_type=session_token_code
    &scope=openid+user+user.birthday+user.mii+user.screenName
    &session_token_code_challenge=[session_token_code_challenge]
    &session_token_code_challenge_method=S256
    &state=[state]'
    and returns session token code verifier.
    '''

    REDIRECT_URI = 'npf' + CLIENT_ID + '://auth'

    state = base64.urlsafe_b64encode(os.urandom(36))
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).replace(b"=", b"")
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier).digest()).replace(b"=", b"")

    body = {
        'client_id': CLIENT_ID,
        'interacted': '1',
        'redirect_uri': REDIRECT_URI,
        'response_type': 'session_token_code',
        'scope': 'openid user user.birthday user.mii user.screenName',
        'session_token_code_challenge': code_challenge,
        'session_token_code_challenge_method': 'S256',
        'state': state
    }

    authorize_url = f'https://accounts.nintendo.com/connect/1.0.0/authorize?{urllib.parse.urlencode(body)}'
    print(f'Login URL: {authorize_url}')
    print("Please open the url above and right click the \"この人にする\" button, copy the link and paste it here:")

    '''
    Step2: Fetches session_token with session_token_code in the pasted url.
    pasted_url is like:
    npf71b963c1b7b6d119://auth
    #session_state=[session_state]
    &session_token_code=[session_token_code]
    &state=[state]
    '''
    pasted_url = input()
    session_token_code = pasted_url[pasted_url.find('&session_token_code') + len("session_token_code=") + 1: pasted_url.find('&state')]

    url = 'https://accounts.nintendo.com/connect/1.0.0/api/session_token'
    header = {
        'User-Agent': f'Coral/{NSO_APP_VERSION} (com.nintendo.znca; build:3062; iOS 15.6.0) NASDK/{NSO_APP_VERSION}',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ja-JP;q=1.0, en-JP;q=0.9, zh-Hans-JP;q=0.8, ko-JP;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'accounts.nintendo.com'
    }
    body = {
        'client_id': CLIENT_ID,
        'session_token_code': session_token_code,
        'session_token_code_verifier': code_verifier
    }

    response = session.post(url, headers=header, data=body)

    global SESSION_TOKEN
    session_token = json.loads(response.text)["session_token"]
    SESSION_TOKEN = session_token
    config_data["session_token"] = session_token
    return session_token


def get_login_token():
    '''
    Logs into Nintendo Switch Online App and fetches login_token(accessToken) using session_token.
    '''

    # Step1: Fetches access_token and id_token from /connect/1.0.0/api/token.
    url = 'https://accounts.nintendo.com/connect/1.0.0/api/token'
    header = {
        'User-Agent': f'Coral/{NSO_APP_VERSION} (com.nintendo.znca; build:3062; iOS 15.6.0) NASDK/{NSO_APP_VERSION}',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ja-JP',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Host': 'accounts.nintendo.com'
    }
    body = {
        'client_id': CLIENT_ID,
        'grant_type': "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token",
        'session_token': SESSION_TOKEN
    }

    response = session.post(url, headers=header, json=body)
    access_token = json.loads(response.text)["access_token"]  # expires_in: "900"
    id_token = json.loads(response.text)["id_token"]


    # Step2: Fetches user's information using access_token.
    url = 'https://api.accounts.nintendo.com/2.0.0/users/me'
    header = {
        'User-Agent': f'Coral/{NSO_APP_VERSION} (com.nintendo.znca; build:3062; iOS 15.6.0) NASDK/{NSO_APP_VERSION}',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ja-JP',
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=header)
    user_info = json.loads(response.text)

    user_country = user_info["country"]
    user_language = user_info["language"]
    user_birthday = user_info["birthday"]
    # user_nickname = user_info["nickname"]
    # print(f"Welcome, {user_nickname}!")

    global USER_LANGUAGE, USER_COUNTRY
    USER_LANGUAGE = user_language
    config_data["user_language"] = user_language
    USER_COUNTRY = user_country


    # Step3: Log into Nintendo Switch Online App and gets accessToken(gToken)
    url = 'https://api-lp1.znc.srv.nintendo.net/v3/Account/Login'
    header = {
        'User-Agent': f'Coral/{NSO_APP_VERSION} (com.nintendo.znca; iOS 15.6.0)',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ja-JP;q=1.0, en-JP;q=0.9, zh-Hans-JP;q=0.8, ko-JP;q=0.7',
        'Content-Type': 'application/json',
        'X-Platform': 'iOS',
        'X-ProductVersion': NSO_APP_VERSION
    }

    f, request_id, timestamp = f_api(id_token, 1)

    parameter = {
        'f': f,
        'language': user_language,
        'naBirthday': user_birthday,
        'naCountry': user_country,
        'naIdToken': id_token,
        'requestId': request_id,
        'timestamp': timestamp
    }
    body = {
        'parameter': parameter
    }

    response = requests.post(url, headers=header, json=body)
    content = json.loads(response.text)

    # user_name = content["result"]["user"]["name"]
    login_token = content["result"]["webApiServerCredential"]["accessToken"]  # expires in 7200

    # print(f"Welcome, {user_name}!")
    return login_token


def get_web_service_token(login_token):
    '''
    Fetches web_service_token (gtoken) (when open Splatoon3).
    '''

    url = 'https://api-lp1.znc.srv.nintendo.net/v2/Game/GetWebServiceToken'
    header = {
        'User-Agent': f'Coral/{NSO_APP_VERSION} (com.nintendo.znca; iOS 15.6.0)',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ja-JP;q=1.0, en-JP;q=0.9, zh-Hans-JP;q=0.8, ko-JP;q=0.7',
        'Content-Type': 'application/json',
        'X-Platform': 'iOS',
        'X-ProductVersion': NSO_APP_VERSION,
        'Authorization': f'Bearer {login_token}'
    }

    f, request_id, timestamp = f_api(login_token, 2)

    parameter = {
        'f': f,
        'id': SPLA3_WEB_SERVICE_ID,
        'registrationToken': login_token,
        'requestId': request_id,
        'timestamp': timestamp
    }
    body = {
        'parameter': parameter
    }

    response = requests.post(url, headers=header, json=body)
    content = json.loads(response.text)
    web_service_token = content["result"]["accessToken"]  # expires in 23400

    global WEB_SERVICE_TOKEN
    WEB_SERVICE_TOKEN = web_service_token
    config_data["web_service_token"] = web_service_token
    return web_service_token


def get_bullet_token():
    '''
    Fetch bullet tokens for Spla3 API.
    '''

    url = 'https://api.lp1.av5ja.srv.nintendo.net/api/bullet_tokens'
    header = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': USER_LANGUAGE,
        'Content-Type': 'application/json',
        'Origin': 'https://api.lp1.av5ja.srv.nintendo.net',
        'X-NACOUNTRY': USER_COUNTRY,
        'X-Web-View-Ver': WEB_VIEW_VERSION
    }
    cookie = {
        '_dnt': "0",
        '_gtoken': WEB_SERVICE_TOKEN
    }

    response = requests.post(url, headers=header, cookies=cookie)
    content = json.loads(response.text)
    bullet_token = content["bulletToken"]

    global BULLET_TOKEN
    BULLET_TOKEN = bullet_token
    config_data["bullet_token"] = bullet_token
    return bullet_token


def is_valid(web_service_token="", bullet_token=""):
    '''
    Validates tokens for spla3 API.
    '''

    url = f"{SPLA3_API_URL}/api/graphql"

    if web_service_token and bullet_token:  # validate both 2 tokens
        # send a request through App
        user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        header = {
            'User-Agent': user_agent,
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': USER_LANGUAGE,
            'Content-Type': 'application/json',
            'Origin': SPLA3_API_URL,
            'X-Web-View-Ver': WEB_VIEW_VERSION,
            'Authorization': f'Bearer {bullet_token}'
        }
        cookie = {
            '_dnt': "0",
            '_gtoken': web_service_token
        }
        body = {
            'extensions': {
                'persistedQuery': {
                    'sha256Hash': 'dba47124d5ec3090c97ba17db5d2f4b3',
                    'version': '1'
                }
            },
            'variables': {}
        }
        response = requests.post(url, headers=header, cookies=cookie, json=body)
        return response.status_code == 200

    elif bullet_token:
        # send a request through widget
        user_agent = 'GameWidgetsExtension/3062 CFNetwork/1335.0.3 Darwin/21.6.0'
        operation_id = 'f2924b9d93f7ff68670b6b0a91ab49370b7e23cf3d6a4e51a6dcc2940e86b023'
        operation_type ='CoopSchedules'
        header = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': USER_LANGUAGE,
            'Apollographql-Client-Version': f'{NSO_APP_VERSION}-3062',
            'Apollographql-Client-Name': 'com.nintendo.znca.widget-apollo-ios',
            'Content-Type': 'application/json',
            'User-Agent': user_agent,
            'X-App-Ver': NSO_APP_VERSION,
            'X-Apollo-Operation-Id': operation_id,
            'X-Apollo-Operation-Name': operation_type,
            'X-Apollo-Operation-Type': 'query',
            'Authorization': f'Bearer {bullet_token}'
        }
        body = {
            "extensions": {
                "persistedQuery": {
                    "sha256Hash": operation_id,
                    "version": 1
                }
            },
            "id": operation_id,
            "operationName": operation_type,
            "variables": {
                "first": 6
            }
        }
        response = requests.post(url, headers=header, json=body)
        return response.status_code == 200


def write_config():
    config_file = open(config_path, "w")
    config_file.seek(0)
    config_file.write(json.dumps(config_data, indent=4, separators=(',', ': ')))
    config_file.close()


if __name__ == '__main__':

    # NSO_APP_VERSION = get_nsoapp_version()

    if WEB_SERVICE_TOKEN and BULLET_TOKEN:
        if not is_valid(WEB_SERVICE_TOKEN, BULLET_TOKEN):
            print("Tokens expired. Generate new tokens...")
        else:
            print("Tokens are still valid.")
            print(f"Web service token(gtoken): {WEB_SERVICE_TOKEN}")
            print(f"Bullet token: {BULLET_TOKEN}")
            sys.exit(0)

    if SESSION_TOKEN == "":
        get_session_token()
        write_config()

    login_token = get_login_token()
    write_config()

    # get_web_service_id(login_token)
    get_web_service_token(login_token)
    get_bullet_token()
    write_config()

    print("New tokens are generated.")
    print(f"Web service token(gtoken): {WEB_SERVICE_TOKEN}")
    print(f"Bullet token: {BULLET_TOKEN}")
    sys.exit(0)