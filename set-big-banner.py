"""
Script for adding/updating big banners for Megogo/Okko
"""

import json
import logging
import sys
from datetime import datetime

import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

CLIENT_SECRET = {
  "type": "service_account",
  "project_id": "megogo-banners",
  "private_key_id": "1f5a0f04487560224a2fb38e19c8304e8de85ae9",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCg/nLL5/aXo/9c\n1OwiLxenzujh9i6gaqt0e0MsOs2ulViI2MBL8MWj3cr534zmEUwWBMY0U/bxwB1X\na2FYC2SdKVe2Ke3gASi7IZ2MzPEzIMGholdaB3A8glNzOLfLs+rT8XDHptve1f67\nUsvdj6W+dVjMpN8kl//xWowz+AIDZa8gDp8FP9wO1T/WN+QQ+Z+OG4smhVwpGxe1\n8OSmoPypBCyOsY5wo2xg/p1st2vX0pxgbCcCgOGTMtEC2y19BAMossHKXtndvEsm\nids7v5GJqQOD5AUR6EF9GsRlmnV94/pLTVzoKThGYI6nhLzb3aTTXaY4GbgA8L16\n5AtoNlGBAgMBAAECggEAL9H0skmH7xn474+VRkAbtC4a8Ydo6SBWJka4uKoMzzcw\nMZHEaKovYpGuSVNULEBmC8JGR2PLXZqVfJJ6OydDLwWJNqQ0so1VlmQRQrHbUTcB\nHOw2Kxk7htWlSPvHaDvcXDECsWMIOyPwQp8AzCJvdmevxTWRzHJTxVKCg6s+mdhB\nMqANaeAmCBW+h403eActUrbC3vYD3++5XJcXhRD14ZdTesTg8CCBjZwaKoV1agA6\nnu774ymAYZRFYoQMxCq0NvT2hgJo+Fy0fenlXv+sQYKUshQ+CmoEPOuwt75C5GAo\niRL1UZmT/0ik70YUXEyKehKgKX6bZxG/D5soMLDmMwKBgQDOJijEsaTpPIiPE9ec\nBCaY8BhJGd/mKvBM7D7jOM49cmpoXYfGnJ+eVgN/wfwEKhtoKdSDKvgklTwFdUrP\nQFIeGnW3a8RQY7mUGxzyBuTVFCBiKTP1hlEA3LW8yOa4FlLUhkTJBDJjpDnK58FZ\nLBBqyTWWfBnZ/9Za2z+qPy4o8wKBgQDH7OvbDQLO4/NtjFlxWNIj32QL+GwB2iph\na2ecLc4vLbHgn3Dqxr8W7f6Y42Wur9S+4TPtKzoub7QKypj/dohR738BUnkRiaoR\nQe4t93+ySNl1foZEEvbiD1r+bVpaI/pQzXaXlBnKbHLCnoLiCosgjvprJNxDRQtx\nuQAkU6H4uwKBgCrXm1llYdRnFCpIAWMXKb5XB3UJv5JiEhaqcldekt4KTTrrVTBd\nlH6feZKvieSDq7Z2Gwg3geJ4cUThH276+xXugdBgwSfD0emJyPYzoJL339MGpRm9\nlFANjmdxiSFw4j3wuZLdIGu80ZXtnC0gDzliH5TqraS0mqO/NPf4sWspAoGAEmkD\n0xkgoBKnsPfSqLhoKXuByARpVcZUTsJIOT6SlQ+dKLUl/citghwKbOPL0klIywcL\n9BQd+Ha62p+LdULiDMGELYf9tBq8OXibyUnYTX+d3s726D/i0jBdzb4eKtzTSSuS\ndyThNx3Dd56HKO+VnjrsXn93dQ5fnmpN1AqLiM8CgYEAq/4NasqrLp2sZfKIBykw\nqNOMCKJ39VJCTv/jg56fNMwOFk3VlA1+qXjEciCoAfbd2Ug8/RZhWLD6yMdooyNb\n0cvg7/qWxV7Brhkv5HQptMjoifKtcOLJ7vUIZnbz+kHjmjrMZLS6upVo+U3T8n7D\nI1NKUIKuUi5klY1eg+wDsKE=\n-----END PRIVATE KEY-----\n",
  "client_email": "daf8fg34weri@megogo-banners.iam.gserviceaccount.com",
  "client_id": "114551878552598260371",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/daf8fg34weri%40megogo-banners.iam.gserviceaccount.com"
}
MEGOGO_BANNERS_URL = 'https://docs.google.com/spreadsheets/d/1nWqPNCRQebWLb2UoZvY6TKt9ff57YhfTezJZi7AGIlk/edit#gid=0'
TARGET_JSON_LOCATION = '/mnt/HC_Volume_2832716/www.fw.kivi.ua/firmware/'
TARGET_JSON_NAME = 'row_rel_ua_4.json'


def get_data_from_spreadsheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(CLIENT_SECRET, scope)
    client = gspread.authorize(credentials)
    try:
        sheet_1 = client.open_by_url(MEGOGO_BANNERS_URL).get_worksheet(0)
    except Exception as e:
        logging.error(f'Error in get_data_from_spreadsheet(): {e}')
        sys.exit(1)
    return sheet_1.get_all_records()


def get_spreadsheet_modification_time(sheet_url):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(CLIENT_SECRET, scope)
    client = gspread.authorize(credentials)
    sheet = client.open_by_url(sheet_url)
    revisions_uri = 'https://www.googleapis.com/drive/v3/files/{}/revisions'.format(sheet.id)
    headers = {'Authorization': 'Bearer {}'.format(credentials.get_access_token().access_token)}
    response = requests.get(revisions_uri, headers=headers).json()
    return response['revisions'][-1]['modifiedTime']


def set_banner(name, locale, img_url, count, start, end, interval):
    banner = {
        "start_time": start,
        "expire_time": end,
        "img": img_url,
        "root": True,
        "count": count,
        "frame": {
            "top": 830,
            "left": 585
        },
        "repeat": interval * 24 * 60 * 60 * 1000,
        "type": "kivi_tv",
        "buttons": [
            {
                "text": "$Accept",
                "style": "button_one_hrn",
                "action": "startActivity",
                "condition": "package",
                "package": "tv.okko.androidtv",
                "analytic_key": "gnezdo_okko",
                "analytic_value": "Accept"
            },
            {
                "text": "$skip",
                "style": "button_one_hrn",
                "action": "finish",
                "analytic_key": "gnezdo_okko",
                "analytic_value": "Skip"
            }
        ]
    }
    return banner


def update_file(element, file_path, row_number, new_element=False):
    with open(file_path, mode='r', encoding='utf8') as f:
        json_contents = json.loads(f.read())
    for item in json_contents['items']:
        if item['id'] == 'megogo_1':
            if new_element:
                item['content'].insert(row_number, element)
            else:
                item['content'][row_number] = element
            break
    json_contents['creation_time'] = datetime.now().strftime('%d.%m.%yT%H:%M')
    return json_contents


def main():
    sheet1_timestamp = datetime.strptime(get_spreadsheet_modification_time(MEGOGO_BANNERS_URL)[:19],
                                         '%Y-%m-%dT%H:%M:%S')
    if (datetime.now() - sheet1_timestamp).total_seconds() < (60 * 60 * 24 - 30):
        logging.basicConfig(filename='set-big-banner.log', level=logging.WARNING)
        banner = set_banner('test', 'RU', 'http://fw.kivi.ua/firmware/banner2ru/optimum_1920х1080.png')
        print(banner)
        logging.shutdown()


if __name__ == '__main__':
    main()
