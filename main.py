import requests as req
from requests.exceptions import ConnectTimeout

import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from video_download import video_download as vd
from parse_cookies import get_cookies_from_file

import pickle


def save(src, fname='page.html'):
    method = 'w' if isinstance(src, str) else 'wb'
    with open(fname, method) as file:
        file.write(src) 


def get_content_tabs():
    url = 'https://m.vk.com/?'
    driver = make_driver()
    print(f'getting {url}')
    driver.get(url)
    save(driver.page_source, 'comm.html')
    vkuiTab = try_except(NoSuchElementException,
                      'vkuiTabs get is fail...',
                      driver.find_element,
                      By.CLASS_NAME, 'vkuiTabs__in')
    vtabs = try_except(NoSuchElementException,
                      'vtabs get is fail...',
                      vkuiTab.find_elements,
                      By.XPATH, '*')
    for vt in vtabs:
        print(vt.get_attribute('href'))



#############################################


def collect_vli(driver, v_or_pl=None):
    log = 'playlists'
    if v_or_pl:
        log = 'videos'


    paginator= try_except(NoSuchElementException,
                      'paginator getting...',
                      driver.find_element,
                      By.CLASS_NAME,
                      'vkuiSpinner__host')
    in_after = try_except(NoSuchElementException,
                      'in_after get is fail...',
                      driver.find_element,
                      By.CLASS_NAME,
                      'vkuiPanel__inAfter')
    i = 0
    while paginator:
        driver.execute_script("arguments[0].scrollIntoView();", in_after)  
        print(f'{i}: scrolling {log} ...', end='\r')
        i += 1
        paginator= try_except(NoSuchElementException,
                      'paginator get is fail...',
                      driver.find_element,
                      By.CLASS_NAME,
                      'vkuiSpinner__host',
                      enter_before=1)
    print(f'{i}: scrolling {log} is done') 
    print(f'collecting vli from {log}... dis is takes a time') 
    
    vli = try_except(NoSuchElementException,
                    'video_list_item get is fail...',
                    driver.find_elements,
                    By.CSS_SELECTOR,
                    'a[data-testid="video_list_item"]')
    if not vli:
        vli = []
    print(f'collected vli from {log}: {len(vli)}') 
    return vli


def collect_playlists(vli):
    print(f'collecting playlists: {len(vli)}')
    playlists = []
    for i, v in enumerate(vli):     
        p = prepare_playlist(i, v)
        playlists.append(p)
    
    return playlists


def prepare_playlist(i, v):
    url = v.get_attribute('href')
    title = try_except(NoSuchElementException,
              'title get is fail...',
              v.find_element,
              By.CSS_SELECTOR,
              "div[class*='VideoListItem__title']")
    count = try_except(NoSuchElementException,
              'count get is fail...',
              v.find_element,
              By.CSS_SELECTOR,
              "span[class*='VideoListItem__subtitle']")
    amount = count.get_attribute('innerHTML')
    amount = int(amount[:-6]) # '467 видео'
    title_text = title.get_attribute("innerHTML")
    name = f'{i}_{title_text}_{amount}'  
    return (url, name, amount)


def dowload_playlists(comm_name, playlists, driver, start=0):
    pl_len = len(playlists)
    print(f'downloading {pl_len}-{start}={pl_len-start} playlists')
    total_video_urls = []
    for pl in playlists[start:]:
        print(f'{pl[1]} downloading with {pl[2]} videos')
        path = f'{comm_name}/playlists/{pl[1]}'
        try_create_dir(path)
        if pl[2]:
            pl_name = f'{pl[1]}/{len(playlists)}'
            driver.get(pl[0])
            v_urls, start = dump_or_get_data(driver, path, pl[1], 0)
            total_video_urls += v_urls
            download_video_list(path, v_urls, start, pl_name)
    
    return total_video_urls


def dump_or_get_data(driver, path, pickle_name, is_pl=False):
    start = 0
    data = []
    pickle_path = f'{path}/{pickle_name}.pkl'
    try:
        data = pickle.load(open(pickle_path, "rb"))
        print(f'using cached video urls for {pickle_name}...')
        listdir = os.listdir(path)
        start = len(listdir) - 2
        if start < 0:
            start = 0
    except(FileNotFoundError):
        print(f'no cached video urls for {pickle_name}.')
    if not data:
        if is_pl:
            pl_vli = collect_vli(driver)
            data = collect_playlists(pl_vli)
        else:
            vli = collect_vli(driver, 1)
            data = [v.get_attribute('href') for v in vli] 
        pickle.dump(data, open(pickle_path,"wb"))
    return data, start

def download_video_list(path, video_urls, start, pl_name=None):
    vu_len = len(video_urls)
    print(f'START TO DOWNLOAD {vu_len}-{start}={vu_len-start} VIDEOS!')
    for i, vu in enumerate(video_urls[start:], start=start):
        if pl_name:
            print(pl_name, ': ', end='\t\t', sep='')
        
        vd(path, vu, i, vu_len)
    return vu_len


def download_all_videos(url=None, driver=None):
    url = 'https://m.vkvideo.ru/@metaaaa' # start for videos
    if not driver:
        driver = make_driver()
    print(f'getting {url}')
    driver.get(url)

    community_name = try_except(NoSuchElementException,
                      'community_name get is fail...',
                      driver.find_element,
                      By.TAG_NAME,
                      'h4').get_attribute('innerHTML')
    print(f'scrapping from {community_name}')
    paths_to_create = [f'{community_name}',
                       f'{community_name}/playlists',
                       f'{community_name}/videos']

    for p in paths_to_create:
        try_create_dir(p)

    see_all = try_except(NoSuchElementException,
                  'see_all get is fail...',
                  driver.find_element,
                  By.CSS_SELECTOR,
                  'a[data-testid="market-group-items-header-open-section"]')
    
    playlists = []
    tvc_pl = 0
    if see_all:
        playlists_url = see_all.get_attribute('href')
        driver.get(playlists_url)
        
        pl_path = f'{community_name}/playlists'
        pl_pickle_path = f'playlists'
        playlists, start_pl = dump_or_get_data(driver, 
                                 pl_path, 
                                 pl_pickle_path,
                                 1)
        tvu_pl = dowload_playlists(community_name, playlists, driver, start_pl)  
        driver.get(url)
    v_path = f'{community_name}/videos'
    v_pickle_path = f'videos'
    all_urls, start_videos = dump_or_get_data(driver, 
                             v_path, 
                             v_pickle_path,
                             0)
    pl_urls = [u for u in all_urls if 'videoplaylist' in u]
    
    if pl_urls and not see_all:
        vli = try_except(NoSuchElementException,
                    'video_list_item get is fail...',
                    driver.find_elements,
                    By.CSS_SELECTOR,
                    'a[data-testid="video_list_item"]')
        playlists = collect_playlists(vli[:len(pl_urls)])
        tvu_pl = dowload_playlists(community_name, playlists, driver)  
    print()
    vu_unfiltered = all_urls[len(pl_urls):]
    video_urls = [] # max and filter
    tvu_pl = [u[:u.find('?')] for u in tvu_pl]
    for v in vu_unfiltered:
        if not v[:v.find('?')] in tvu_pl:
            video_urls.append(v)


    print(f'Filtered {len(vu_unfiltered) - len(video_urls)} videos')
    path = f'{community_name}/videos'
    pl_len = len(playlists)

    vu_len = download_video_list(path, video_urls, start_videos)
    
    print()
    print(f'Downloaded {vu_len} videos and {pl_len} playlists with {len(tvu_pl)} videos. ☺')
    
    #print(*enumerate(playlist_urls), sep='\n')


#############################################



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

def make_driver(load_cookies=False):
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless=new")
    options.add_argument("--enable-javascript")

    driver = webdriver.Chrome(options=options)
    

    if load_cookies:
        driver.get('https://m.vk.com/docs?oid=-198891591')
        cookies = get_cookies_from_file()
        sleep(10)
        for cookie in cookies:
          #  print(cookie)
            driver.add_cookie(cookie)
    return driver

def get_albums():
    url = 'url with m' # <==== START
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


def try_except(ex, mes, meth, *params, enter_before=0): 
    try_count = 10
    i = 0
    while True:
        try: 
            res = meth(*params)
            if not res:
                raise ex
            if i > 0:
                print(f'{i}: {mes} done.')

            return res
            break
        except(ex):
            i +=1
            if i > try_count:
                print()
                print(f'{meth.__name__} is fail')
                return
            else:
                if enter_before:
                    print(f'{i}: {mes} done.')
                    enter_before = 0
                print(f'{i}: {mes}', end='\r')
            sleep(1.5)


def try_create_dir(path):
    try:
        os.mkdir(path)
    except(FileExistsError):
        print(f'{path} directory exist')


if __name__ == '__main__': 
   path = ''
   if path:
       os.chdir(path)
       print(f'Current workdir: {path}')
   #get_albums()
   download_all_videos()
