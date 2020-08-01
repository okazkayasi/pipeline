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
    time.sleep(5)

    reachable = br.find_element(By.CLASS_NAME, "search-results__list")\
        .find_elements_by_xpath("//span[text()='Status is reachable']")
    online = br.find_element(By.CLASS_NAME, "search-results__list")\
        .find_elements_by_xpath("//span[text()='Status is online']")
    offline = br.find_element(By.CLASS_NAME, "search-results__list")\
        .find_elements_by_xpath("//span[text()='Status is offline']")

    ghost = br.find_elements_by_class_name('ivm-view-attr__ghost-entity')

    the_dict = {}

    reachable_count = len(reachable)
    online_count = len(online)
    offline_count = len(offline)
    total_count = reachable_count + online_count + offline_count

    online_list, reachable_list, offline_list = [], [], []
    for person in online:
        name = (person.find_element_by_xpath('../../../../../../../..')
                .find_element(By.CLASS_NAME, "search-result__info")
                .find_element(By.CLASS_NAME, "actor-name").text)
        online_list.append(name)

    if len(online_list) > 0:
        del online_list[-1]

    for person in reachable:
        name = (person.find_element_by_xpath('../../../../../../../..')
                .find_element(By.CLASS_NAME, "search-result__info")
                .find_element(By.CLASS_NAME, "actor-name").text)
        reachable_list.append(name)

    for person in offline:
        name = (person.find_element_by_xpath('../../../../../../../..')
                .find_element(By.CLASS_NAME, "search-result__info")
                .find_element(By.CLASS_NAME, "actor-name").text)
        offline_list.append(name)

    for person in ghost:
        name = (person.find_element_by_xpath('../../../../../../..')
                .find_element(By.CLASS_NAME, "search-result__info")
                .find_element(By.CLASS_NAME, "actor-name").text)
        offline_list.append(name)
    return online_list, reachable_list, offline_list


def go_next_page(br):
    if not br.find_element_by_class_name('artdeco-pagination__button--next').is_enabled():
        print('disabledd')
        return False
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

    online = 0
    reach = 0
    everyone = 0
    check_people = ['asd']
    active = True
    page = 1

    on_list = ['online:']
    reach_list = ['reachable:']
    off_list = ['offline:']

    while True:
        go_down(br)
        online_list, reachable_list, offline_list = get_active_names(
            br)
        print(online_list)
        print(reachable_list)
        print(offline_list)

        on_list.extend(online_list)
        reach_list.extend(reachable_list)
        off_list.extend(offline_list)

        everyone += len(online_list) + len(reachable_list) + len(offline_list)
        online += len(online_list)
        reach += len(reachable_list)

        # go to next page
        print('all:{} online: {} and reachable {} at page {}'.format(
            everyone, online, reach, page))
        if not go_next_page(br):
            break

        page += 1

    now = datetime.datetime.now()
    days = ["Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"]
    intDay = datetime.datetime.today().weekday()
    day = days[intDay]
    todayDate = datetime.datetime.today().strftime('%Y-%m-%d')
    dayTime = datetime.datetime.today().strftime('%H:%M')

    f1 = ['Date', 'Day', 'Time', 'Total Count',
          'Online Count', 'Reachable Count', 'Last Page']
    fields = [todayDate, day, dayTime, everyone, online, reach, page]

    with open('names.csv', 'a', newline='\n', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(f1)
        writer.writerow(fields)
        writer.writerow(on_list)
        writer.writerow(reach_list)
        writer.writerow(off_list)

    config = configparser.ConfigParser()
    config.read('file.ini')
    sleep_time = int(config.get('auth', 'sleep_minutes'))
    print('sleep for {} minutes'.format(sleep_time))
    time.sleep(sleep_time*60)


if __name__ == "__main__":
    br = open_browser(True)
    run_time = 0
    while True:
        try:
            fun(br)
        except Exception as e:
            print(e)
        run_time += 1
