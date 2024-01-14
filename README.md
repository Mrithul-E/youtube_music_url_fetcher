# youtube_music_url_fetcher

# YouTube Music and YouTube API Integration

This Python script, `youtube_music_url_fetcher.py`, leverages the YouTube Music API and YouTube API to retrieve information about songs based on a provided search term. The script is designed to find the top 6 search results for a given song name, extract audio URLs for those songs, and fetch lyrics if available. Additionally, it provides a convenient function, `get_song_name()`, for users to obtain information about a specific song.

## Dependencies

Before using the script, ensure you have the following dependencies installed:

- `innertube`: for fetching video url from youtube
- `ytmusicapi`: for getting lyrics of songs, correct song names
- `pytube`: for getting song url without SignatureCipher
- `concurrent.futures.ThreadPoolExecutor`: for parallelizing requests

You can install the dependencies using the following:

```bash
pip install innertube ytmusicapi pytube
```

## Usage
1. Saving the file named `youtube_music_url_fetcher.py` in your working directory
   
2. Import the necessary module in your project file:

   ```python
   import youtube_music_url_fetcher
   ```
   
3. Use the `get_song_name()` function from `youtube_music_url_fetcher.py` to retrieve information about a song:

   full python code: 
   ```python
   import youtube_music_url_fetcher

   song_info = youtube_music_url_fetcher.get_song_name(song_name="song name ")
   print(song_info)
   ```

   Example Output:

   ```python
   {'title': 'song name', 'lyric': None, 'url': 'long url', "thumbnail":'url of thumbnail'}
   ```

4. Use the `download_file()` function inside `download_audio()` class from `youtube_music_url_fetcher.py` to download the audio file:

   full python code: 
   ```python
   import youtube_music_url_fetcher
   obj = youtube_music_url_fetcher.download_audio(audio_url="audio url extracted using this lib",file_name="name of file",del_file="for deleting the existing file with the file at the starting // pass a bool(True/False)")
   obj.download_file()
   ```
5. getting one url only:

   full python code: 
   ```python
   import youtube_music_url_fetcher

   url = youtube_music_url_fetcher.get_song_name(song_name="song name", url_only=True)
   print(url)
   ```

   Example Output:

   ```python
   ['https://.............']
   ```
   
6. getting url and downloading song:
   
   full code:
   ```python
   import youtube_music_url_fetcher
   
   data = youtube_music_url_fetcher.get_song_data_from_name("song name ")
   print(data)
   
   downloader = youtube_music_url_fetcher.download_audio(audio_url=data[0]['url'],file_name="hi0.mp3",del_file=True)
   downloader.download_file()
   ```
   
## Important Notes

- Keep your dependencies up to date for security and compatibility reasons.

Feel free to modify the script or enhance it based on your specific use case. Happy coding!


# Disclaimer:
USE THE SOFTWARE AT YOUR OWN RISK.THE AUTHOR(S) DISCLAIM ANY WARRANTY OR GUARANTEE OF ITS PERFORMANCE, ACCURACY, OR SUITABILITY FOR ANY PARTICULAR PURPOSE.
THE AUTHOR(S) PROVIDE THIS SOFTWARE 'AS IS' WITHOUT ANY WARRANTY. THEY ARE NOT RESPONSIBLE FOR ANY ISSUES OR CONSEQUENCES ARISING FROM THE USE OF THIS SOFTWARE.
