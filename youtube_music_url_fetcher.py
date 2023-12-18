import innertube
from ytmusicapi import YTMusic
from pytube import YouTube
from concurrent.futures import ThreadPoolExecutor
import requests
from concurrent.futures import as_completed
from concurrent.futures import Future
import os 
import mutagen

yt = YTMusic()
client = innertube.InnerTube("WEB")

class download_audio:
    
    def __init__(self, audio_url, file_name,del_file : bool):
        self.audio_url = audio_url
        self.file_name = file_name
        if del_file:
            try:
                os.remove(self.file_name)
            except:
               pass 
        
    
    def get_chunk_list(self):
        r = requests.get(self.audio_url,stream=True)
        byt = r.headers['Content-Length']
        byt = int(byt)

        half_bytes = byt/2
        start_end_bytes = []
        start = 0
        half_bytes = str(half_bytes).replace(".0","")
        try:
            half_bytes = int(half_bytes)
        except:
            half_bytes = float(half_bytes)
                
        if str(type(half_bytes)) == "<class 'float'>":
                half_bytes = half_bytes+0.5

        end = half_bytes

        while True:
            if end > byt:
                end = byt
            if end == byt:
                start_end_bytes.append((start,end))
                break
            start_end_bytes.append((start,end))
            start = end+1
            end = start+(half_bytes-1)
        return start_end_bytes, byt
    
    def download(self,download_data):

        start_byte_and_end_byte, url, file_name = download_data
        future = Future()
        
        headers = {'Range': 'bytes=%d-%d' % (start_byte_and_end_byte[0],start_byte_and_end_byte[1])} 
        r = requests.get(url, stream=False,headers=headers)
        print(r.headers['Content-Length'])
        try:
            # for chunk in r.iter_content(chunk_size=1024):
            # ...
            with open(file_name, 'ab') as audio_file:
                audio_file.write(r.content)
        except:
            import time 
            time.sleep(1)
            
            with open(file_name, 'ab') as audio_file:
                audio_file.write(r.content)
        #saving the byte string to the "future":        
        future.set_result(r.content)        
        return future
    
    def download_file(self):
        chunks,byt = self.get_chunk_list()
        args_list = tuple(((int(chunk[0]),int(chunk[1])), self.audio_url, self.file_name) for chunk in chunks)
        
        import time
        start_time = time.time()
        #_____________________________
        # download the 2 chunks parallel
        
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            for future in as_completed(executor.map(self.download, args_list)):
                result = future.result()
                results.append(result)

        #______________________________ 
        
        # rearrange the 2 binary chunks if the audio file is corrupted 
        try:
            file_info = mutagen.File(self.file_name)
            print(file_info)
            if file_info == {}:
                print("rearranging chunks in the file!!")
                # reverse the results list and write it to file 
                results = results[::-1]
                os.remove(self.file_name)
                with open(self.file_name,"ab") as audio_rearrange:
                    for i in results:
                        audio_rearrange.write(i)
        except:
            print("rearranging chunks in the file!!")
            # reverse the results list and write it to file 
            results = results[::-1]
            os.remove(self.file_name)
            with open(self.file_name,"ab") as audio_rearrange:
                for i in results:
                    audio_rearrange.write(i)
        end_time = time.time()
        
        print(f"start:{start_time}\n end:{end_time}\n\n time_to_run:{end_time-start_time}")

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
                    if i["mimeType"].split(";")[0]=="audio/mp4":
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


def get_song_data_from_name(song_name):
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
    thumbnails = []
    while True:
        if k == len(song_name_json):
            break
        
        if song_name_json[k]['category'] != 'Featured playlists' and song_name_json[k]['category'] != 'Community playlists' and song_name_json[k]['category'] != 'More from YouTube':
            try:
                title_name = song_name_json[k]['title']
                video_id = song_name_json[k]['videoId'] 
                thumbnail_url = song_name_json[k]['thumbnails'][0]['url']
            except:
                k += 1
                continue      
        else:
            k += 1
            continue 
        title_list.append(title_name+" "+"song")
        vide_id_list.append(video_id)
        thumbnails.append(thumbnail_url)
        
        k += 1
        if len(title_list) == 5:
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
    for title,lyric,url,thumbnail in zip(title_list,lyrics,urls,thumbnails): 
        song_data_dict.append({"title":title,"lyric":lyric,"url":url,"thumbnail":thumbnail})
    return song_data_dict
    
#data = get_song_name()    
