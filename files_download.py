
import requests as req
from requests.exceptions import ConnectTimeout

from time import sleep
import json

from main import try_create_dir

INVALID_FILE_CHARS = '/\\?%*:|"<>'

def clean_fn(fn):
    return ''.join([c if c not in INVALID_FILE_CHARS else '_' for c in fn ])


def read_file_to_string(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
            return file_content
    except FileNotFoundError:
        print(f"Error: File not found at path: {file_path}")
        return None


def files_download(url=None):
    if not url:
        url = 'https://api.vk.com/method/docs.get?v=5.253&client_id=your_id'
     
    offset = 0
    p_count = offset + 100
    params = {
              #'owner_id': your id, 
              'owner_id': 228, 
              'count': p_count,
              'offset':offset,
              'access_token': 'vk1.a.'}

    #cn = 'community name'
    cn = 'some cringe' 
    ptc = [cn, f'{cn}/files']
    [try_create_dir(p) for p in ptc]
    save_path= f'{ptc[1]}/{cn}_urls.json'
    dld = read_file_to_string(save_path)

    if dld:
        dld = json.loads(dld)
        print('Items: ', len(dld))
        download_files(dld, cn, ptc[1])
        return



    data = None
    resp = req.get(url, params=params)
    if resp.status_code == 200:
        data = resp.json()
        if 'response' in data.keys():
            with open(f'{ptc[1]}/{cn}_resp.txt', 'wb') as file:
                file.write(resp.content)
        else:
            print(data)
            return
    else:
        print(f"Error: {response.status_code}")
        return
    
    dld = []
    if data:
        data = data['response']
        count = data['count']
        dld = scrap(data['items'])
        offset = len(data['items'])
        while len(dld) < count:
            params['offset'] = offset
            resp = req.get(url, params=params)
            data = resp.json()
            try:
                data = data['response'] 
            except(e):
                print(e)
                print('OK, wait...')
                sleep(5)
                continue
            offset += p_count
            dld += scrap(data['items'])

    print('Items: ', len(dld))
    jdump = json.dumps(dld, indent=4)
    with open(save_path, 'w') as file:
        file.write(jdump)

    #download_files(dld, cn, ptc[1])

            
def download_files(dld, cn, path):
    for i, d in enumerate(dld):
        resp = req.get(d[1])
        fname = f'{i}_{d[0]}'
        with open(f'{path}/{fname}', 'wb') as file:
            file.write(resp.content) 

        print(f'{len(dld)}/{i}: {d[0]}', 'done.')
    print(f'Download {len(dld)} files done.')


def scrap(items):
    res = []
    for item in items:
        fname = clean_fn(item['title'])
        url = item['url']
        res.append((fname, url))

    return res


if __name__ == '__main__':
    files_download()

