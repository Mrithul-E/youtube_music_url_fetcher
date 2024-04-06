from ytmusicapi import YTMusic
import innertube
import copy
from concurrent.futures import ThreadPoolExecutor

android_music_client = innertube.InnerTube("ANDROID_MUSIC")
web_music_client = innertube.InnerTube("WEB")
yt_music_client = YTMusic()

def get_lyrics(video_id):
    
    def extract_transcript_params(next_data):
        engagement_panels = next_data["engagementPanels"]

        for engagement_panel in engagement_panels:
            engagement_panel_section = engagement_panel[
                "engagementPanelSectionListRenderer"
            ]

            if engagement_panel_section.get("panelIdentifier")!= "engagement-panel-searchable-transcript":
                continue

            return engagement_panel_section["content"]["continuationItemRenderer"]["continuationEndpoint"]["getTranscriptEndpoint"]["params"]
    try:
        data = web_music_client.next(video_id)
        transcript_params = extract_transcript_params(data)
        transcript = web_music_client.get_transcript(transcript_params)
        transcript = web_music_client.get_transcript(transcript)
        transcript_segments = transcript["actions"][0]["updateEngagementPanelAction"]["content"]["transcriptRenderer"]["content"]["transcriptSearchPanelRenderer"]["body"]["transcriptSegmentListRenderer"]["initialSegments"]
        
        return {"synced":True,"lyric":transcript_segments}
    
    except Exception as e:
        
        lyrics_browse_id = yt_music_client.get_watch_playlist(video_id)
                 
        lyric = None
        
        if lyrics_browse_id['lyrics']:
            try:
                lyric = yt_music_client.get_lyrics(lyrics_browse_id['lyrics'])
                return {"synced":False,"lyric":lyric}
            except:
                lyric = yt_music_client.get_lyrics(lyrics_browse_id['lyrics'])
                return {"synced":False,"lyric":lyric} 
        else:
            return None

def get_audio_video_url(video_id):
    
    data = android_music_client.player(video_id=video_id)

    formats = copy.deepcopy(data['streamingData']['formats'])
    formats.extend(data['streamingData']['adaptiveFormats'])

    audio_formats = []
    video_formats = []
    
    for i in formats:
        if i['mimeType'].find("audio") == 0:
            audio_formats.append(i)
        else:
            video_formats.append(i)
    
    return {"audio_formats":audio_formats, "video_formats":video_formats}  

def yt_music_song_video_search(song_name, ignore_spell_correction: bool = False):
    song_name_json = yt_music_client.search(song_name,ignore_spelling = ignore_spell_correction)

    song_and_video = []
    copy_song_json_list = copy.deepcopy(song_name_json)
    pop_index_list = []

    #filter songs and videos
    for count,i in enumerate(song_name_json):
        if i['resultType'] == 'song' and i['category'] != 'Episodes' or i['resultType'] == 'video' and i['category'] != 'Episodes':
            song_and_video.append(i)
            pop_index_list.append(count) 

    for i in sorted(pop_index_list,reverse=True):
        copy_song_json_list.pop(i)
    
    #returning - song_and_video(only song,video) , copy_song_json_list(oother formats without song,video)
    return song_and_video, copy_song_json_list

def get_full_response(song_name, ignore_spell_correction: bool = False,lyrics: bool = False):
    song_and_video, other_formats = yt_music_song_video_search(song_name=song_name, ignore_spell_correction=ignore_spell_correction)
    video_id_list = [id['videoId'] for id in song_and_video]
    
    with ThreadPoolExecutor(max_workers=25) as executor:
        url_list = list(executor.map(get_audio_video_url,video_id_list))
        if lyrics:
            lyrics_list = list(executor.map(get_lyrics,video_id_list))
        else:
            lyrics_list = [None]*len(video_id_list)
            
        song_full_details = []    
        for song_video,url,lyric in zip(song_and_video,url_list,lyrics_list):
            song_video["url"] = url
            song_video["lyric"] = lyric
            
            song_full_details.append(song_video) 
            
        return song_full_details 
