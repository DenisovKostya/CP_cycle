from __future__ import print_function

import os.path
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from User import User
from Competition import Competition

from CompetitionResult import parse_competition_result, convert_competition_result
from GoogleSheetCell import GoogleSheetCell


def name_of_column(x):
    if x <= 26:
        return chr(ord('A') + x - 1)
    x -= 1
    a = x / 26 - 1
    b = x % 26
    return str(chr(ord('A') + a)) + str(chr(ord('A') + b))


def process_line(s):
    if isinstance(s, str) and s != "-":
        return s
    return ""


def safe(arr, i, j):
    try:
        return arr[i][j]
    except BaseException as e:
        print(e, "37 line")
        return ""


def process_elem(row, num):
    try:
        return process_line(row[num])
    except BaseException:
        print("error")
        return ""


def _get_start(s):
    if not s:
        return ""
    return s.split(' → ')[0]


def _get_end(s):
    if not s:
        return ""
    return s.split(' → ')[1]


class Information:
    def parse_row(self, row, i):
        nicks = {
            'codeforces': process_elem(row, 3),
            'atcoder': process_elem(row, 4),
            'tlx': process_elem(row, 5),
            'codechef': process_elem(row, 6),
            'dmoj': process_elem(row, 7)
        }
        start_ratings = {
            'codeforces': _get_start(process_elem(row, 9)),
            'atcoder': _get_start(process_elem(row, 10)),
            'tlx': _get_start(process_elem(row, 11)),
            'codechef': _get_start(process_elem(row, 12)),
            'dmoj': _get_start(process_elem(row, 13))
        }
        last_ratings = {
            'codeforces': _get_end(process_elem(row, 9)),
            'atcoder': _get_end(process_elem(row, 10)),
            'tlx': _get_end(process_elem(row, 11)),
            'codechef': _get_end(process_elem(row, 12)),
            'dmoj': _get_end(process_elem(row, 13))
        }
        self.users.append(User(reg_time=row[0], name=row[1], uni=row[2], nicks=nicks, start_ratings=start_ratings,
                               row_number=i, contact=process_elem(row, 8), last_ratings=last_ratings,
                               upd_tlx=self.update_tlx))

    def __init__(self, update_tlx):
        self.users = []
        self.competitions = []
        self.creds = None
        self.update_view_table = False
        self.update_tlx = update_tlx
        self.SAMPLE_SPREADSHEET_ID = "1KaNBf_sL0QSopzJAOnlvt8gzeR-ntXN5ylsR8sf-EfE"

        # 1--_DicBzF8S2-jvF2EfygfGYG8daHyaiUVcmgyAS8aw
        # "1t2Ox_3i9ekL3ox0JOyKxnD-w7S2myFkswyE2LeEKeRI" old id
        self.SAMPLE_RANGE_NAME = 'A1:100'  # если количество рядков больше 100 надо увеличить
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.

        self.SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file'
            #'https://www.googleapis.com/auth/drive',
            # 'https://www.googleapis.com/auth/spreadsheets.readonly'
        ]
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

    def parse_competitions(self, row):
        for i in range(14, len(row)):
            if not row[i]:
                break
            self.competitions.append(Competition(row[i], i))

    def format_for_platform(self, platform):
        return {user.nicks[platform]: user for user in self.users if user.nicks[platform]}

    def get_free_column(self):
        return 14 + len(self.competitions)

    def __enter__(self):
        try:
            print("GO HERE")
            service = build('sheets', 'v4', credentials=self.creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                        range=self.SAMPLE_RANGE_NAME).execute()
            values = result.get('values', [])

            if not values:
                raise BaseException('No data found.')

            # for row in values:
            #    print(row)
            self.parse_competitions(values[0])
            for i in range(1, len(values)):
                # 0 - для времени
                # 1 - ФИО
                # 2 - ВУЗ
                # 3 - codeforces ник
                # 4 - atcoder ник
                # 5 - tlx ник
                # 6 - codechef ник
                # 7 - dmoj ник
                # 8 - контакт
                # 9 - начальный codeforces rating
                # 10 - начальный atcoder rating
                # 11 - начальный tlx rating
                # 12 - начальный codechef rating
                # 13 - начальный dmoj rating
                self.parse_row(values[i], i)
                for j in range(14, 14 + len(self.competitions)):
                    print(j)
                    #print(j - 14, len(self.competitions), len(self.users), "here", *parse_competition_result(safe(values, i, j)))
                    self.competitions[j - 14].add_participant(self.users[-1], *parse_competition_result(safe(values, i, j)))
                    #print("out here")
        except HttpError as err:
            print(err)
        except BaseException as err:
            print(err)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("exit")
        try:
            service = build('sheets', 'v4', credentials=self.creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            #sheet.values().update(
            #    spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
            #    range="J2:K3",
            #    includeValuesInResponse=True,
            #    valueInputOption="USER_ENTERED",
            #    body={
            #      "values": [
            #        [
            #          "text", "text2"
            #        ],
            #          ["t1", "t2"]
            #      ]
            #    }
            #).execute()
            n = len(self.users)
            m = 14 + len(self.competitions)
            arr = [{"values": [GoogleSheetCell.formated_cell("") for j in range(m)]} for i in range(n)]
            print(n, m)
            for competition in self.competitions:
                for official in competition.contestants:
                    for rated in competition.contestants[official]:
                        for name in competition.contestants[official][rated]:
                            result = competition.contestants[official][rated][name]
                            arr[result.user.row_number - 1]["values"][competition.column] = GoogleSheetCell.formated_cell(
                                convert_competition_result(
                                    result.score,
                                    result.place,
                                    rated
                                )
                            )
                            competition.add_points_to_user(result.user, result.score, result.place, rated)

            for index, user in enumerate(self.users):
                arr[index]["values"][0] = GoogleSheetCell.formated_cell(user.reg_time)
                arr[index]["values"][1] = GoogleSheetCell.formated_cell(user.name)
                arr[index]["values"][2] = GoogleSheetCell.formated_cell(user.uni)
                arr[index]["values"][3] = GoogleSheetCell.formated_cell(
                    f"=ГИПЕРССЫЛКА(\"{user.codeforces_link()}\"; \"{user.nicks['codeforces']}\")",
                    user.codeforces_color(),
                    True,
                    True
                )
                arr[index]["values"][4] = GoogleSheetCell.formated_cell(
                    f"=ГИПЕРССЫЛКА(\"{user.atcoder_link()}\"; \"{user.nicks['atcoder']}\")",
                    user.atcoder_color(),
                    True,
                    True
                )
                arr[index]["values"][5] = GoogleSheetCell.formated_cell(
                    f"=ГИПЕРССЫЛКА(\"{user.tlx_link()}\"; \"{user.nicks['tlx']}\")",
                    user.tlx_color(),
                    True,
                    True
                )
                arr[index]["values"][6] = GoogleSheetCell.formated_cell(
                    f"=ГИПЕРССЫЛКА(\"{user.codechef_link()}\"; \"{user.nicks['codechef']}\")",
                    user.codechef_color(),
                    True,
                    True
                )
                arr[index]["values"][7] = GoogleSheetCell.formated_cell(
                    f"=ГИПЕРССЫЛКА(\"{user.dmoj_link()}\"; \"{user.nicks['dmoj']}\")",
                    user.dmoj_color(),
                    True,
                    True
                )
                arr[index]["values"][8] = GoogleSheetCell.formated_cell(user.contact)
                arr[index]["values"][9] = GoogleSheetCell.formated_cell(
                    user.get_change_rating('codeforces'),
                    background=user.get_color_delta('codeforces')
                )
                arr[index]["values"][10] = GoogleSheetCell.formated_cell(
                    user.get_change_rating('atcoder'),
                    background=user.get_color_delta('atcoder')
                )
                arr[index]["values"][11] = GoogleSheetCell.formated_cell(
                    user.get_change_rating('tlx'),
                    background=user.get_color_delta('tlx')
                )
                arr[index]["values"][12] = GoogleSheetCell.formated_cell(
                    user.get_change_rating('codechef'),
                    background=user.get_color_delta('codechef')
                )
                arr[index]["values"][13] = GoogleSheetCell.formated_cell(
                    user.get_change_rating('dmoj'),
                    background=user.get_color_delta('dmoj')
                )
            #for i in range(n):
            #    print(arr[i]["values"][14])
            print(arr)
            #sheet.values().update(
            #    spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
            #    range=f"A2:{name_of_column(m)}{1 + n}",
            #    includeValuesInResponse=True,
            #    valueInputOption="USER_ENTERED",
            #    body = {
            #        'values': arr
            #    }
            #).execute()
            #print(n, m, 1 + n, m + 5)
           # sheet.batchUpdate(
            #    spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
            #    body={
             # "requests": [
             #   {
             #     "updateDimensionProperties": {
             #       "range": {
              #        "sheetId": 382460164,
              #        "dimension": "COLUMNS",
               #       "startIndex": 0,
                 #     "endIndex": 20
                   # },
                   # "properties": {
                   #   "pixelSize": 160
                   # },
                  #  "fields": "pixelSize"
                 # }
                #},
                #{
                 # "updateDimensionProperties": {
                 #   "range": {
                 #     "sheetId": 382460164,
                     # "dimension": "ROWS",
                    #  "startIndex": 0,
                   #   "endIndex": 40
                  #  },
                 #   "properties": {
                #      "pixelSize": 40
              #      },
               #     "fields": "pixelSize"
              #    }
              #  }
             # ]
            #}).execute()
            #for i in arr:
             #   print(len(i))
            #time.sleep(5)
            sheet.batchUpdate(
                spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                body={
                    "requests": [
                        {
                            "updateCells": {
                                "rows": arr,
                                "fields": "*",
                                "start": {
                                    "columnIndex": 0,
                                    "rowIndex": 1,
                                    "sheetId": 1204596574
                                        # 1994838323 old id
                                }
                            }
                        }
                    ]
                }
            ).execute()
            print("UPDATE", self.update_view_table)
            if not self.update_view_table:
                return

            self.users.sort(key=lambda user: -user.total)
            view_sheet_id = "1d8fyyWbWhWE_O9LQDihV7s10JTLPJChv5GtRAKsWW90"
            # 12YQKDM5nNnhHq4SHTUUVpIBoAOidCsgkjXHHpAgDKkg
            # "1ASkkoDfLYcns-1T8-vYB51VSTLDnbA2rmyg_L9kCmMo" old id
            view_arr = [{"values": [GoogleSheetCell.formated_cell("") for j in range(m)]} for i in range(n)]
            for i in range(len(self.users)):
                self.users[i].row_number = i
            for index, user in enumerate(self.users):
                cnt_bigger = 1
                for another_user in self.users:
                    if another_user.total > user.total:
                        cnt_bigger += 1
                view_arr[index]["values"][0] = GoogleSheetCell.formated_cell(cnt_bigger)
                view_arr[index]["values"][1] = GoogleSheetCell.formated_cell(user.name)
                view_arr[index]["values"][2] = GoogleSheetCell.formated_cell(user.uni)
                view_arr[index]["values"][3] = GoogleSheetCell.formated_cell(
                    f"=ГИПЕРССЫЛКА(\"{user.codeforces_link()}\"; \"{user.nicks['codeforces']}\")",
                    user.codeforces_color(),
                    True,
                    True
                )
                view_arr[index]["values"][4] = GoogleSheetCell.formated_cell(
                    f"=ГИПЕРССЫЛКА(\"{user.atcoder_link()}\"; \"{user.nicks['atcoder']}\")",
                    user.atcoder_color(),
                    True,
                    True
                )
                view_arr[index]["values"][5] = GoogleSheetCell.formated_cell(
                    f"=ГИПЕРССЫЛКА(\"{user.tlx_link()}\"; \"{user.nicks['tlx']}\")",
                    user.tlx_color(),
                    True,
                    True
                )
                view_arr[index]["values"][6] = GoogleSheetCell.formated_cell(
                    f"=ГИПЕРССЫЛКА(\"{user.codechef_link()}\"; \"{user.nicks['codechef']}\")",
                    user.codechef_color(),
                    True,
                    True
                )
                view_arr[index]["values"][7] = GoogleSheetCell.formated_cell(
                    f"=ГИПЕРССЫЛКА(\"{user.dmoj_link()}\"; \"{user.nicks['dmoj']}\")",
                    user.dmoj_color(),
                    True,
                    True
                )
                view_arr[index]["values"][8] = GoogleSheetCell.formated_cell(
                    user.get_change_rating('codeforces'),
                    background=user.get_color_delta('codeforces')
                )
                view_arr[index]["values"][9] = GoogleSheetCell.formated_cell(
                    user.get_change_rating('atcoder'),
                    background=user.get_color_delta('atcoder')
                )
                view_arr[index]["values"][10] = GoogleSheetCell.formated_cell(
                    user.get_change_rating('tlx'),
                    background=user.get_color_delta('tlx')
                )
                view_arr[index]["values"][11] = GoogleSheetCell.formated_cell(
                    user.get_change_rating('codechef'),
                    background=user.get_color_delta('codechef')
                )
                view_arr[index]["values"][12] = GoogleSheetCell.formated_cell(
                    user.get_change_rating('dmoj'),
                    background=user.get_color_delta('dmoj')
                )
                view_arr[index]["values"][13] = GoogleSheetCell.formated_cell(user.total)
            for competition in self.competitions:
                for official in competition.contestants:
                    for rated in competition.contestants[official]:
                        for name in competition.contestants[official][rated]:
                            result = competition.contestants[official][rated][name]
                            points = competition.calc_points(result.score, result.place, rated, result.user.is_official())
                            view_arr[result.user.row_number]["values"][competition.column] = GoogleSheetCell.formated_cell(
                                points
                            )
            sheet.batchUpdate(
                spreadsheetId=view_sheet_id,
                body={
                    "requests": [
                        {
                            "updateCells": {
                                "rows": view_arr,
                                "fields": "*",
                                "start": {
                                    "columnIndex": 0,
                                    "rowIndex": 2,
                                    "sheetId": 0
                                }
                            }
                        }
                    ]
                }
            ).execute()
        except HttpError as err:
            print(err)

    def add_competition(self, competition):
        self.competitions.append(competition)
