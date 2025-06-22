import sys

import yt_dlp
from yt_dlp.utils import DownloadError


def video_download(path, v_url, i, vu_len):
    ydl_opts = {'outtmpl': f'{path}/{i}_%(title)s.mp4', 'extractor_retries':1,'noprogress': True, 'quiet':True, 'allowed_extractors':['vk']}
    print(f'{i}/{vu_len}: {path} downloading...', end='\r')
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([v_url])
        except DownloadError as e:
            m = e.args[0]
            vn = 'non_vk_video'
            if 'youtube' in m.lower():
                vn = 'some_youtube_video'
            elif 'no video format' in m.lower():
                vn = 'no_video_format'
                
            with open(f'{path}/{i}_{vn}.mp4', 'wb') as file:
                file.write(b'pass')
    print(f'{i}/{vu_len}: {path} done.\t')


if __name__ == '__main__':
    url = sys.argv[1]
    try: 
        path = sys.argv[2]
    except IndexError:
        path = '/storage/emulated/0/Download/vk'
    video_download(path, url, 0)
