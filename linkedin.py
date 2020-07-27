import datetime
import pickle
import datetime
import time
import configparser

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import csv


def open_browser():

    config = configparser.ConfigParser()
    config.read('file.ini')
    user = config.get('auth', 'username')
    pw = config.get('auth', 'password')

    option = webdriver.ChromeOptions()
    option.add_argument("--start-maximized")

#     option.add_argument("--incognito")
    # option.add_argument("--headless")
    browser = webdriver.Chrome(executable_path='./chromedriver',
                               options=option)

    url = 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
    browser.get(url)
    browser.find_element_by_id('username').send_keys(user)
    browser.find_element_by_id('password').send_keys(pw)
    browser.find_element_by_xpath(
        "//button[normalize-space()='Sign in']").click()

    return browser


def get_active_names(br):
    people = br.find_element(By.CLASS_NAME, "search-results__list")\
        .find_elements_by_class_name('presence-indicator--is-reachable')
    names = []
    for p in people:
        name = (p.find_element_by_xpath('../../../../../../..')
                .find_element(By.CLASS_NAME, "search-result__info")
                .find_element(By.CLASS_NAME, "actor-name").text)
        names.append(name)
    return names


def go_next_page(br):
    time.sleep(1)
    active = br.find_element_by_class_name(
        'artdeco-pagination__button--next').is_enabled()
    if not active:
        return False
    br.find_element_by_class_name('artdeco-pagination__button--next').click()
    time.sleep(1)
    return True


def go_down(br, n=1):
    html = br.find_element_by_tag_name('html')
    if n == 1:
        html.send_keys(Keys.END)
    elif n == -1:
        html.send_keys(Keys.HOME)


if __name__ == "__main__":
    br = open_browser()
    time.sleep(3)
    br.get('https://www.linkedin.com/search/results/people/?facetNetwork=%5B%22F%22%5D&origin=MEMBER_PROFILE_CANNED_SEARCH')
    all_people = []

    active = True
    while True:
        all_people.extend(get_active_names(br))
        print(len(all_people))
        go_down(br)
        if not go_next_page(br):
            break

    fields = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
           len(all_people)]
    fields.extend(all_people)
    
    with open('names.csv', 'a', newline='\n') as f:
        writer = csv.writer(f)
        writer.writerow(fields)

    br.close()