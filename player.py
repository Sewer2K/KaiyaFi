import pygame
import time
import threading
import os
import tempfile
import yt_dlp
from pathlib import Path

# Suppress pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

class MusicPlayer:
    """Pygame-based music player with streaming support"""
    
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        self.current_track = None
        self.playlist = []
        self.current_index = -1
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.5
        pygame.mixer.music.set_volume(self.volume)
        self.current_file = None
        self.start_time = 0
        self.paused_time = 0
    
    def play(self, video_id, track_info=None):
        """Play a track from YouTube video ID"""
        try:
            # Stop current playback and clean up
            pygame.mixer.music.stop()
            time.sleep(0.2)  # Give more time for file to be released
            
            if self.current_file and os.path.exists(self.current_file):
                try:
                    os.remove(self.current_file)
                except Exception as e:
                    # If file is locked, try a different temp file name
                    import random
                    pass
            
            # Download audio to temp file for pygame with unique name
            import random
            temp_dir = tempfile.gettempdir()
            temp_id = random.randint(1000, 9999)
            output_file = os.path.join(temp_dir, f'music_player_temp_{temp_id}.mp3')
            
            # Remove old temp file if exists
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except:
                    pass
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_file.replace('.mp3', '.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'noprogress': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'keepvideo': False,
            }
            
            # Build YouTube URL
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Download the audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
            
            # The file should be converted to mp3
            if not os.path.exists(output_file):
                # Check for the file without extension change
                base = output_file.replace('.mp3', '')
                for ext in ['.mp3', '.m4a', '.webm', '.opus', '.ogg']:
                    test_file = base + ext
                    if os.path.exists(test_file):
                        output_file = test_file
                        break
                else:
                    raise Exception(f"Downloaded file not found. Checked: {base}.*")
            
            # Load and play
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            
            self.current_track = track_info
            self.current_file = output_file
            self.is_playing = True
            self.is_paused = False
            self.start_time = time.time()
            self.paused_time = 0
            
            return True
        except Exception as e:
            print(f"Playback error: {e}")
            return False
    
    def pause(self):
        """Pause playback"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.is_paused = True
            self.paused_time = time.time()
    
    def resume(self):
        """Resume playback"""
        if not self.is_playing and pygame.mixer.music.get_busy():
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.is_paused = False
        elif not self.is_playing:
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
    
    def stop(self):
        """Stop playback"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.current_track = None
        self.playlist = []  # Clear playlist when stopped
        self.current_index = -1
        if self.current_file and os.path.exists(self.current_file):
            try:
                os.remove(self.current_file)
            except:
                pass
    
    def set_volume(self, volume):
        """Set volume (0-100)"""
        self.volume = max(0, min(100, volume)) / 100.0
        pygame.mixer.music.set_volume(self.volume)
    
    def get_volume(self):
        """Get current volume"""
        return int(self.volume * 100)
    
    def get_position(self):
        """Get current playback position (0.0 to 1.0)"""
        if not self.current_track:
            return 0.0
        pos = pygame.mixer.music.get_pos() / 1000.0
        return min(1.0, pos / 180.0)  # Estimate
    
    def set_position(self, position):
        """Set playback position (0.0 to 1.0)"""
        pygame.mixer.music.set_pos(position)
    
    def get_time(self):
        """Get current playback time in milliseconds"""
        if self.is_playing:
            return int((time.time() - self.start_time) * 1000)
        return 0
    
    def get_length(self):
        """Get track length in milliseconds"""
        # Estimate from duration string
        if self.current_track and 'duration' in self.current_track:
            duration = self.current_track['duration']
            if ':' in str(duration):
                parts = str(duration).split(':')
                if len(parts) == 2:
                    mins, secs = parts
                    return (int(mins) * 60 + int(secs)) * 1000
        return 180000  # Default 3 minutes
    
    def is_playing_state(self):
        """Check if currently playing"""
        return self.is_playing and pygame.mixer.music.get_busy()
    
    def load_playlist(self, tracks):
        """Load a playlist"""
        self.playlist = tracks
        self.current_index = -1
    
    def shuffle_playlist(self):
        """Shuffle the current playlist"""
        import random
        if self.playlist:
            random.shuffle(self.playlist)
            self.current_index = -1
    
    def play_next(self):
        """Play next track in playlist"""
        if self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            return self.playlist[self.current_index]
        return None
    
    def play_previous(self):
        """Play previous track in playlist"""
        if self.current_index > 0:
            self.current_index -= 1
            return self.playlist[self.current_index]
        return None
