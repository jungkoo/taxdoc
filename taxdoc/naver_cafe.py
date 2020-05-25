#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import namedtuple
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

    def get(self, url):
        self._driver.get(url)

    def get_driver(self):
        return self._driver

    def get_club_id(self):
        return self._club_id

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


class NCafeAutoJoin:
    def __init__(self, user_name, user_password, driver_path, cafe_url="https://cafe.naver.com/nunion", ):
        self._accept = NCafeLogin(driver_path=driver_path, cafe_url=cafe_url)\
            .login(user_name=user_name, user_password=user_password)
        self._join = NCafeLogin(driver_path=driver_path, cafe_url=cafe_url)\
            .login(user_name=user_name, user_password=user_password)

    def find_wait_users(self):
        """
        유저정보 & 체크박스 컨트롤 가능한 객체 리턴
        """
        def _extract_wait_users():
            """
                가입승인대기유저 목록 로딩한다
            """
            accept = self._accept
            accept.get("https://cafe.naver.com/ManageJoinApplication.nhn?search.clubid={}".format(accept.get_club_id()))
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
        for user in _extract_wait_users():
            yield CafeUserCheckBox(user, self._accept, self._join)

    def close(self):
        self._accept.close()
        self._join.close()


class CafeUserCheckBox:
    """
    가입승인을 해준다
    """
    def __init__(self, init_user: CafeUser, accept: NCafeLogin, level_up: NCafeLogin):
        self._cafe_accept = accept
        self._level_up = level_up
        self._value = init_user
        self._id = init_user.id
        el = self._cafe_accept.get_element(By.CSS_SELECTOR, "input[name='applyMemberCheck'][value='{}']".format(self._id))
        self._checked = el.is_selected()
        self.element = el

    def set(self, value: CafeUser):
        self._value = value

    def get(self):
        return self._value

    def is_checked(self):
        return self._checked

    def checked(self):
        if not self.is_checked():
            self.element.click()
            self._save_for_accept()
            self._checked = True

    def level(self, visible_text):
        level_up = self._level_up
        seed_url = "https://cafe.naver.com/ManageLevelUp.nhn?m=view&fromUpService=member" \
                   "&model.clubid={cludid}&model.memberid={id}"
        level_up.get(seed_url.format(**dict(cludid=level_up.get_club_id(), memberid=self._id)))
        level_up_select_box = Select(self._driver.find_element_by_id('memberLevelSelect'))
        level_up_select_box.select_by_visible_text(visible_text)
        level_up.get_element(By.ID, "comment").send_keys("{} 확인완료".format(visible_text))
        for btn in self._driver.find_elements_by_css_selector("#pop_footer>a"):
            if btn.text.strip == "확인":
                btn.click()
                time.sleep(1)
                return True
        return False

    def _save_for_accept(self):
        """
        승인신청
        """
        action = self._cafe_accept.get_element(By.CSS_SELECTOR, "div.action_in")
        for btn in action.find_elements_by_css_selector("a.btn_type"):
            if btn.text.strip() == "가입승인":
                btn.click()
                time.sleep(1)
                alert = self._cafe_accept.get_driver().switch_to.alert
                alert.accept()
                time.sleep(1)
                return True
        raise Exception("가입승인 실패 : ".format(self._value))

    def __str__(self):
        return"[{}] {}".format("O" if self.is_checked() else "X", self._value)