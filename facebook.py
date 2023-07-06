import bs4
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

import json
import logging
import traceback
import time

GM_WEBPAGE = 'https://www.facebook.com/'
MAX_WAIT = 10
MAX_SCROLLS = 40


class FacebookScraper:
    def __init__(self, debug=True):
        self.debug = debug
        self.driver = self.__get_driver()
        self.logger = self.__get_logger()
        self.action = ActionChains(self.driver)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)

        self.driver.close()
        self.driver.quit()
        return True

    def __click(self, element):
        self.action.move_to_element(element).click().perform()
        time.sleep(1)

    def __get_driver(self):
        options = Options()

        if not self.debug:
            options.add_argument("--headless")
        else:
            options.add_argument("--window-size=1450,920")

        options.add_argument("--disable-notifications")
        options.add_argument("--accept-lang=zh-TW")
        input_driver = webdriver.Chrome(options=options)
        input_driver.get(GM_WEBPAGE)

        return input_driver

    def __get_logger(self):
        # create logger
        logger = logging.getLogger('facebook-scraper')
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        fh = logging.FileHandler('fb-scraper.log')
        fh.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # add formatter to ch
        fh.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(fh)

        return logger

    def __scroll(self):
        scroll_count = 0
        while scroll_count < MAX_SCROLLS:
            previous_height = self.driver.execute_script("return document.body.scrollHeight;")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            current_height = self.driver.execute_script("return document.body.scrollHeight;")

            if current_height == previous_height:
                break

    def __get_and_filter_element_by_xpath(self, contains: str, value: dict) -> list:
        rules = []
        for k, v in value.items():
            rules.append(f'@{k}="{v}"')
        non_filter = self.driver.find_elements(by=By.XPATH, value=f'//div[{"and".join(rules)}]')
        try:
            return list(filter(lambda x: contains in x.text, non_filter))
        except Exception as e:
            self.logger.warning(e)
            return []

    def __expand_reviews(self):
        unexpanded = self.__get_and_filter_element_by_xpath("則留言", {"aria-expanded": "false"})
        for u in unexpanded:
            self.__click(u)

        about = self.__get_and_filter_element_by_xpath("最相關", {"role": "button", "tabindex": 0})
        for a in about:
            self.__click(a)
            tabs = self.__get_and_filter_element_by_xpath("所有留言", {"role": "menuitem"})
            for t in tabs:
                self.__click(t)
                break

        history = self.__get_and_filter_element_by_xpath("查看", {"role": "button", "tabindex": 0})
        for h in history:
            self.__click(h)

        reply = self.__get_and_filter_element_by_xpath("檢視", {"role": "button", "tabindex": 0})
        for r in reply:
            self.__click(r)

    def __parse(self, review: bs4.Tag):
        data = {}

        if "推薦了" in str(review):
            data["recommend"] = "推薦了"
        elif "不推薦" in str(review):
            data["recommend"] = "不推薦"
        else:
            data["recommend"] = "無評價"

        span_elements = review.find_all('span', {'class': "xt0psk2"})
        try:
            data["commenter"] = span_elements[1].text
            data["fan_page"] = span_elements[2].text
        except Exception as e:
            logging.debug(e)
            data["commenter"] = ""
            data["fan_page"] = ""

        div_elements = review.select('div[dir="auto"][style="text-align:start"]')
        data["comment"] = "" if not div_elements else div_elements[0].text

        div_elements = review.select('div[dir="auto"][style="text-align: start;"]')
        replies = {}
        for k, v in enumerate(div_elements):
            replies[k] = v.text
        data["replies"] = json.dumps(replies, ensure_ascii=False)
        return data

    def login(self, email, password):
        email_input = self.driver.find_element(by=By.ID, value="email")
        email_input.send_keys(email)

        password_input = self.driver.find_element(by=By.ID, value="pass")
        password_input.send_keys(password)

        recent_rating_bt = self.driver.find_element(by=By.NAME, value="login")
        self.__click(recent_rating_bt)

        return 0

    def get_reviews(self, url):
        self.driver.get(url)

        self.__scroll()
        self.__expand_reviews()

        response = BeautifulSoup(self.driver.page_source, 'html.parser')
        blocks = response.find_all('div', class_='x1n2onr6 x1ja2u2z')

        parsed_reviews = []
        for index, review in enumerate(blocks):
            print(f"processing in comment {index}")
            self.logger.info(f"processing in comment {index}")
            r = self.__parse(review)
            parsed_reviews.append(r)
        return parsed_reviews
