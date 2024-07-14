import requests
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time


driver = webdriver.Chrome()
browser = driver


def get_cf_rating(user):
    try:
        url_cf = user.codeforces_link()
        r = requests.get(url_cf)
        # print(r.text)
        t = r.text.split('Contest rating:')
        return int(t[1].split('>')[1].split('<')[0])
    except BaseException:
        return 0


def get_atcoder_rating(user):
    try:
        url_atcoder = user.atcoder_link()
        r = requests.get(url_atcoder)
        # print(r.text)
        return int(r.text.split('Rating')[1].split('>')[4].split('<')[0])
    except BaseException:
        return 0


def get_tlx_rating(user):
    try:
        browser.get(user.tlx_link())
        html = browser.page_source
        time.sleep(5)
        last_height = driver.execute_script('return document.getElementsByTagName("td")[3].innerHTML')
        return int(last_height)
    except BaseException:
        return 0


def get_codechef_rating(user):
    try:
        url_codechef = user.codechef_link()
        r = requests.get(url_codechef)
        #print(r.text.split("<div class=\"rating-number\">")[1].split('<')[0])
        return int(r.text.split("<div class=\"rating-number\">")[1].split('<')[0].split('?')[0])
    except BaseException:
        return 0


def get_dmoj_rating(user):
    try:
        url_dmoj = user.dmoj_link()
        r = requests.get(url_dmoj)
        #print(r.text.split('Rating')[1].split('</span></span></div>')[0].split('>')[-1])
        return int(r.text.split('Rating')[1].split('</span></span></div>')[0].split('>')[-1])
    except BaseException:
        return 0


def difference_color(start_rating, current_rating):
    try:
        current_rating = int(current_rating)
        start_rating = int(start_rating)
        delta = current_rating - start_rating
        if delta == 0:
            return (1, 1, 1)

        r = 0
        g = 0
        b = 0
        alpha = (15 + 2 * abs(delta)) / 1000
        if delta < 0:
            r = 255
        else:
            g = 255

        nr = max(0, min(255, ((1 - alpha) * 255 + alpha * r + 0.5)))
        ng = max(0, min(255, ((1 - alpha) * 255 + alpha * g + 0.5)))
        nb = max(0, min(255, ((1 - alpha) * 255 + alpha * b + 0.5)))
        return (nr / 255, ng / 255, nb / 255)
    except BaseException:
        return (1, 1, 1)


class User:

    def __init__(self, reg_time, name, uni, nicks, start_ratings, row_number, contact, last_ratings, upd_tlx):
        self.reg_time = reg_time
        self.name = name
        self.uni = uni
        self.nicks = nicks
        self.start_ratings = start_ratings
        self.row_number = row_number
        self.contact = contact
        self.ratings = dict()
        for i in start_ratings:
            #print(upd_tlx, i)
            if not upd_tlx and i == 'tlx':
                self.ratings[i] = int(last_ratings[i])
                if self.start_ratings[i] == "" and self.nicks[i]:
                    self.start_ratings[i] = self.ratings[i]
                continue
            self.ratings[i] = self.get_rating(i)
            if self.start_ratings[i] == "" and self.nicks[i]:
                self.start_ratings[i] = self.ratings[i]
        self.total = 0

    def get_rating(self, platform):
        if platform == "codeforces":
            return get_cf_rating(self)
        if platform == "atcoder":
            return get_atcoder_rating(self)
        if platform == "tlx":
            return get_tlx_rating(self)
        if platform == "codechef":
            return get_codechef_rating(self)
        if platform == "dmoj":
            return get_dmoj_rating(self)
        return 0

    def get_change_rating(self, platform):
        return f"{self.start_ratings[platform]} → {self.ratings[platform]}"

    def get_color_delta(self, platform):
        return difference_color(self.start_ratings[platform], self.ratings[platform])

    def get_start_rating(self, platform):
        if self.start_ratings[platform]:
            return self.start_ratings[platform]
        if platform == "codeforces":
            self.start_ratings[platform] = get_cf_rating(self)
            return self.start_ratings[platform]
        if platform == "atcoder":
            self.start_ratings[platform] = get_atcoder_rating(self)
            return self.start_ratings[platform]
        if platform == "tlx":
            self.start_ratings[platform] = get_tlx_rating(self)
            return self.start_ratings[platform]
        if platform == "codechef":
            self.start_ratings[platform] = get_codechef_rating(self)
            return self.start_ratings[platform]
        if platform == "dmoj":
            self.start_ratings[platform] = get_dmoj_rating(self)
            return self.start_ratings[platform]
        return 0

    def is_official(self):
        if isinstance(self.uni, str) and self.uni != "-":
            return True
        return False

    def atcoder_link(self):
        if self.nicks['atcoder']:
            return f"https://atcoder.jp/users/{self.nicks['atcoder']}"
        return ""

    def codeforces_link(self):
        if self.nicks['codeforces']:
            return f"https://codeforces.com/profile/{self.nicks['codeforces']}"
        return ""

    def tlx_link(self):
        if self.nicks['tlx']:
            return f"https://tlx.toki.id/profiles/{self.nicks['tlx']}"
        return ""

    def codechef_link(self):
        if self.nicks['codechef']:
            return f"https://codechef.com/users/{self.nicks['codechef']}"
        return ""

    def dmoj_link(self):
        if self.nicks['dmoj']:
            return f"https://dmoj.ca/user/{self.nicks['dmoj']}"
        return ""

    def convert_hex(self, h):
        return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

    def convert_rgb(self, h):
        return tuple([h[0] / 255, h[1] / 255, h[2] / 255])

    def codeforces_color(self):
        num = self.ratings['codeforces']
        if num <= 0:
            return (0, 0, 0)
        if num < 1200:
            return self.convert_rgb([128, 128, 128])
        if num < 1400:
            return self.convert_rgb([0, 128, 0])
        if num < 1600:
            return self.convert_rgb([3, 168, 158])
        if num < 1900:
            return self.convert_rgb([0, 0, 255])
        if num < 2100:
            return self.convert_rgb([170, 0, 170])
        if num < 2400:
            return self.convert_rgb([255, 140, 0])
        return self.convert_rgb([255, 0, 0])

    def atcoder_color(self):
        num = self.ratings['atcoder']
        if num <= 0:
            return (0, 0, 0)
        if num < 500:
            return self.convert_rgb([128, 128, 128])
        if num < 800:
            return self.convert_rgb([128, 64, 0])
        if num < 1200:
            return self.convert_rgb([0, 128, 0])
        if num < 1600:
            return self.convert_rgb([0, 192, 200])
        if num < 2000:
            return self.convert_rgb([0, 0, 255])
        if num < 2400:
            return self.convert_rgb([192, 192, 0])
        if num < 2600:
            return self.convert_rgb([255, 128, 0])
        return self.convert_rgb([255, 0, 0])

    def tlx_color(self):
        num = self.ratings['tlx']
        if num <= 0:
            return (0, 0, 0)
        if num < 1650:
            return self.convert_rgb([183, 183, 183])
        if num < 1750:
            return self.convert_rgb([112, 173, 71])
        if num < 2000:
            return self.convert_rgb([60, 120, 216])
        if num < 2200:
            return self.convert_rgb([112, 48, 160])
        if num < 2500:
            return self.convert_rgb([255, 232, 178])
        return self.convert_rgb([255, 0, 0])

    def codechef_color(self):
        num = self.ratings['codechef']
        if num <= 0:
            return (0, 0, 0)
        if num < 1400:
            return self.convert_rgb([102, 102, 102])
        if num < 1600:
            return self.convert_rgb([30, 125, 34])
        if num < 1800:
            return self.convert_rgb([51, 102, 204])
        if num < 2000:
            return self.convert_rgb([104, 66, 115])
        if num < 2200:
            return self.convert_rgb([255, 191, 0])
        if num < 2500:
            return self.convert_rgb([255, 127, 0])
        return self.convert_rgb([208, 1, 27])

    def dmoj_color(self):
        num = self.ratings['dmoj']
        if num <= 0:
            return (0, 0, 0)
        if num < 1000:
            return self.convert_rgb([153, 153, 153])
        if num < 1300:
            return self.convert_rgb([0, 169, 0])
        if num < 1600:
            return self.convert_rgb([0, 0, 255])
        if num < 1900:
            return self.convert_rgb([128, 0, 128])
        if num < 2400:
            return self.convert_rgb([255, 177, 0])
        return self.convert_rgb([238, 0, 0])

    def add_points(self, x):
        self.total += x

    def codechef_stars(self):
        num = self.ratings['codechef']
        if num <= 0:
            return 0
        if num < 1400:
            return 1
        if num < 1600:
            return 2
        if num < 1800:
            return 3
        if num < 2000:
            return 4
        if num < 2200:
            return 5
        if num < 2500:
            return 6
        return 7

    def get_delta(self, platform):
        return int(self.ratings[platform]) - int(self.start_ratings[platform])

    def get_summary_delta(self):
        return self.get_delta('codechef') + self.get_delta('dmoj') + self.get_delta('tlx') + self.get_delta('codeforces') + self.get_delta('atcoder')

