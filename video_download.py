import yt_dlp


def video_download(path, v_url, i, vu_len):

    ydl_opts = {'outtmpl': f'{path}/{i}_%(title)s.mp4', 'noprogress': True, 'quiet':True}
    #v_url = 'https://m.vkvideo.ru/video-140892259_456242082'
    print(f'{i}/{vu_len}: {path} dowloading...', end='\r')
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([v_url])
    print(f'{i}/{vu_len}: {path} done.')

if __name__ == '__main__':
    video_download('tvar/playlists/1_pl_69', 'https://m.vkvideo.ru/video-217672821_456239602?from=video', 45)
