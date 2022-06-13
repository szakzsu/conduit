from Conduit_vizsgaremek import login_details
from Conduit_vizsgaremek.login_details import login_user


def cookie_accept(browser):
    cookies = browser.find_element_by_xpath(
        '//button[@class="cookie__bar__buttons__button cookie__bar__buttons__button--accept"]')
    cookies.click()


def login(browser):
    sign_in = browser.find_element_by_xpath('//a[@href="#/login"]')
    sign_in.click()
    email = browser.find_element_by_xpath('//input[@placeholder="Email"]')
    email.send_keys(login_user['email'])
    password = browser.find_element_by_xpath('//input[@placeholder="Password"]')
    password.send_keys(login_user['password'])
    sign_in_btn = browser.find_element_by_xpath('//button[@class="btn btn-lg btn-primary pull-xs-right"]')
    sign_in_btn.click()