from urllib.request import Request, urlopen
from urllib.parse import quote_plus
import locale, json

from bs4 import BeautifulSoup


class ArtistProfiler:
    
    searchapi = "https://itunes.apple.com/search?"
    lang, loc = (locale.getdefaultlocale()[0].split("_"))
    
    def _artist_req_url(artist: str):
        params = f"term={quote_plus(artist)}&entity=musicArtist"
        params += f"&country={ArtistProfiler.loc}&lang="
        params += f"{ArtistProfiler.lang}&media=music"
        return ArtistProfiler.searchapi+params

    def _album_req_url(artist: str):
        query = f"albums by {artist}"
        params = f"term={quote_plus(query)}&entity=album"
        params += f"&country={ArtistProfiler.loc}&lang="
        params += f"{ArtistProfiler.lang}&media=music"
        return ArtistProfiler.searchapi+params

    def _artist(artist):
        res = Browser.request(ArtistProfiler._artist_req_url(artist))
        artist = res["results"][0]["artistName"].lower().strip()
        return artist

    def verify_artist(artist):
        try:
            res = Browser.request(ArtistProfiler._artist_req_url(artist))
            result = res["results"][0]["artistName"].lower().strip()
            if result != artist:            
                msg = f"Using closest match for {artist}:\n"
                msg + f"{result}."
                return msg
            return artist
        except:
            return False    
        
    def _collection_loc_url(artist):
        try:
            result = ArtistProfiler._artist(artist)
            url = ArtistProfiler._album_req_url(result)
            
            res = Browser.request(url)
            album = res["results"][0]
            collection_url = album["collectionViewUrl"]
            track_count = int(album["trackCount"])
            cat_start_id = \
                int(collection_url.split('/')[-1].split('?')[0])
            cat_end_id = \
                cat_start_id + (track_count - 1)
            params = f'i={cat_start_id}-{cat_end_id}'
            return collection_url + params
        except Exception as e:
            print(str(e))

    def _request_artist_info(artist):
        artist = ArtistProfiler._artist(artist)
        album_url = ArtistProfiler._collection_loc_url(artist)
        conn = urlopen(album_url)
        try:
            assert conn.status == 200
            contents = conn.read()
            conn.close()
            html = contents.decode("utf-8")
            html = BeautifulSoup(html, 'lxml')
            html_tag = {
                'element': 'script',
                'class': {"name": "schema:music-album"}}
            results = html.find(html_tag['element'], html_tag['class'])
            results_json = json.loads(results.contents[0])
            return (artist, results_json)
        except Exception as e:
            print(str(e))
        
    def profile(artist: str):
        try:
            name, res = ArtistProfiler._request_artist_info(artist)
            class Artist:
                pass
            artist = Artist()
            artist.name = name
            artist.genres = res["genre"]
            # [TODO] include artist albums & singles
            artist.tophits = [ex["name"] for ex in res["workExample"]]
            return artist
        except Exception as e:
            print(str(e))



class Browser:

    def __init__(self, auth_json=None):
        self.fetch_b64 = lambda url: b64encode(urlopen(url).read().decode("utf-8"))
        self.fetch_html = lambda url: urlopen(url).read().decode("utf-8")
        self.fetch_iostream = lambda url: BytesIO(urlopen(url).read())
        self.fetch_json = lambda url: json.loads(urlopen(url).read())
        self.fetch_retrive = lambda url, path: urlretrieve(url, path)
        self.fetch_content = lambda url: urlopen(url).read()
        
    @staticmethod    
    def request(url: str):
        conn = urlopen(Request(url, 
            headers={"User-Agent": "Sidekick (v1.0)"}))
        if conn.status != 200:
            min_recognized_browser_useragent = \
            {"User-Agent": "Firefox Android Sidekick (v1.0)"}
            headers = min_recognized_browser_useragent
            conn = urlopen(Request(url, headers))
        if conn.status == 200:   
            res = conn.read()
            conn.close()
        else:
            print("Request failed.")
            print(f"Status Code: {conn.status}")
            conn.close()
            return None
        try:
            res=json.loads(res)
        except:
            res=res.decode("utf-8")
        return res
