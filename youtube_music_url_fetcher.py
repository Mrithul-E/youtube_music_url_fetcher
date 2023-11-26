import innertube
from ytmusicapi import YTMusic
from pytube import YouTube
from concurrent.futures import ThreadPoolExecutor

yt = YTMusic()
client = innertube.InnerTube("WEB")


def get_audio_url(song_name):
    data = client.search(query=song_name)
    video_id_1st_list = []
    #get video id from search results
    for i in data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']:
        try:
            video_id_str= i['videoRenderer']['videoId']
            video_id_1st_list.append(video_id_str)
        except:
            pass    
    
    link = None
    for j in video_id_1st_list:
            yt=YouTube("https://www.youtube.com/watch?v="+j)
            json_respo = yt.streaming_data
            streamData_adap_formats = json_respo['adaptiveFormats']
            for i in streamData_adap_formats:
                if "mimeType" in i:
                    if i["mimeType"].split(";")[0]=="audio/webm" or i["mimeType"].split(";")[0]=="audio/mp4":
                        if "url" in i:
                            link = i["url"]
                            break
            break               
    return link         

def get_lyrics_of_song(videID):
    lyrics_browse_id = yt.get_watch_playlist(videID)
    lyric = None
    if lyrics_browse_id['lyrics']:
        lyric = yt.get_lyrics(lyrics_browse_id['lyrics'])
    else:
        lyric = None   
    return lyric     


def get_song_name(song_name):
    """
    this function auto-correct the spelling mistakes, get search results from yt-music and 
    then call other functions for getting lyrics and url of song 
    """
    name = song_name
    song_name_json = yt.search(name)
    k = 0
    title_name = None
    title_list = []
    vide_id_list = []
    while True:
        if k == len(song_name_json):
            break
        
        if song_name_json[k]['category'] != 'Featured playlists' or song_name_json[k]['category'] != 'Community playlists':
            try:
                title_name = song_name_json[k]['title']
                video_id = song_name_json[k]['videoId'] 
            except:
                k += 1
                continue      
        else:
            k += 1
            continue 
        title_list.append(title_name+" "+"song")
        vide_id_list.append(video_id)
        
        k += 1
        if len(title_list) == 6:
            break
    #_______________________________________
    
    # artist_names = ""
    # for i in song_name_json[0]['artists']:
    #     artist_names = artist_names+i["name"]
    # song_name = title_name+" "+artist_names
    # print(song_name) 
    
    #_________________________________________
    
    
    # Number of concurrent requests (adjust as needed)
    num_threads = min(8, len(title_list))  # You can adjust the number of threads based on your needs

    # Using ThreadPoolExecutor to parallelize the requests
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        urls = list(executor.map(get_audio_url,title_list))  
        
    num_threads = min(8, len(vide_id_list))  # You can adjust the number of threads based on your needs

    # Using ThreadPoolExecutor to parallelize the requests
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        lyrics = list(executor.map(get_lyrics_of_song,vide_id_list))    
    #get_lyrics_of_song(videID=video_id) 
    song_data_dict = []
    for title,lyric,url in zip(title_list,lyrics,urls): 
        song_data_dict.append({"title":title,"lyric":lyric,"url":url})
    return song_data_dict
    
#data = get_song_name()    
