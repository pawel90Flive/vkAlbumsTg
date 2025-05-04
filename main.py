import requests as req
from requests.exceptions import ConnectTimeout

import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


def save(src, fname='page.html'):
    method = 'w' if isinstance(src, str) else 'wb'
    with open(fname, method) as file:
        file.write(src) 

def get_available(community_name, exist):
    if not exist:
        return

    albs = os.listdir(community_name)
    
    albs_photos_count = {}
    for alb in albs:
       albs_photos_count[alb] = len(os.listdir(f'{community_name}/{alb}')) 
    #print(albs_photos_count)
    
    return albs_photos_count 


def get_needed(albs_photos_count, albs):
    aal = albs_photos_count.keys()
    
    needed = {}
    for alb in albs:
        if alb in aal:
            if not albs_photos_count[alb] ==\
                    int(alb[alb.rfind('_')+1:]):
                needed[alb] = albs_photos_count[alb]
        else:
            needed[alb] = 0 
    return needed


    
def req_get(url):
    while True:
        try:
            resp = req.get(url)
            return resp
            break
        except(ConnectTimeout):
            print('req is fail, trying again...')

def make_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    return driver

def get_albums():
    url = 'url with m'
    driver = make_driver()
    print(f'getting {url}')
    driver.get(url)
    save(driver.page_source, 'alb.html')

    albs_count= try_except(NoSuchElementException,
                      'albs_count get is fail...',
                      driver.find_element,
                      By.CSS_SELECTOR,
                      'span[class="Pad__count"]')
    albs_count = int(albs_count.get_attribute('innerHTML'))
    driver.get(f'{url}?act=all')
    albs = try_except(NoSuchElementException,
                      'albs get is fail...',
                      driver.find_elements,
                      By.CLASS_NAME, 'AlbumItem')
    title = driver.find_element(By.TAG_NAME, 'title').get_attribute('innerHTML')
    community_name = title[:title.find('\'s albu')]
    print(f'{title} | {community_name} started to scraping a {albs_count} albums')
    try:
        os.mkdir(community_name)
    except(FileExistsError):
        print('community name directory exist')


    available = get_available(community_name, 1)
    l1 = len(albs)
    while len(albs) < albs_count:
        driver.execute_script("arguments[0].scrollIntoView();", albs[-1])   
        sleep(1) 
        albs = try_except(NoSuchElementException,
                          'albs get is fail...',
                          driver.find_elements,
                          By.CLASS_NAME, 'AlbumItem')
        l2 = len(albs)
        print(f'{l2}/{albs_count}', end='\r')
        if l1 == l2:
            driver.execute_script('document.querySelector(".Popup").remove()')
        else:
            l1 = l2
    
    albs_data = []
    print('albs_data preparing: ')
    for i, a in enumerate(albs):
        a_title = a.find_element(By.CLASS_NAME, 'AlbumItemInfo__title').get_attribute('innerHTML')
        a_subtitle = a.find_element(By.CLASS_NAME, 'AlbumItemInfo__subtitle').get_attribute('innerHTML')
        count = int(a_subtitle[:a_subtitle.find(' phot')])
        if count == 0:
            continue
        a_href = a.get_attribute("href")
        name = f'{i}_{a_title}_{count}'
        albs_data.append((name, a_href))
        print(f'{name} album prepared.')

    all_albs_names = [n[0] for n in  albs_data]
    needed = get_needed(available, all_albs_names)
    needed_keys = needed.keys()
    
    for alb_name, alb_url in albs_data:
        if alb_name in needed_keys: 
            get_album(driver, alb_name,
                      alb_url, community_name,
                      needed[alb_name])
    print(f'Community done.')


def get_album(driver,
              alb_name, 
              alb_url, 
              community_name,
              start):
    album_substr = alb_url[alb_url.rfind('/')+1:]
    print(f'getting {alb_name} album...') 
    driver.get(alb_url)
    #save(driver.page_source, 'alb.html')
    try:
        os.mkdir(f'{community_name}/{alb_name}')
    except(FileExistsError):
        print('album directory exist')

    ases = driver.find_elements(By.CLASS_NAME, 'PhotosPhotoItem')
    ases = try_except(NoSuchElementException,
                      'a_tag_photos get is fail...',
                      driver.find_elements,
                      By.CLASS_NAME, 'PhotosPhotoItem')
    photos_count =int(alb_name[alb_name.rfind('_')+1:]) 
    l1 = len(ases)
    while len(ases) < photos_count:
        driver.execute_script("arguments[0].scrollIntoView();", ases[-1])   
        sleep(1)
        ases = try_except(NoSuchElementException,
                          'a_photos get is fail...',
                          driver.find_elements,
                          By.CLASS_NAME, 
                          'PhotosPhotoItem')
        l2 = len(ases)
        print(f'{l2}/{photos_count}', end='\r')
        if l1 == l2:
            driver.execute_script('document.querySelector(".Popup").remove()')
        else:
            l1 = l2
        #save(driver.page_source, 'alb_scrolled.html')

    href_list= [h.get_attribute("href") for h in ases]
    photo_substr_list = [s[s.rfind('/')+1:] for s in href_list]
    photo_substr_list_prepared =\
            photo_substr_list[start:]
    psl = len(photo_substr_list)
    for i, ps in enumerate(photo_substr_list_prepared,
                           start):
        full_url = f'{alb_url}?z={ps}%2F{album_substr}'
        print(f'getting {i}/{psl} : {ps}')
        get_photo(driver, full_url, i, alb_name, community_name)
    print(f'{alb_name} is done.')


def get_photo(driver, href, num, name, community_name):
    driver.get(href)
    #save(driver.page_source, 'ph.html')
    button = try_except(NoSuchElementException,
                        'find_el is fail...',
                        driver.find_element,
                        By.CLASS_NAME,
                        'MediaViewHeader__more')
    if not button:
        print('get_photo try again...')
        get_photo(driver, href, num, name, community_name)
        return

    button.click()
    a_download = driver.find_element(By.CSS_SELECTOR, 'a[data-action-id="download"]')
    
    full = try_except(StaleElementReferenceException,
                      'href get is fail...',
                      a_download.get_attribute,
                      'href')
    if not full:
        print('get_photo try again...')
        get_photo(driver, href, num, name, community_name)
        return

    #img = a_ph.find_element(By.TAG_NAME, 'img')
    #src = img.get_attribute('src')
    photo_resp = req_get(full)
    with open(f'{community_name}/{name}/p{num}.png', 'wb') as file:
        file.write(photo_resp.content) 


def try_except(ex, mes, meth, *params): 
    i = 0
    while True:
        try: 
            res = meth(*params)
            if i > 0:
                print()

            return res
            break
        except(ex):
            i +=1
            if i > 20:
                print()
                print(f'{meth.__name__} is fail')
                return
            else:
                print(f'{i}: {mes}', end='\r')
            sleep(1.5)

if __name__ == '__main__': 
   #get_album()
   get_albums()
