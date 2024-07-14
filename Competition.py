from CompetitionResult import CompetitionResult


def parse(s) -> (str, str):
    s = s.split('_')
    return s[0], s[1], s[2]


def calc_points(c, points, mx_points, n_group, place):
    return c * 50 * points * (2 * n_group - 2) / (mx_points * (n_group + place - 2))


class Competition:

    def __init__(self, s, column):
        self.platform, self.type, self.description = parse(s)

        self.contestants = {
            True: {  #official
                True: {  # Rated

                },
                False: {  # Unrated

                }
            },
            False: {  #unofficial
                True: {  # Rated

                },
                False: {  # Unrated

                }
            },
        }
        self.mx_points = {
            True: {
                True: -1,
                False: -1
            },
            False: {
                True: -1,
                False: -1
            },
        }
        self.column = column

    def get_coeff(self) -> float:
        if self.platform == "codeforces":
            if self.type == "1":  # div 1
                return 1
            if self.type == "2":  # div 2
                return 0.75
            if self.type == "3":  # div 3
                return 0.4
            if self.type == "4":  # div 4
                return 0.25
            if self.type == "1+2":  # div 1 + div 2
                return 1.5
        if self.platform == "atcoder":
            if self.type == "abc":
                return 0.7
            if self.type == "arc":
                return 1
            if self.type == "agc":
                return 2
        if self.platform == "tlx":
            return 1
        if self.platform == "codechef":
            if self.type == "5":
                return 0.6
            if self.type == "6":
                return 0.7
            if self.type == "7":
                return 0.8
        if self.platform == "dmoj":
            return 1
        raise BaseException("no such platform")

    def calc_max_points(self, official, rated):
        self.mx_points[official][rated] = max(self.mx_points[official][rated], 1)
        for contestant in self.contestants[official][rated]:
            self.mx_points[official][rated] = max(self.mx_points[official][rated],
                                                  self.contestants[official][rated][contestant].score)

    def calc_points(self, points, place, rated, official):
        coeff = self.get_coeff()
        n_group = max(10, len(self.contestants[official][rated]))
        if self.mx_points[official][rated] == -1:
            self.calc_max_points(official, rated)
        mx_points = self.mx_points[official][rated]
        #print(mx_points, n_group + place - 2)
        return calc_points(coeff, points, mx_points, n_group, place)

    def add_participant(self, user, score, place, rated):
        if place != -1:
            self.contestants[user.is_official()][rated][user.name] = CompetitionResult(score, place, user)

    def add_points_to_user(self, user, score, place, rated):
        if place != -1:
            #print(self.platform, self.type, self.description)
            user.add_points(self.calc_points(score, place, rated, user.is_official()))
