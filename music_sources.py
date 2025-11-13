import yt_dlp
from ytmusicapi import YTMusic
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import load_config, CACHE_DIR

class MusicSource:
    """Base class for music sources"""
    
    def search(self, query, limit=10):
        raise NotImplementedError
    
    def get_stream_url(self, track_id):
        raise NotImplementedError


class YouTubeMusicSource(MusicSource):
    """YouTube Music integration"""
    
    def __init__(self):
        self.ytmusic = YTMusic()
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'no_color': True,
        }
    
    def search(self, query, limit=10):
        """Search YouTube Music"""
        try:
            results = self.ytmusic.search(query, filter="songs", limit=limit)
            tracks = []
            for item in results:
                tracks.append({
                    'id': item.get('videoId'),
                    'title': item.get('title', 'Unknown'),
                    'artist': ', '.join([a['name'] for a in item.get('artists', [])]),
                    'album': item.get('album', {}).get('name', 'Unknown'),
                    'duration': item.get('duration', 'Unknown'),
                    'thumbnail': item.get('thumbnails', [{}])[-1].get('url', ''),
                    'source': 'youtube'
                })
            return tracks
        except Exception as e:
            print(f"YouTube search error: {e}")
            return []
    
    def get_stream_url(self, track_id):
        """Get streaming URL for a track"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(f"https://music.youtube.com/watch?v={track_id}", download=False)
                return info['url']
        except Exception as e:
            print(f"Error getting stream URL: {e}")
            return None


class SpotifySource(MusicSource):
    """Spotify integration"""
    
    def __init__(self):
        config = load_config()
        self.sp = None
        if config['spotify']['client_id'] and config['spotify']['client_secret']:
            try:
                self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                    client_id=config['spotify']['client_id'],
                    client_secret=config['spotify']['client_secret'],
                    redirect_uri=config['spotify']['redirect_uri'],
                    scope="user-library-read playlist-read-private user-read-playback-state",
                    cache_path=str(CACHE_DIR / ".spotify_cache"),
                    open_browser=True
                ))
            except Exception as e:
                print(f"Spotify auth error: {e}")
                self.sp = None
    
    def search(self, query, limit=10):
        """Search Spotify"""
        if not self.sp:
            return []
        
        try:
            results = self.sp.search(q=query, limit=limit, type='track')
            tracks = []
            for item in results['tracks']['items']:
                tracks.append({
                    'id': item['id'],
                    'title': item['name'],
                    'artist': ', '.join([a['name'] for a in item['artists']]),
                    'album': item['album']['name'],
                    'duration': f"{item['duration_ms'] // 60000}:{(item['duration_ms'] // 1000) % 60:02d}",
                    'thumbnail': item['album']['images'][0]['url'] if item['album']['images'] else '',
                    'source': 'spotify',
                    'preview_url': item.get('preview_url', '')
                })
            return tracks
        except Exception as e:
            print(f"Spotify search error: {e}")
            return []
    
    def get_user_playlists(self):
        """Get user's Spotify playlists"""
        if not self.sp:
            return []
        
        try:
            playlists = self.sp.current_user_playlists()
            return [{
                'id': p['id'],
                'name': p['name'],
                'tracks': p['tracks']['total']
            } for p in playlists['items']]
        except Exception as e:
            print(f"Error getting playlists: {e}")
            return []
    
    def get_playlist_tracks(self, playlist_id):
        """Get tracks from a Spotify playlist"""
        if not self.sp:
            return []
        
        try:
            results = self.sp.playlist_tracks(playlist_id)
            tracks = []
            for item in results['items']:
                track = item['track']
                if track:
                    duration_ms = track.get('duration_ms', 0)
                    duration_str = f"{duration_ms // 60000}:{(duration_ms // 1000) % 60:02d}" if duration_ms else "0:00"
                    
                    tracks.append({
                        'id': track['id'],
                        'title': track['name'],
                        'artist': ', '.join([a['name'] for a in track['artists']]),
                        'album': track['album']['name'],
                        'duration': duration_str,
                        'thumbnail': track['album']['images'][0]['url'] if track['album'].get('images') else '',
                        'source': 'spotify'
                    })
            return tracks
        except Exception as e:
            print(f"Error getting playlist tracks: {e}")
            return []
