import time
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

browser = webdriver.Chrome(ChromeDriverManager().install())
URL = 'http://localhost:1667/#/'
browser.get(URL)
browser.maximize_window()


def accept_the_cookies():
    WebDriverWait(browser, 5).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[@class="cookie cookie__bar cookie__bar--bottom-left"]')))
    accept_cookies = browser.find_element_by_xpath(
        '//button[@class="cookie__bar__buttons__button cookie__bar__buttons__button--accept"]')
    accept_cookies.click()


def teardown():
    browser.quit()


# TC01: Checking if the cookie's pop up window has closed after accepting the cookies
accept_the_cookies()

try:
    cookie_window = browser.find_elements_by_xpath('//div[@class="cookie cookie__bar cookie__bar--bottom-left"]')
    assert len(cookie_window) == 0
    print('You have accepted the cookies!')
except AssertionError:
    print('An error occurred when accepting the cookies!')

# TC2: Registration with no user data, so testcase is expected to fail

registration = browser.find_element_by_xpath('//a[@href="#/register"]')
registration.click()
username = browser.find_element_by_xpath('//input[@placeholder="Username"]')
username.send_keys("")
email = browser.find_element_by_xpath('//input[@placeholder="Email"]')
email.send_keys("")
password = browser.find_element_by_xpath('//input[@placeholder="Password"]')
password.send_keys("")
sign_up_btn = browser.find_element_by_xpath('//button[@class="btn btn-lg btn-primary pull-xs-right"]')
sign_up_btn.click()

registration_error = WebDriverWait(browser, 5).until(
    EC.presence_of_element_located((By.XPATH, '//div[text()="Username field required. "]')))

assert registration_error.is_displayed()
print('An error occurred during the registration process')

error_btn = browser.find_element_by_xpath('//button[@class="swal-button swal-button--confirm"]')
error_btn.click()

# TC3: Logging in as registered user, and confirming that the user is logged in
sign_in = browser.find_element_by_xpath('//a[@href="#/login"]')
sign_in.click()
email = browser.find_element_by_xpath('//input[@placeholder="Email"]')
email.send_keys("gosh.zsu@gmail.com")
password = browser.find_element_by_xpath('//input[@placeholder="Password"]')
password.send_keys("Szakzsu01!")
sign_in_btn = browser.find_element_by_xpath('//button[@class="btn btn-lg btn-primary pull-xs-right"]')
sign_in_btn.click()
profile_btn = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.XPATH, '//a[@href="#/@szakzsu/" and @class="nav-link"]')))
try:
    assert profile_btn.text == 'szakzsu'
    print("Logged in successfully.")
except TimeoutException:
    print("An error occurred during the login process")

# TC4: Listing the article(s) with a "laoreet" tag
laoreet_tag = browser.find_element_by_xpath(
    '//div[@class="sidebar"]/div[@class="tag-list"]/a[text()="laoreet"]')
laoreet_tag.click()

time.sleep(1)
article_list = browser.find_elements_by_xpath('//a[@class="preview-link"]/h1')
try:
    assert len(article_list) != 0
    print("I have found the desired article!")
except AssertionError:
    print("No articles found!")

# TC05: Browsing several pages of articles
home = browser.find_element_by_xpath('//a[@href="#/"]')
home.click()
page_links = WebDriverWait(browser, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, '//a[@class="page-link"]')))
time.sleep(1)
for page_link in page_links:
    page_link.click()
    time.sleep(2)
active_page = browser.find_element_by_xpath('//li[@class="page-item active"]')
try:
    assert page_link.text == active_page.text
    print("Pagination is correct")
except AssertionError:
    print("Pagination is not matching!")

# TC06: Commenting on an existing article
home_btn = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.XPATH, '//a[@class="nav-link router-link-exact-active active"]')))
home_btn.click()

first_article = browser.find_elements_by_xpath('//div[@class="article-preview"]')[0]
first_article.click()
comment_field = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.XPATH, '//textarea[@placeholder="Write a comment..."]')))
comment_field.send_keys("This is a great article :)")

post_comment_btn = browser.find_element_by_xpath('//button[text()="Post Comment"]')
post_comment_btn.click()

comment_author = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.XPATH, '//a[@href="#/@szakzsu/"]')))

try:
    assert comment_author.text == "szakzsu"
    print("Your comment has been posted successfully!")
except AssertionError:
    print("An error occurred during the process!")


# TC07: New data input from file, publishing an article
new_article_tab = browser.find_element_by_xpath('//a[@href="#/editor"]')
new_article_tab.click()
article_title = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.XPATH, '//fieldset/input[@class="form-control form-control-lg"]')))
article_about = browser.find_element_by_xpath('//input[starts-with(@placeholder,"What")]')
article_content = browser.find_element_by_xpath('//textarea')
article_tags = browser.find_element_by_xpath('//input[@placeholder="Enter tags"]')
submit_btn = browser.find_element_by_xpath('//button[@type="submit"]')
with open('test_article.txt', 'r', encoding='UTF-8') as article:
    file_content = article.readlines()
article_title.send_keys(file_content[0].rstrip())
article_about.send_keys(file_content[1].rstrip())
article_content.send_keys(file_content[2].rstrip())
article_tags.send_keys(file_content[3])
article_tags.send_keys(file_content[4])
submit_btn.click()
time.sleep(2)

published_title = browser.find_element_by_css_selector('h1')

try:
    assert published_title.text == file_content[0].rstrip()
    print('Your article has been published successfully!')
except AssertionError:
    print('An error occurred during publication')

# TC08: Modification of existing article
edit_btn = browser.find_element_by_xpath('//a[@href="#/editor/how-to-reverse-a-list-in-python"]')
edit_btn.click()
body_modify = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.XPATH, '//fieldset/textarea[@class="form-control"]')))
body_modify.clear()
body_modify.send_keys("I\'ve changed my mind, and I will write something else here soon...")
article_tags.send_keys("updated content")
submit_btn.click()

time.sleep(2)

tag_list = browser.find_elements_by_xpath('//div/a[@class="tag-pill tag-default"]')
try:
    assert tag_list[2].text == "updated content"
    print("Update successful")
except AssertionError:
    print("Your article could not be updated")

# TC09: Deleting the created article
delete_btn = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.XPATH, '//button[@class="btn btn-outline-danger btn-sm"]')))
delete_btn.click()

time.sleep(2)

try:
    assert browser.current_url == "http://localhost:1667/#/"
    print("Article deleted successfully!")
except AssertionError:
    print("Article not deleted!")

# TC10: Downloading data to file, downloading article titles
popular_tags = browser.find_elements_by_xpath('//a[@class="tag-pill tag-default"]')
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
logout_btn = browser.find_element_by_xpath('//a[@active-class="active"]')
logout_btn.click()
login_btn = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.XPATH, '//a[@href="#/login"]')))
try:
    assert login_btn.is_displayed()
    print("You have logged out successfully!")
except AssertionError:
    print("An error occurred during the logout process.")

teardown()
