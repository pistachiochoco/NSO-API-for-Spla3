# Get tokens from Nintendo Switch Online App API to access Spla3 API
Refer to [ZekeSnider/NintendoSwitchRESTAPI](https://github.com/ZekeSnider/NintendoSwitchRESTAPI).

## What is needed
- Nintendo Account

## Environment
- Python 3.8 or above

## Usage
```
$ python3 NSO_API.py
```
If you are the first time run this command, you will see a login url printed in the terminal. After you log into it and
paste the redirected url in the terminal, a config file will be generated automatically. The `session token` and
`web service token` and `bullet token` and `user language` will be saved.<br>
When you run the command again, it will use the `session token` saved before and validate other 2 tokens. If the 2 tokens
is invalid, it will generate new tokens.

## Steps
[Here](https://raw.githubusercontent.com/pistachiochoco/NSOAPIforSpla3/main/NSO_Login_Diagram.svg) is the diagram of login process.
#### 1. Generate a login URL.
When you log in to your Nintendo Account on Nintendo Switch Online App, you will see this page. The url is like:
`https://accounts.nintendo.com/connect/1.0.0/authorize?client_id=71b963c1b7b6d119&interacted=1
&redirect_uri=npf71b963c1b7b6d119://auth&response_type=session_token_code
&scope=openid+user+user.birthday+user.mii+user.screenName&session_token_code_challenge=[session_token_code_challenge]
&session_token_code_challenge_method=S256&state=[state]`.<br>
This link contains many parameters.
- Generated every time:
  - session_token_code_challenge
  - state
- Fixed:
  - client_id: 71b963c1b7b6d119
  - interacted: 1
  - redirect_uri: npf71b963c1b7b6d119://auth
  - response_type: session_token_code
  - scope: openid+user+user.birthday+user.mii+user.screenName
  - session_token_code_challenge_method: S256

The way of generating this url refers to [frozenpandaman/s3s](https://github.com/frozenpandaman/s3s).<br>

#### 2. Get a session token.
If you click the 
"Select this account(この人にする)" button on this url generated in Step1, you will be redirected to a link like
`npf71b963c1b7b6d119://auth#session_state=[session_state]&session_token_code=[session_token_code]&state=[state]`.<br>
Use the `session_token_code` and send a POST request to https://accounts.nintendo.com/connect/1.0.0/api/session_token,
you can get the `session token` in the response.<br>
Once you get a `session token`, you can reuse it which means you have not to log in again when you want to access Spla3 
API.<br>

#### 3. Get access token and id token.
Use `session token` from Step2, send a POST request to https://accounts.nintendo.com/connect/1.0.0/api/token, you can 
get the `access token` and `id token` in the response.<br>

#### 4. Get user's information for authorization.
Use `access token` from Step3, send a GET request to https://api.accounts.nintendo.com/2.0.0/users/me, you can get your 
information including nickname, birthday, country, language and etc.<br>

#### 5. Get a login token. (Log into NSO App)
Use `id token` from Step2 and **user's birthday, country and language** from Step4, send a POST request to 
https://api-lp1.znc.srv.nintendo.net/v3/Account/Login, you can get a token named `accessToken` in 
`webApiServerCredential` in the response. To distinguish different tokens, I named this `accessToken` as 
`login token.`<br>
With this `login token`, we can get the 2 tokens needed for Spla3 API.<br>
When sending the request to [/v3/Account/Login](https://api-lp1.znc.srv.nintendo.net/v3/Account/Login), also parameters 
called `f`, `requestedId` and `timestamp` are needed. I generate these parameters using 
[imink/f-API](https://github.com/imink-app/f-API).

#### 6. Get the game web service list. (not necessary each time because it is fixed)
Use `login token` from Step5, send a POST request to https://api-lp1.znc.srv.nintendo.net/v1/Game/ListWebServices, you 
can get the web service list containing the game id and the API url of Splatoon2, Splatoon3, Super Smash Bros. and
Animal Crossing.<br>
The id and url is also necessary when you want to access the API of each game.<br>
- Splatoon3 web service id: 4834290508791808
- Splatoon3 API URL: https://api.lp1.av5ja.srv.nintendo.net<br>

#### 7. Get a web service token.
Use `login token` from Step5 and response from f API, send a POST request to 
https://api-lp1.znc.srv.nintendo.net/v2/Game/GetWebServiceToken, you can get a token called `accessToken` in the
response. To distinguish different tokens, I named this token as 
`web service token`. This web service token is needed when you send requests to Spla3 API.

#### 8. Get a bullet token.
Use `login token` from Step5, send a POST request to https://api.lp1.av5ja.srv.nintendo.net/api/bullet_tokens, you can 
get the `bullet token`. This bullet token is also needed when you send requests to Spla3 API.

# Access Spla3 API
Spla3 API is a little different from Spla2 API. There are two ways to access it.
One is fetching data through the NSO App, the other is fetching data through the widget (different user-agent).<br>

## What are needed
- `web service token` from Step7
- `bullet token` from Step8

## Methods

#### 1. Access in App
You can get all the data with this type of request. What are needed is `web service token` generated in Step7 and 
`bullet token` from Step8.<br>
Set the `bullet token` as `authorization` and `web service token` as `cookie`, also set a hash code in the json body, 
you can get the corresponding response.<br><br>
For example, hash code `c0429fd738d829445e994d3370999764` is for fetching current fest data (useCurrentFestQuery).

#### 2. Access in Widget
NSO Widget is newly added for Splatoon3. You can get stage schedules (battle and salmon run), recent battle results, 
gear you recently used and photos through the widget.<br>
**Only `bullet token` is needed for sending this type of request**.<br>
Set the `bullet token` as `authorization`, and also a hash code in both request header and json body, you can get the 
corresponding response.<br><br>
For example, you should set `f5131603b235edce2218e71c27ed0d35610cb78c48bb44aa88e98fb37ab08cd0` and `VsSchedules` in 
both header and json body to fetch battle schedules (regular match, anarchy battle open and challenge, X match).

## Maybe helpful
#### Send requests via RapidAPI
You can use [RapidAPI](https://paw.cloud/) open the Spla3_API_test.paw file to see the specific setting of the requests.

#### Send requests in Python
In `NSO_API.py`, the function `is_valid` actually sends the two types of requests using the same setting.<br>
In `Spla3_API_Helper.py`, it will load tokens and send all availale requests to Spla3 API and save the response
locally. You can change the global variable `USER_LANGUAGE` to any language code in `./Data/language_code.json` as you
like.

#### Available Requests
[Here(`./Data/query_id_data.json`)](https://github.com/pistachiochoco/NSOAPIforSpla3/blob/main/Data/query_id_data.json)
I saved all query-id pairs under the current web view version. Note than some queries need specific id inside other
response to fetch data. For example, if you want fetch to the detailed result of one game, you need the id of that game
for fetching the result.