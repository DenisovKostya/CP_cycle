import os
import onlinejudge
from Competition import Competition
from stdiomask import getpass


class AtcoderResults:

    @staticmethod
    def get_results(contestId, handles_by_judges, column, s):

        class StandingsRow:
            def __init__(self, user, place, points, penalty, user_group):
                self.user = user
                self.place = place
                self.points = points
                self.penalty = penalty
                self.user_group = user_group

            def __str__(self):
                return f'{self.place}) {self.user}: ({self.points}, {self.penalty}, user_group = {self.user_group}, official = {self.user.is_official})'

        class Standings:
            def __init__(self, online_judge, contest_id, start_date):
                self.online_judge = online_judge
                self.contest_id = contest_id
                self.start_date = start_date
                self.results = []
                self.last_id = [-1 for i in range(3)]
                self.n_participants = [0 for i in range(3)]

            def add_result(self, handle, points, penalty, user_group):
                user = handles_by_judges[handle]
                place = 1
                if self.last_id[user_group] != -1:
                    place = self.results[self.last_id[user_group]].place
                    if points != self.results[self.last_id[user_group]].points or penalty != self.results[self.last_id[user_group]].penalty:
                        place = self.n_participants[user_group] + 1
                self.n_participants[user_group] += 1
                self.last_id[user_group] = len(self.results)
                self.results.append(StandingsRow(user, place, points, penalty, user_group))

            def empty(self):
                for result in self.results:
                    if result.points != 0:
                        return False
                return True

            def __str__(self):
                return '\n'.join([str(row) for row in self.results])

        def get_atcoder_standings(contest_id):
            def get_credentials():
                if os.path.isfile('data/atcoder_credentials.txt'):
                    f = open('data/atcoder_credentials.txt', 'r')
                    credentials = f.read().split()
                    f.close()
                    if len(credentials) == 2:
                        return tuple(credentials)
                username = input('Enter atcoder username: ')
                password = getpass(prompt='Enter atcoder password: ')
                return username, password

            def save_credentials(username, password):
                f = open('data/atcoder_credentials.txt', 'w')
                print(username, password, file=f)
                f.close()

            def login():
                atcoder = onlinejudge.service.atcoder.AtCoderService()
                while True:
                    try:
                        username, password = get_credentials()
                        atcoder.login(get_credentials=lambda username=username, password=password: (username, password))
                        save_credentials(username, password)
                        break
                    except onlinejudge.type.LoginError:
                        print('Incorrect username or password, please try again')
                session = onlinejudge.service.atcoder.utils.get_default_session()
                return session

            def get_contest_date(session, contest_id):
                url = f'https://atcoder.jp/contests/{contest_id}'
                response = session.get(url, allow_redirects=False).text
                pos = response.find('<small class="contest-duration">')
                pos = response.find('</time>', pos)
                pos = response.rfind('>', 0, pos) + 1
                year = response[pos:pos + 4]
                month = response[pos + 5:pos + 7]
                day = response[pos + 8:pos + 10]
                return f'{day}.{month}.{year}'

            def get_rated_range_max(contest_id):
                if contest_id.find('abc') != -1:
                    return 2000
                if contest_id.find('arc') != -1:
                    return 2800
                return 10 ** 9

            session = login()
            start_date = get_contest_date(session, contest_id)
            url = f'https://atcoder.jp/contests/{contest_id}/standings/json'
            response = session.get(url, allow_redirects=False)
            if response.status_code != 200:
                print(f'{response.status_code}: incorrect parameters (check contest id), try again')
                exit(1)
            data = response.json()
            standings = Standings('atcoder', contest_id, start_date)
            results = []
            for row in data['StandingsData']:
                if not row['IsRated'] and False:
                    continue
                handle = row['UserScreenName']
                if handle not in handles_by_judges:
                    continue
                if not row['TotalResult']['Count']:
                    continue
                points = row['TotalResult']['Score'] // 100
                penalty = row['TotalResult']['Elapsed'] // 10 ** 9 + row['TotalResult']['Penalty'] * 5 * 60
                user_group = 0
                if row['OldRating'] < get_rated_range_max(contest_id):
                    user_group = 0
                else:
                    user_group = 1
                rated = user_group == 0
                results.append((-points, penalty, handle, rated))
            results.sort()
            new_competition = Competition(s, column)
            place = {
                True: {
                    True: 1,
                    False: 1
                },
                False: {
                    True: 1,
                    False: 1
                }
            }
            for result in results:
                handle = result[2]
                points = -result[0]
                rated = result[3]
                current_place = place[handles_by_judges[handle].is_official()][rated]
                new_competition.add_participant(handles_by_judges[handle], points, current_place, rated)
                print(handle, points, current_place, rated)
                place[handles_by_judges[handle].is_official()][rated] += 1
            return new_competition

        return get_atcoder_standings(contestId)
