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
     
    def get_related(name):
        try:
            browseid = YTMusic().search(name)[0]["browseId"]
            results = YTMusic().get_artist(browseid)["related"]["results"]
            return [r["title"] for r in results]
        except:
            return [name]
        
    def profile(artist: str):
        try:
            name, res = ArtistProfiler._request_artist_info(artist)
            class Artist:
                pass
            artist = Artist()
            artist.name = name
            artist.genres = res["genre"]
            artist.related = ArtistProfiler.get_related(artist.name)
            artist.tophits = [ex["name"] for ex in res["workExample"]]
            return artist
        except Exception as e:
            print(str(e))
