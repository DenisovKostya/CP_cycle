def parse_competition_result(s):
    if isinstance(s, str) and s != "":
        try:
            rated = s[-1] == '+'
            s = s[:-1]
            s = s.split('_')
            score = float(s[1])
            place = int(s[0])
            return score, place, rated
        except BaseException as e:
            print(e)
            return 0, -1, False
    return 0, -1, False


def _sgn(rated):
    if rated:
        return '+'
    return '-'


def convert_competition_result(score, place, rated):
    return f"{place}_{score}{_sgn(rated)}"


class CompetitionResult:

    def __init__(self, score, place, user):
        self.score = score
        self.place = place
        self.user = user
