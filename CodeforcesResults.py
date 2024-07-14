import requests
from Competition import Competition


class CodeforcesResults:

    @staticmethod
    def get_results(contestId, cf_users, column, s):
        url = f'https://codeforces.com/api/contest.standings?contestId={contestId}&showUnofficial=true'
        response = requests.get(url)
        if response.status_code != 200:
            print(f'{response.status_code}: incorrect parameters (check contest id), try again')
            print(url)
            exit(1)
        data = response.json()
        possible_types = ['CONTESTANT', 'OUT_OF_COMPETITION']
        cf_nicks = cf_users.keys()
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
        new_competition = Competition(s, column)
        for participant in data["result"]["rows"]:
            if participant["party"]["participantType"] not in possible_types:
                continue
            if participant["party"]["members"][0]["handle"] not in cf_nicks:
                continue
            handle = participant["party"]["members"][0]["handle"]
            points = participant["points"]
            rated = participant["party"]["participantType"] == "CONTESTANT"
            current_place = place[cf_users[handle].is_official()][rated]
            new_competition.add_participant(cf_users[handle], points, current_place, rated)
            print(handle, points, current_place, rated)
            place[cf_users[handle].is_official()][rated] += 1
        return new_competition
