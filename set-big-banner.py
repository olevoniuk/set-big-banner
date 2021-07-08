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
  "project_id": "set-big-banner",
  "private_key_id": "cfc34e27449de31d2462da462e3d47d0e69090d4",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQChSx1SImzEG3VK\ndhHYCqq+V7m8N7IEe55vsnSBWqavaBC0ILlcp71HUwpLwQd6rAvbu0aBDaBPyJSP\nn+fB7ACKDnhyovbj1aph18io9gdUBVCjlnpLV2Q2R/q5dQyn9X30D9W6H+GcN0h7\ngIUVleRjWwOY2Az93JxYuxfNUQZt7127iphT5iNcMBiR8uTJsLh/C3Bv3ZtkM8el\nzfGbFWdXZDe8lKo9x+MDTZZ2s7ayq1a7DtD04yU73CIz/R5/7/l2OdDV7Jn/tcuY\niHLcF7F3R/gDqkAcbQDc0z4z1tT2MaWTIiWZj6eFpJBBQPAkCoEDNYh1BHd+2OFb\nsimHq4SZAgMBAAECggEALeGSoSMWwoA3EKvebpC2Ojf1JzPGqVzK2GYwmv1A7iOR\noNOwNsmmX4whISRzLrOTGfm/WAWaxSc/D04C3Jh4HM15+M4fofbNJVD/DQUTV5S9\neBNdjWH6KTC3gxrnMz3zisIYX34jLM9TCIKqGNZPJe4la0yGAY7IULtDzY1PYWTi\nS/5M6RdDESIgxf8GVDpwtUo09TlrvofBofqk6HfWQKA/c0aLwqMRWTVNtDeoZhFd\n8dLcoUi/CBP17+Dl9RtmFW3gwXEoF4vYpQZQlKVXvtccYHYaysJxGakJal+IWIPK\nElDuynB48nNl4Fi3aMx+S/KgB1nXWcUd6RHh74JhQwKBgQDch/DDsddzi1G6yg+V\n6N1zxlDWV2aENEHcEXrVQX48IYSHgMvZDH/hClYPBtL/xVzaUTxDROBn4X6XiOlY\nR9UipZvkLWCKqaYyE8Ek69AKVqSOUBrr3vF5AkAOFoWCYuJzo2c7vfGiBh6e22y4\nYJfL9pKGgU80FS/sWpQGur8HZwKBgQC7PCXUjxrRH9wRRxyErxA9W6k4eatVqzl/\nEn93g/3jcnrxLBFyD6Wej/SqyHcZg2M1Hujsc1SV1aNjvXW6NBqaYejWUZxRdcvs\n6k6eZvQUu/v5kHtInGi5/rrGxS3bQ4RwoPTCI7+JQGDh6xqv8H2WrMKzmN9LXnK9\nibolVeWT/wKBgFpNgBViOWsi3XCzVPZ5yFSkHG3olB4GmAFZVwcELoDI6M/juZVD\nPQoVhW/Zx4TceE0dfqO9DHb9Ky057vMrVuc9ETy6KBIfreJLnIdV2HajS/bKbnuv\nawm2FiyupDTj8P6RJrCb8tn5z4gVKcvGIeJvMUjKongdROZvoLWwupB5AoGAedWA\ntFjOVWgK1j9Uok4cHiEH8xTQ1XUOe854nTeJPLhgoZBQZc0isxPvXDYHsdVZ99X+\nMOY3EyyqHhvJgHmpGe4+CT+fnS4unSI2OEK77sYIB3PplO0aBHVp6i+iUDwV8Qf7\nXFzQpKn8oOVQP04ZGrOeGimOm0eBGC6HrwW+1tcCgYEAvEgBQrCAaY3jbtcglN5k\n8k3kMpBOt47fNzL516xO6tMFgt2yQ/LSIycKVE1LQa63Mzv+bR0Iu2Rqj/JQd1eE\njiz4h6xLyK5FYb4UDRo+4sW7J0klzTD//X2V8v+oB0lFJfd+NL6y0AHcFhvhEltq\nDxnaCrnAbX8yZx3hjVGerVU=\n-----END PRIVATE KEY-----\n",
  "client_email": "set-big-banner@set-big-banner.iam.gserviceaccount.com",
  "client_id": "116616314111251299137",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/set-big-banner%40set-big-banner.iam.gserviceaccount.com"
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
