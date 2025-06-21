import yt_dlp
from yt_dlp.utils import DownloadError


def video_download(path, v_url, i, vu_len):
    ydl_opts = {'outtmpl': f'{path}/{i}_%(title)s.mp4', 'extractor_retries':1,'noprogress': True, 'quiet':True, 'allowed_extractors':['vk']}
    print(f'{i}/{vu_len}: {path} dowloading...', end='\r')
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([v_url])
        except DownloadError as e:
            m = e.args[0]
            vn = 'non_vk_video'
            if 'youtube' in m.lower():
                vn = 'some_youtube_video'
                
            with open(f'{path}/{i}_{vn}.mp4', 'wb') as file:
                file.write(b'pass')
    print(f'{i}/{vu_len}: {path} done.\t\t')


if __name__ == '__main__':
    #video_download('tvar/playlists/1_pl_69', 'https://m.vkvideo.ru/video-217672821_456239602?from=video', 45)
