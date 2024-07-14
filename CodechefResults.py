import requests
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
from Competition import Competition


driver = webdriver.Chrome()
browser = driver


def get_penalty(s):
    s = s.split(':')
    return int(s[2]) + int(s[1]) * 60 + int(s[0]) * 3600


def search(url):
    try:
        browser.get(url)
        time.sleep(10)
        start_text = driver.execute_script('return document.body.getInnerHTML()')
        text = start_text.split('>Total Score</div>')
        tmp = text[1].split('</div>')
        text = tmp[0].split('>')[-1]
        T = tmp[3].split('</p>')[0].split('>')[-1]

        res = int(text)
        penalty = get_penalty(T)
        return res, penalty
    except BaseException:
        return -1, -1


print(search("https://www.codechef.com/rankings/START94C?itemsPerPage=100&order=asc&page=1&search=frusua"))


class CodechefResults:

    @staticmethod
    def find_user(contestId, nick):
        for letter in ['A', 'B', 'C', 'D']:
            link = f"https://www.codechef.com/rankings/{contestId}{letter}?itemsPerPage=100&order=asc&page=1&search={nick}&filterBy=Country%3DUkraine"
            result = search(link)
            if result != (-1, -1):
                return result
        return -1, -1

    @staticmethod
    def get_results(contestId, codechef_users, column, s, add):
        bonus = {
            7: add[3],
            6: add[3],
            5: add[3],
            4: add[2],
            3: add[2],
            2: add[1],
            1: add[0],
            0: add[0]
        }
        new_competition = Competition(s, column)
        results = []
        stars = int(new_competition.type)
        for nick in codechef_users:
            print(f"{nick} processing", end=' ', flush=True)
            result = CodechefResults.find_user(contestId, nick)
            if result != (-1, -1):
                rated = codechef_users[nick].codechef_stars() <= stars
                res = result[0] + bonus[codechef_users[nick].codechef_stars()]
                results.append((-res, result[1], nick, rated))
                print(res, result[1], rated, end=' ')
            print(f"! processed")
        results.sort()
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
            current_place = place[codechef_users[handle].is_official()][rated]
            new_competition.add_participant(codechef_users[handle], points, current_place, rated)
            print(handle, points, current_place, rated)
            place[codechef_users[handle].is_official()][rated] += 1
        return new_competition
