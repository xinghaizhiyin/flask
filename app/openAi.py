import musicbrainzngs

musicbrainzngs.set_useragent("My Music App", "1.0", "https://my-music-app.com")

# 搜索艺术家为 "Coldplay" 的音乐曲目
results = musicbrainzngs.search_recordings(artist='Coldplay', limit=10)

# 提取搜索结果
recordings = results['recording-list']

# 打印热门音乐曲目信息
for recording in recordings:
    title = recording['title']
    artist = recording['artist-credit'][0]['artist']['name']
    print(f"Title: {title}, Artist: {artist}")
