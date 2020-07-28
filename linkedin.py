import datetime
import pickle
import datetime
import time
import configparser

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import csv


def open_browser(visible=False):

    config = configparser.ConfigParser()
    config.read('file.ini')
    user = config.get('auth', 'username')
    pw = config.get('auth', 'password')

    option = webdriver.ChromeOptions()
    # option.add_argument("user-data-dir=C:/Users/okazkayasi/AppData/Local/Google/Chrome/User Data/") #Path to your chrome profile
    option.add_argument("--start-maximized")
    if not visible:
        option.add_argument("--headless")

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
    time.sleep(2)

    pip = br.find_element(By.CLASS_NAME, "search-results__list")\
        .find_elements_by_xpath("//span[text()='Status is reachable']")
    people = br.find_element(By.CLASS_NAME, "search-results__list")\
        .find_elements_by_xpath("//span[text()='Status is online']")
    del people[-1]
    online = len(people)
    reach = len(pip)
    people.extend(pip)
    names = []
    for p in people:
        try:
            name = (p.find_element_by_xpath('../../../../../../../..')
                .find_element(By.CLASS_NAME, "search-result__info")
                .find_element(By.CLASS_NAME, "actor-name").text)
            names.append(name)
        except Exception as e:
            print(e)
            time.sleep(5)
            return get_active_names(br)
    return names, online, reach


def go_next_page(br):


    br.find_element_by_class_name('artdeco-pagination__button--next').click()
    time.sleep(4)
    return True


def go_down(br, n=1):
    html = br.find_element_by_tag_name('html')
    if n == 1:
        html.send_keys(Keys.END)
    elif n == -1:
        html.send_keys(Keys.HOME)



def fun(br):

    time.sleep(3)
    br.get('https://www.linkedin.com/search/results/people/?facetNetwork=%5B%22F%22%5D&origin=MEMBER_PROFILE_CANNED_SEARCH')
    time.sleep(3)
    try:
        if len(br.find_elements_by_class_name('msg-overlay-list-bubble--is-minimized')) == 0:
            br.find_element_by_class_name('msg-overlay-bubble-header').click()
    except:
        print('no message box')

    all_people = []
    online = 0
    reach = 0
    check_people = ['asd']
    active = True
    page = 1
    while True:
        go_down(br)
        page_people, page_online, page_reach = get_active_names(br)
        print(page_people)
        
        online += page_online
        reach += page_reach

        if page_people == check_people:
            break

        # go to next page           
        all_people.extend(page_people)
        print('online: {} and reachable {} at page {}'.format(online, reach, page))
        page += 1
        check_people = page_people
        go_next_page(br)


    fields = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        online, reach]
    fields.extend(all_people)
    
    with open('names.csv', 'a', newline='\n', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(fields)

    config = configparser.ConfigParser()
    config.read('file.ini')
    sleep_time = int(config.get('auth', 'sleep_minutes'))
    print('sleep for {} minutes'.format(sleep_time))
    time.sleep(sleep_time*60)


if __name__ == "__main__":
    br = open_browser()
    run_time = 0
    while True:
        try:
            fun(br)
        except Exception as e:
            if run_time == 0:  # means it didn't work even one time.
                br = open_browser(visible=True)
                try:
                    fun(br)
                except Exception as e:
                    print('You have 3 minutes to solve the puzzle', e)
                    time.sleep(180)
        run_time += 1
