import csv
import time
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from basic_definitions import cookie_accept, login
from login_details import register_user, login_user


class TestConduit(object):
    def setup(self):
        browser_options = Options()
        browser_options.headless = True
        self.browser = webdriver.Chrome(ChromeDriverManager().install(), options=browser_options)
        self.browser.implicitly_wait(10)
        URL = 'http://localhost:1667/#/'
        self.browser.get(URL)
        self.browser.maximize_window()

    # TC01: Checking if the cookie's pop up window has closed after accepting the cookies
    def test_accept_the_cookies(self):
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//div[@class="cookie cookie__bar cookie__bar--bottom-left"]')))
        accept_cookies = self.browser.find_element_by_xpath(
            '//button[@class="cookie__bar__buttons__button cookie__bar__buttons__button--accept"]')
        accept_cookies.click()

        try:
            cookie_window = self.browser.find_elements_by_xpath(
                '//div[@class="cookie cookie__bar cookie__bar--bottom-left"]')
            assert len(cookie_window) == 0
            print('You have accepted the cookies!')
        except AssertionError:
            print('An error occurred when accepting the cookies!')

    # TC2a: Registration with no user data, so testcase is expected to fail
    def test_no_data_registration(self):
        cookie_accept(self.browser)
        registration = self.browser.find_element_by_xpath('//a[@href="#/register"]')
        registration.click()
        username = self.browser.find_element_by_xpath('//input[@placeholder="Username"]')
        username.send_keys("")
        user_email = self.browser.find_element_by_xpath('//input[@placeholder="Email"]')
        user_email.send_keys("")
        user_password = self.browser.find_element_by_xpath('//input[@placeholder="Password"]')
        user_password.send_keys("")
        sign_up_btn = self.browser.find_element_by_xpath('//button[@class="btn btn-lg btn-primary pull-xs-right"]')
        sign_up_btn.click()

        registration_error = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.XPATH, '//div[text()="Username field required. "]')))

        assert registration_error.is_displayed()
        print('An error occurred during the registration process')

        error_btn = self.browser.find_element_by_xpath('//button[@class="swal-button swal-button--confirm"]')
        error_btn.click()

    # TC02b: Registration with valid details, because a registered account will be necessary for further tests
    def test_valid_user_registration(self):
        cookie_accept(self.browser)
        registration = self.browser.find_element_by_xpath('//a[@href="#/register"]')
        registration.click()
        username = self.browser.find_element_by_xpath('//input[@placeholder="Username"]')
        username.send_keys(register_user['Username'])
        user_email = self.browser.find_element_by_xpath('//input[@placeholder="Email"]')
        user_email.send_keys(register_user['Email'])
        user_password = self.browser.find_element_by_xpath('//input[@placeholder="Password"]')
        user_password.send_keys(register_user['Password'])
        sign_up_btn = self.browser.find_element_by_xpath('//button[@class="btn btn-lg btn-primary pull-xs-right"]')
        sign_up_btn.click()
        time.sleep(2)
        message = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="swal-text"]'))).text
        try:
            if message == 'Your registration was successful!':
                print("You have registered successfuly!")
            elif message == 'Email already taken.':
                print("This email address is already in use")
        except AssertionError:
            print("An error occurred during registration")

    # TC3: Logging in as registered user, and confirming that the user is logged in
    def test_login_as_registered_user(self):
        cookie_accept(self.browser)
        sign_in = self.browser.find_element_by_xpath('//a[@href="#/login"]')
        sign_in.click()
        email = self.browser.find_element_by_xpath('//input[@placeholder="Email"]')
        email.send_keys(login_user['email'])
        password = self.browser.find_element_by_xpath('//input[@placeholder="Password"]')
        password.send_keys(login_user['password'])
        sign_in_btn = self.browser.find_element_by_xpath('//button[@class="btn btn-lg btn-primary pull-xs-right"]')
        sign_in_btn.click()
        profile_btn = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@href="#/@szakzsu/" and @class="nav-link"]')))

        try:
            assert profile_btn.text == 'szakzsu'
            print("Logged in successfully.")
        except TimeoutException:
            print("An error occurred during the login process")

    # TC4: Listing the article(s) with a "laoreet" tag
    def test_listing_the_article(self):
        cookie_accept(self.browser)
        login(self.browser)
        laoreet_tag = self.browser.find_element_by_xpath(
            '//div[@class="sidebar"]/div[@class="tag-list"]/a[text()="laoreet"]')
        laoreet_tag.click()

        time.sleep(2)

        listed_articles = self.browser.find_elements_by_tag_name('h1')
        articles_with_laoreet_tag = self.browser.find_elements_by_xpath(
            '//div[@class="article-preview"]//a[@href="#/tag/laoreet"]')

        try:
            # -1 because the conduit logo is also a h1 element
            assert len(listed_articles) - 1 == len(articles_with_laoreet_tag)
            print("Only articles with \"laoreet\" tags were listed!")
        except AssertionError:
            print("No articles found!")

    # TC05: Browsing several pages of articles
    def test_browsing_the_pages(self):
        cookie_accept(self.browser)
        login(self.browser)
        page_links = WebDriverWait(self.browser, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//a[@class="page-link"]')))
        time.sleep(1)
        for page_link in page_links:
            page_link.click()
            time.sleep(2)
        active_page = self.browser.find_element_by_xpath('//li[@class="page-item active"]')
        try:
            assert page_link.text == active_page.text
            print("Pagination is correct")
        except AssertionError:
            print("Pagination is not matching!")

    # TC06: Commenting on an existing article
    def test_posting_a_comment(self):
        cookie_accept(self.browser)
        login(self.browser)
        first_article = self.browser.find_element_by_xpath('//a[@href="#/articles/lorem-ipsum-dolor-sit-amet"]')
        first_article.click()
        time.sleep(2)
        comment_field = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//textarea[@placeholder="Write a comment..."]')))
        comment_field.send_keys("This is a great article :)")

        post_comment_btn = self.browser.find_element_by_xpath('//button[text()="Post Comment"]')
        post_comment_btn.click()

        comment_author = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@href="#/@szakzsu/"]')))

        try:
            assert comment_author.text == "szakzsu"
            print("Your comment has been posted successfully!")
        except AssertionError:
            print("An error occurred during the process!")

    # TC07: New data input from file, publishing an article
    def test_data_input_from_file(self):
        cookie_accept(self.browser)
        login(self.browser)
        new_article_tab = self.browser.find_element_by_xpath('//a[@href="#/editor"]')
        new_article_tab.click()
        article_title = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//fieldset/input[@class="form-control form-control-lg"]')))
        article_about = self.browser.find_element_by_xpath('//input[starts-with(@placeholder,"What")]')
        article_content = self.browser.find_element_by_xpath('//textarea')
        article_tags = self.browser.find_element_by_xpath('//input[@placeholder="Enter tags"]')
        submit_btn = self.browser.find_element_by_xpath('//button[@type="submit"]')
        counter = 0
        with open('test_article.csv', 'r', encoding='UTF-8') as article:
            file_content = csv.reader(article, delimiter=';')
            while counter != 3:
                for row in file_content:
                    article_title.send_keys(row[0])
                    article_about.send_keys(row[1])
                    article_content.send_keys(row[2])
                    article_tags.send_keys(row[3])
                    submit_btn.click()
                    time.sleep(2)
                    new_article_tab.click()
                    counter += 1
                    time.sleep(2)

        logged_in_account = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@href="#/@szakzsu/"]')))
        home_btn = self.browser.find_element_by_xpath('//a[@class="nav-link router-link-exact-active active"]')
        home_btn.click()
        logged_in_account.click()

        time.sleep(2)
        published_article = self.browser.find_elements_by_xpath('//div[@class="article-preview"]')

        try:
            assert len(published_article) == counter
            print('Your articles have been published successfully!')
        except AssertionError:
            print('An error occurred during publication')

    # TC08: Modification of existing article
    def test_modifying_existing_article(self):
        cookie_accept(self.browser)
        login(self.browser)
        logged_in_account = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@href="#/@szakzsu/"]')))
        home_btn = self.browser.find_element_by_xpath('//a[@class="nav-link router-link-exact-active active"]')
        home_btn.click()
        logged_in_account.click()
        time.sleep(2)
        edit_article = self.browser.find_element_by_xpath('//a[@href="#/articles/how-to-reverse-a-list-in-python"]')
        edit_article.click()
        edit_btn = self.browser.find_element_by_xpath('//a[@href="#/editor/how-to-reverse-a-list-in-python"]')
        edit_btn.click()
        body_modify = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//fieldset/textarea[@class="form-control"]')))
        body_modify.clear()
        body_modify.send_keys("I\'ve changed my mind, and I will write something else here soon...")
        article_tags = self.browser.find_element_by_xpath('//input[@placeholder="Enter tags"]')
        article_tags.send_keys("updated content")
        submit_btn = self.browser.find_element_by_xpath('//button[@type="submit"]')
        submit_btn.click()

        time.sleep(2)

        tag_list = self.browser.find_elements_by_xpath('//div/a[@class="tag-pill tag-default"]')
        try:
            assert tag_list[1].text == "updated content"
            print("Update successful")
        except AssertionError:
            print("Your article could not be updated")

    # TC09: Deleting the created article
    def test_deleting_an_article(self):
        cookie_accept(self.browser)
        login(self.browser)
        logged_in_account = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@href="#/@szakzsu/"]')))
        home_btn = self.browser.find_element_by_xpath('//a[@class="nav-link router-link-exact-active active"]')
        home_btn.click()
        logged_in_account.click()
        time.sleep(2)
        edit_article = self.browser.find_element_by_xpath('//a[@href="#/articles/how-to-reverse-a-list-in-python"]')
        edit_article.click()
        delete_btn = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[@class="btn btn-outline-danger btn-sm"]')))
        delete_btn.click()

        time.sleep(2)

        try:
            assert self.browser.current_url == "http://localhost:1667/#/"
            print("Article deleted successfully!")
        except AssertionError:
            print("Article not deleted!")

    # TC10: Downloading data to file, downloading article titles
    def test_downloading_data_to_file(self):
        cookie_accept(self.browser)
        login(self.browser)
        popular_tags = self.browser.find_elements_by_xpath('//a[@class="tag-pill tag-default"]')
        with open('popular_tags.txt', 'w') as f:
            for tag in popular_tags:
                f.write(tag.text + ', ')

        try:
            with open('popular_tags.txt', 'r') as f:
                read_tags = f.read().split(', ')
                for i, tag in enumerate(popular_tags):
                    assert tag.text == read_tags[i]
            print("Downloading the data was successful!")
        except AssertionError:
            print("Something went wrong!")

    # TC11: Logging out of the Conduit application
    def test_logout(self):
        cookie_accept(self.browser)
        login(self.browser)
        time.sleep(2)
        logout_btn = self.browser.find_element_by_xpath('//a[@active-class="active"]')
        logout_btn.click()
        login_btn = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@href="#/login"]')))
        try:
            assert login_btn.is_displayed()
            print("You have logged out successfully!")
        except AssertionError:
            print("An error occurred during the logout process.")

    def teardown(self):
        self.browser.quit()
