import NSO_API, NSO_API_Helper
import os, sys, json, re
import requests
from bs4 import BeautifulSoup

SPLA3_API_URL = NSO_API.SPLA3_API_URL
self_path = os.path.dirname(__file__)
root_path = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
data_path = os.path.join(self_path + '/SampleData')
try:
    os.mkdir(data_path)
except(FileExistsError):
    pass

WEB_SERVICE_TOKEN = ""
BULLET_TOKEN = ""
USER_LANGUAGE = 'ja-JP'  # For fetching sample data I use Japanese for convenience.
WEB_VIEW_VERSION = "2.0.0-bd36a652"  # Can be loaded from ./Data/web_view_ver.json.

QUERY_ID = {
    # "CheckinWithQRCodeMutation": "8d54e1c6bdcc65181f65adc582914ad8",
    # "CreateMyOutfitMutation": "31ff008ea218ffbe11d958a52c6f959f",
    # "ReplayModalReserveReplayDownloadMutation": "87bff2b854168b496c2da8c0e7f3e5bc",
    # "SaleGearDetailOrderGesotownGearMutation": "b79b7a101a243912754f72437e2ad7e5",
    # "SupportButton_SupportChallengeMutation": "30aa261475d43bd765b4200fc67003c8",
    # "UpdateMyOutfitMutation": "bb809066282e7d659d3b9e9d4e46b43b",
    # "VotesUpdateFestVoteMutation": "a2c742c840718f37488e0394cd6e1e08",
    # "BankaraBattleHistoriesQuery": "0438ea6978ae8bd77c5d1250f4f84803",
    # "BankaraBattleHistoriesRefetchQuery": "92b56403c0d9b1e63566ec98fef52eb3",
    # "BattleHistoryCurrentPlayerQuery": "49dd00428fb8e9b4dde62f585c8de1e0",
    # "CatalogQuery": "52504060c81ff2f2d618c4e5377e6e7c",
    # "CatalogRefetchQuery": "4423dfd630867301fcdd834cd52922f4",
    # "ChallengeQuery": "8a079214500148bf88a8fce1d7209b90",
    # "ChallengeRefetchQuery": "34aedc79f96b8613501bba465295f779",
    # "CheckinQuery": "5d0d1b45ebf4e324d0dae017d9df06d2",
    # "ConfigureAnalyticsQuery": "f8ae00773cc412a50dd41a6d9a159ddd",
    # "CoopHistoryDetailQuery": "9ade2aa3656324870ccec023636aed32",
    # "CoopHistoryDetailRefetchQuery": "d3188df2fd4436870936b109675e2849",
    # "CoopHistoryQuery": "2fd21f270d381ecf894eb975c5f6a716",
    # "CoopPagerLatestCoopQuery": "a2704e18852efce9cdbc61e205e1ed4e",
    "DetailFestRecordDetailQuery": "96c3a7fd484b8d3be08e0a3c99eb2a3d",
    "DetailFestRefethQuery": "18c7c465b18de5829347b7a7f1e571a1",
    # "DetailFestVotingStatusRefethQuery": "92f51ed1ab462bbf1ab64cad49d36f79",
    "DetailRankingQuery": "4869de13d0d209032b203608cb598aef",
    "DetailTabViewWeaponTopsArRefetchQuery": "a6782a0c692e8076656f9b4ab613fd82",
    # "DetailTabViewWeaponTopsClRefetchQuery": "8d3c5bb2e82d6eb32a37eefb0e1f8f69",
    # "DetailTabViewWeaponTopsGlRefetchQuery": "b23468857c049c2f0684797e45fabac1",
    # "DetailTabViewWeaponTopsLfRefetchQuery": "d46f88c2ea5c4daeb5fe9d5813d07a99",
    "DetailTabViewXRankingArRefetchQuery": "eb69df6f2a2f13ab207eedc568f0f8b6",
    # "DetailTabViewXRankingClRefetchQuery": "68f99b7b02537bcb881db07e4e67f8dd",
    # "DetailTabViewXRankingGlRefetchQuery": "5f8f333770ed3c43e21b0121f3a86716",
    # "DetailTabViewXRankingLfRefetchQuery": "4e8b381ae6f9620443627f4eac3a2210",
    "DetailVotingStatusQuery": "53ee6b6e2acc3859bf42454266d671fc",
    # "DownloadSearchReplayQuery": "43a5f23eec238d7ee827cc87f47f050c",
    # "FestRecordQuery": "44c76790b68ca0f3da87f2a3452de986",
    # "FestRecordRefetchQuery": "73b9837d0e4dd29bfa2f1a7d7ee0814a",
    # "FriendListQuery": "f0a8ebc384cf5fbac01e8085fbd7c898",
    # "FriendListRefetchQuery": "aa2c979ad21a1100170ddf6afea3e2db",
    # "GesotownQuery": "a43dd44899a09013bcfd29b4b13314ff",
    # "GesotownRefetchQuery": "951cab295eafdbeccfc2e718d7a98646",
    # "HeroHistoryQuery": "fbee1a882371d4e3becec345636d7d1c",
    # "HeroHistoryRefetchQuery": "4f9ae2b8f1d209a5f20302111b28f975",
    # "HistoryRecordQuery": "32b6771f94083d8f04848109b7300af5",
    # "HistoryRecordRefetchQuery": "57b1ccae6949c407e2df9bcad2a8e573",
    # "HomeQuery": "dba47124d5ec3090c97ba17db5d2f4b3",
    "JourneyChallengeDetailQuery": "38e58b84376a2ad49ddbe4061b948455",
    # "JourneyChallengeDetailRefetchQuery": "8dc246933b1f4e26a6dfd251878cf786",
    "JourneyQuery": "bc71fc0264f3f72256724b069f7a4097",
    # "JourneyRefetchQuery": "09eee118fa16415d6bc3846bc6e5d8e5",
    # "LatestBattleHistoriesQuery": "0176a47218d830ee447e10af4a287b3f",
    # "LatestBattleHistoriesRefetchQuery": "7161210aad0793e58e76f20e0443855e",
    # "MyOutfitDetailQuery": "d935d9e9ba7a5b6b5d6ece7f253304fc",
    # "MyOutfitsQuery": "81d9a6849467d2aa6b1603ebcedbddbe",
    # "MyOutfitsRefetchQuery": "10db4e349f3123c56df14e3adec2ee6f",
    # "PagerLatestVsDetailQuery": "0329c535a32f914fd44251be1f489e24",
    "PagerUpdateBattleHistoriesByVsModeQuery": "094a9b44ff21e8c409d6046fc1af9dfe",
    # "PhotoAlbumQuery": "7e950e4f69a5f50013bba8a8fb6a3807",
    # "PhotoAlbumRefetchQuery": "53fb0ad32c13dd9a6e617b1158cc2d41",
    # "PrivateBattleHistoriesQuery": "8e5ae78b194264a6c230e262d069bd28",
    # "PrivateBattleHistoriesRefetchQuery": "89bc61012dcf170d9253f406ebebee67",
    "RankingHoldersFestTeamRankingHoldersPaginationQuery": "be2eb9e9b8dd680519eb59cc46c1a32b",
    # "RegularBattleHistoriesQuery": "3baef04b095ad8975ea679d722bc17de",
    # "RegularBattleHistoriesRefetchQuery": "4c95233c8d55e7c8cc23aae06109a2e8",
    # "ReplayQuery": "7ec830425971a0e0ff5b2a378455e38e",
    # "ReplayUploadedReplayListRefetchQuery": "1d1048e2af114e263a3c3d3ddd34bcb4",
    # "SaleGearDetailQuery": "6eb1b255b2cf04c08041567148c883ad",
    # "SettingQuery": "61228d553e7463c203e05e7810dd79a7",
    # "StageRecordQuery": "f08a932d533845dde86e674e03bbb7d3",
    # "StageRecordsRefetchQuery": "2fb1b3fa2d40c9b5953ea1ae263e54c1",
    # "StageScheduleQuery": "730cd98e84f1030d3e9ac86b6f1aae13",
    # "VsHistoryDetailPagerRefetchQuery": "994cf141e55213e6923426caf37a1934",
    # "VsHistoryDetailQuery": "291295ad311b99a6288fc95a5c4cb2d2",
    # "WeaponRecordQuery": "5f279779e7081f2d14ae1ddca0db2b6e",
    # "WeaponRecordsRefetchQuery": "6961f618fcef440c81509b205465eeec",
    # "XBattleHistoriesQuery": "6796e3cd5dc3ebd51864dc709d899fc5",
    # "XBattleHistoriesRefetchQuery": "94711fc9f95dd78fc640909f02d09215",
    # "XRankingDetailQuery": "ec7174376203f9901713e116075c5ecd",
    # "XRankingDetailRefetchQuery": "2aac81b2ec56fb2d15ce3d6a2b625772",
    # "XRankingQuery": "d771444f2584d938db8d10055599011d",
    # "XRankingRefetchQuery": "5149402597bd2531b4eea04692d8bfd5",
    # "myOutfitCommonDataEquipmentsQuery": "d29cd0c2b5e6bac90dd5b817914832f8",
    # "myOutfitCommonDataFilteringConditionQuery": "d02ab22c9dccc440076055c8baa0fa7a",
    # "refetchableCoopHistory_coopResultQuery": "2a7f4335bcf586d904db85e75ba868c0",
    # "useCurrentFestQuery": "c0429fd738d829445e994d3370999764"
}

def load_tokens():
    '''
    Loads web service token and bullet token and save them globally.
    '''

    config_path = os.path.join(root_path, "config.txt")
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
        query_data_path = os.path.join(root_path, '/Data')
        query_file = open(os.path.join(query_data_path, "query_id_data.json"), "r")
        query_data = query_file.read()
        query_file.close()
    except (IOError, ValueError):
        print("query_id_data.json file doesn't exist. Please run NSO_API_Helper.py to generate it.")
        sys.exit(1)

    global QUERY_ID
    QUERY_ID = json.loads(query_data)
    return

def get_sample_data(query_name):
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
                'sha256Hash': QUERY_ID[query_name],
                'version': '1'
            }
        },
        'variables': {
            # "id": "WFJhbmtpbmdTZWFzb24tcDoy"
            # "vsResultId": "VnNIaXN0b3J5RGV0YWlsLXUtYWpjYWJhdHpxdXNyb2tleXBubW06UkVHVUxBUjoyMDIyMTExM1QxMzU3MDlfMTcyY2EzOTAtNzNlZC00MjBiLTg0NjItMWI3NjRlMjAwOTM1"
            # "myOutfitId": "TXlPdXRmaXQtdS1hamNhYmF0enF1c3Jva2V5cG5tbTox"
            # "saleGearId": "U2FsZUdlYXItMF8xNjczMzk1MjAwXzA"
            # "coopHistoryDetailId": "Q29vcEhpc3RvcnlEZXRhaWwtdS1hamNhYmF0enF1c3Jva2V5cG5tbToyMDIzMDEwNFQxMzUwMzVfZGJhYTUxMjYtYTBlYi00ZTFjLWI1MzMtYjU0NDIzOWVjZDY2"
            # "isRegular": True,
            # "isBankara": True,
            # "isXBattle": False,
            # "isLeague": False,
            # "isPrivate": False
            # "festId": "RmVzdC1KUDpKVUVBLTAwMDAy"
            "id": "RmVzdC1KUDpKVUVBLTAwMDAy"
            # "id": "Q2hhbGxlbmdlSm91cm5leS1qb3VybmV5XzE"

        }
    }


    response = requests.post(url, headers=header, cookies=cookie, json=body)
    if response.status_code != 200:
        print("Request failed.")
        sys.exit(1)
    text = json.loads(response.text)
    NSO_API_Helper.save_data(text, f"{query_name}.json", data_path)

if __name__ == '__main__':
    load_tokens()
    # load_query_ids()
    get_sample_data("RankingHoldersFestTeamRankingHoldersPaginationQuery")
    sys.exit(0)
