from selenium import webdriver
from collections import namedtuple
import os
# https://chromedriver.storage.googleapis.com/index.html?path=81.0.4044.69/

Schedule = namedtuple('Schedule', 'start end contents')


class DooraySchedule:
    def __init__(self, user, passwd, domain="naverunion"):
        option = webdriver.ChromeOptions()
        option.headless = True
        option.add_argument('--lang=ko-KR')
        option.add_argument('--user-agent="Chrome/37.0.2049.0 Safari/537.36"')
        option.add_argument("window-size=1024x768")
        driver_path = os.path.abspath(__file__).replace("dooray.py", "chromedriver")
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
        dt = d.find_element_by_css_selector("span.calendar-date").text.strip()
        result = []
        for row in d.find_elements_by_css_selector(".tui-full-calendar-weekday-schedule-title"):
            result.append(Schedule("{} 00:00".format(dt), "{} 24:00".format(dt), row.text))
        for row in d.find_elements_by_css_selector(".tui-full-calendar-time-schedule-content"):
            result.append(Schedule("{} {}".format(dt, row.find_element_by_css_selector("div.schedule-info strong").text)
                                   , ""
                                   , row.find_element_by_css_selector("span.schedule-content").text))
        return result

    def get_today_project(self):
        pass

    def close(self):
        if self._driver:
            self._driver.close()


if __name__ == "__main__":
    dooray = DooraySchedule("아이디", "암호")
    r = dooray.get_today_calendar()
    print(r)