#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import namedtuple, Set
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
import time

# 네이버아이디, 성함, 별명, 전화번호마지막자리, 법인
CafeUser = namedtuple('CafeUser', 'id nick age gender date reply')


class NCafeLogin:
    def __init__(self, driver_path, cafe_url="https://cafe.naver.com/nunion"):
        option = webdriver.ChromeOptions()
        option.headless = True
        option.add_argument('--lang=ko-KR')
        option.add_argument('--user-agent="Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/37.0.2049.0 Safari/537.36"')
        option.add_argument("window-size=1024x768")
        d = webdriver.Chrome(driver_path, chrome_options=option)
        d.implicitly_wait(3)
        self._cafe_url = cafe_url
        self._driver = d
        self._club_id = 0
        self._username = None
        self._user_password = None
        self._driver_path = driver_path
        self._windows_handle = {}

    def login(self, user_name, user_password):
        """
        로그인 처리에서 봇으로 판정되면, 캡챠로 이동된다.
        그래서 우회 로직이 필요하다.
        """
        self._username = user_name
        self._user_password = user_password
        self._driver.get("https://nid.naver.com/nidlogin.login?url=" + self._cafe_url)
        self._driver.execute_script("""
            document.querySelector("#id").value = "{}"; 
            document.querySelector("#pw").value = "{}";
        """.format(user_name, user_password))
        webdriver.ActionChains(self._driver).move_by_offset(712, 384).perform()
        self.get_element(By.ID, "log.login").click()
        self._club_id = self._extract_club_id()
        return self

    def _extract_club_id(self):
        """
        로그인후 club 관리 페이지로 이동하면 club_id 를 URL 에서 알아낼수 있다.
        """
        self.get_element(By.CLASS_NAME, "ico_setting", True).click()
        url = self._driver.execute_script("return document.URL")
        code = "clubid="
        club_id = url[url.index(code)+len(code):].split("&")[0]
        return club_id

    def get_driver(self):
        return self._driver

    def get_club_id(self):
        return self._club_id

    def current_url(self, url):
        """
        로그인세션을 유지한채 url 을 새탭에 하나씩 띄워서 조작할 수 있도록 한다.
        단, thread safe 하지 않으므로 주의하자.
        """
        if url not in self._windows_handle:
            self.get_driver().execute_script("window.open()")
            tab_id = self.get_driver().window_handles[-1]
            self.get_driver().switch_to.window(tab_id)
            self.get_driver().get(url)
            WebDriverWait(self.get_driver(), 10).until(EC.element_to_be_clickable((By.TAG_NAME, "BODY")))
            self._windows_handle[url] = tab_id
        else:
            self.get_driver().switch_to.window(self._windows_handle[url])

    def get_element(self, by, value, wait=False):
        """
        element 를 가져올때 wait 하는 로직을 넣어 sync 한 처리가 가능하도록 하자.
        """
        if not wait:
            if by == By.ID:
                return self._driver.find_element_by_id(value)
            if by == By.CSS_SELECTOR:
                return self._driver.find_element_by_css_selector(value)
            if by == By.CLASS_NAME:
                return self._driver.find_element_by_class_name(value)
            if by == By.LINK_TEXT:
                return self._driver.find_element_by_link_text(value)

        try:
            element = WebDriverWait(self._driver, 5).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            self._driver.quit()
        raise Exception("element error !")

    def close(self):
        if self._driver:
            self._driver.implicitly_wait(1)
            self._driver.close()
            self._driver = None
        return self._driver


class NCafeAutoJoin:
    def __init__(self, nCafeLogin: NCafeLogin):
        self._cafe = nCafeLogin
        self._change_level_user()
        self._change_wait_user()
        time.sleep(2)

    def _change_wait_user(self):
        url = "https://cafe.naver.com/ManageJoinApplication.nhn?search.clubid={}".format(self._cafe.get_club_id())
        self._cafe.current_url(url)
        return self._cafe

    def _change_level_user(self):
        url = "https://cafe.naver.com/ManageWholeMember.nhn?clubid={}".format(self._cafe.get_club_id())
        self._cafe.current_url(url)
        return self._cafe

    def get_wait_users(self):
        """
        가입대기중인 명단을 보여준다
        """
        accept = self._change_wait_user()
        table_body = accept.get_element(By.ID, "applymemberList", True)
        for row in table_body.find_elements_by_css_selector("tr"):
            if not ((row.get_attribute("id") or "").startswith("member")):
                continue
            nickname_id = row.find_element_by_css_selector("td:nth-child(2) > div > a").text.strip() \
                .replace("(", "").replace(")", "").split()
            age = row.find_element_by_css_selector("td:nth-child(3)").text.strip()
            gender = row.find_element_by_css_selector("td:nth-child(4)").text.strip()
            date = row.find_element_by_css_selector("td:nth-child(5)").text.strip()
            # reply load
            row.find_element_by_css_selector("td:nth-child(6) > a").click()
            reply = accept.get_element(By.CSS_SELECTOR,
                                       "#{}Answer>td > div > div > ol > li > p".format(nickname_id[1]), True).text
            yield CafeUser(id=nickname_id[1], nick=nickname_id[0], age=age, gender=gender, date=date, reply=reply)

    def get_guest_users(self, filter_level="손님"):
        """
        손님 등급 명단을 조회해준다
        """
        level_up = self._change_level_user()
        table_body = level_up.get_element(By.CSS_SELECTOR, "#_tableContent > table > tbody", True)
        for row in table_body.find_elements_by_css_selector("tr"):
            column = row.find_elements_by_css_selector("td")
            if column[3].text != filter_level:
                continue
            _nick_id = column[1].text.split()
            _id = _nick_id[1][1:len(_nick_id[1])-1]
            _nick = _nick_id[0]
            _age = "-"
            _gender = column[9].text
            _date = column[4].text.strip()
            _replay = "-"
            yield CafeUser(id=_id, nick=_nick, age=_age, gender=_gender, date=_date, reply=_replay)

    def _conform_wait_users(self, user_id_list=[]):
        _cafe = self._change_wait_user()
        if len(user_id_list) <= 0:
            raise RuntimeError("wait user is empty list.")
        for user_id in user_id_list:
            if not isinstance(user_id, str):
                raise RuntimeError("user_id is not string")
            el = _cafe.get_element(By.CSS_SELECTOR, "input[name='applyMemberCheck'][value='{}']".format(user_id), True)
            if not el:
                raise RuntimeError("Wait Users Element Find ERROR !!!")

            if not el.is_selected():
                el.click()
        action = _cafe.get_element(By.CSS_SELECTOR, "div.action_in")
        for btn in action.find_elements_by_css_selector("a.btn_type"):
            if btn.text.strip() == "가입승인":
                btn.click()
                try:
                    WebDriverWait(self._cafe.get_driver(), 5).until(EC.alert_is_present(), "선택한 신청자의 멤버가입을 승인하시겠습니까?")
                    self._cafe.get_driver().switch_to.alert.accept()
                    WebDriverWait(self._cafe.get_driver(), 5).until(EC.alert_is_present(), "가입처리가 완료되었습니다")
                    self._cafe.get_driver().switch_to.alert.accept()
                except TimeoutError:
                    raise RuntimeError("alert timeout error")
                return self
        raise Exception("wait user conform error !!!")

    def _conform_level_users(self, user_id_list=[], visible_text="일반 조합원"):
        for user_id in user_id_list:
            seed_url = "https://cafe.naver.com/ManageLevelUp.nhn?m=view&fromUpService=member" \
                       "&model.clubid={cludid}&model.memberid={id}"
            self._cafe.current_url(seed_url.format(**dict(cludid=self._cafe.get_club_id(), id=user_id)))
            level_up_select_box = Select(self._cafe.get_element(By.ID, "memberLevelSelect", True))
            level_up_select_box.select_by_visible_text(visible_text)
            self._cafe.get_element(By.ID, "comment").send_keys("{} 확인완료".format(visible_text))
            for btn in self._cafe.get_driver().find_elements_by_css_selector("#pop_footer>a"):
                if btn.text.strip() == "확인":
                    btn.click()
                    WebDriverWait(self._cafe.get_driver(), 5).until(EC.alert_is_present(), "등업신청")
                    alert = self._cafe.get_driver().switch_to.alert
                    alert.accept()
                    break

    def close(self):
        self._cafe.close()