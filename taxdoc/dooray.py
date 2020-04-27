from selenium import webdriver
from collections import namedtuple
from datetime import datetime, timedelta
import os
# https://chromedriver.storage.googleapis.com/index.html?path=81.0.4044.69/

Schedule = namedtuple('Schedule', 'date contents')


def date_to_str(sdt):
    if sdt:
        return sdt.strftime("%Y/%m/%d")  # %H:%M:%S
    else:
        return "-"


def today():
    t = datetime.now()
    return datetime(t.year, t.month, t.day)


def normalized_date(date_str=""):
    """
        2020.01.15   2020/01/15
        20.01.15     20/01/15
        01.15        01/15
    """
    t = date_str.strip().replace(".", "/").replace("-", "/").split("/")
    if len(t) == 3:
        if len(t[0]) == 4:
            # yyyy/mm/dd
            return datetime(int(t[0].strip()), int(t[1].strip()), int(t[2].strip()))
        if len(t[0]) == 2:
            # yy/mm/dd
            return datetime(int("20"+t[0].strip()), int(t[1].strip()), int(t[2].strip()))
    if len(t) == 2:
        # mm/dd
        return datetime(datetime.now().year, int(t[0].strip()), int(t[1].strip()))
    return None


def range_date(start_date, end_date):
    if start_date is None or end_date is None:
        raise Exception("range_date error : " , start_date, end_date)
    start = start_date if start_date < end_date else end_date
    end = end_date if start_date < end_date else start_date
    current = start
    rsb = []
    while current <= end:
        rsb.append(current)
        current = current + timedelta(days=1)
    return rsb


def split_date(date_full_str=""):
    rsb = []
    for date_str in date_full_str.split(","):
        if "~" in date_str:
            rsb.extend(between_date(date_str))
        else:
            rsb.append(normalized_date(date_str))
    return rsb


def between_date(date_str=""):
    t = date_str.split("~")
    if len(t) == 2:
        start_date = normalized_date(t[0].strip())
        end_date = datetime(start_date.year, start_date.month, int(t[1].strip())) \
            if start_date and t[1].strip().isnumeric() else normalized_date(t[1].strip())
        return range_date(start_date, end_date)
    else:
        raise Exception("between date error : {}".format(t))


def parse_project_title_date_list(title=""):
    def extract_date(t):
        try:
            if t.startswith("["):
                return t[1:t.index("]")]
            if t.startswith("("):
                return t[1:t.index(")")]
        except ValueError:
            return ""
    date_str = extract_date(title)
    rsb = []
    if date_str is None:
        return rsb
    if "," in date_str:
        rsb.extend(split_date(date_str))
    elif "~" in date_str:
        rsb.extend(between_date(date_str))
    elif normalized_date(date_str):
        rsb.append(normalized_date(date_str))
    return rsb


class DooraySchedule:
    def __init__(self, user, passwd,
                 driver_path=os.path.abspath(__file__).replace("dooray.py", "chromedriver"), domain="naverunion"):
        option = webdriver.ChromeOptions()
        option.headless = True
        option.add_argument('--lang=ko-KR')
        option.add_argument('--user-agent="Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/37.0.2049.0 Safari/537.36"')
        option.add_argument("window-size=1024x768")
        self._url = "https://{}.dooray.com".format(domain)
        d = webdriver.Chrome(driver_path, chrome_options=option)
        d.implicitly_wait(3)
        d.get(self._url)
        d.find_element_by_css_selector("input[title=\"아이디\"]").send_keys(user)
        d.find_element_by_css_selector("input[title=\"비밀번호\"]").send_keys(passwd)
        d.find_element_by_css_selector("button[type=\"submit\"]").click()
        self._driver = d

    def get_today_calendar(self):
        """
        달력에서 오늘의 일정을 크롤링한다
        """
        d = self._driver
        d.get("{}/calendar".format(self._url))
        # 일간 프로젝트로 변경
        d.find_element_by_css_selector("span.calendar-date-navigation button.dropdown-toggle").click()
        d.find_element_by_css_selector("span.calendar-date-navigation ul.dropdown-menu li:first-child").click()
        dt_str = date_to_str(normalized_date(d.find_element_by_css_selector("span.calendar-date").text.strip()))

        result = []
        for row in d.find_elements_by_css_selector(".tui-full-calendar-weekday-schedule-title") or []:
            datetime_str = "{} 00:00".format(dt_str)
            contents = row.text
            result.append(Schedule(datetime_str, contents))
        for row in d.find_elements_by_css_selector(".tui-full-calendar-time-schedule-content") or []:
            time_str = row.find_element_by_css_selector("div.schedule-info strong").text.strip()
            datetime_str = "{} {}".format(dt_str, time_str)
            contents = row.find_element_by_css_selector("span.schedule-content").text.strip()
            result.append(Schedule(datetime_str, contents))
        return result

    def get_today_project(self, project_id="2383317213373131941"):
        d = self._driver
        d.get("{}/project/{}/workflowIds=all&page=1".format(self._url, project_id))
        result = []
        for row in d.find_elements_by_css_selector("div.post-item") or []:
            status = row.find_elements_by_css_selector("span.workflow-badge")
            if len(status) <= 0 or status[0] == "완료":
                continue
            title = row.find_element_by_css_selector("span.subject").text
            today_str = date_to_str(today()) + " __:__"
            if today() not in parse_project_title_date_list(title):  # 오늘 이슈인지
                continue

            result.append(Schedule(today_str,  title))
        return result

    def close(self):
        if self._driver:
            self._driver.close()