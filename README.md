# 🎵 KaiyaFi

**Your terminal, your music, your way.** A powerful CLI music player that brings YouTube Music and Spotify to your command line. Stream millions of songs for free, manage playlists, and control everything with simple commands - no GUI needed!

![Screenshot](Screenshots/Screenshot-2025-11-12%20231006.png)
## ✨ Features

- 🎵 **YouTube Music Integration** - Search and play music from YouTube Music (completely free!)
- 🎧 **Spotify Integration** - Access your Spotify playlists and library
- 📝 **Playlist Management** - Create and manage local playlists
- 🔀 **Shuffle Mode** - Randomize your playlist playback
- ⏯️ **Full Playback Controls** - Play, pause, next, previous, volume control
- 🎨 **Beautiful Terminal UI** - Rich formatting with progress bars and real-time updates
- ⚙️ **Customizable Settings** - Configure default volume, auto-play, and more
- 📄 **Pagination** - Browse large playlists with easy page navigation
- 🔄 **Auto-Play** - Automatically plays the next track when current one finishes
- 💾 **Persistent Storage** - All settings and playlists are saved locally

## 🚀 Installation

### Prerequisites

1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **FFmpeg** - Required for audio conversion
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg` or `sudo dnf install ffmpeg`

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/kaiyafi.git
   cd kaiyafi
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the player**
   ```bash
   python main.py
   ```

## 🎮 Usage

### Basic Commands

#### Search & Playback
```bash
search <query>          # Search for music
play <number>           # Play track from search results
pause                   # Pause playback
resume                  # Resume playback
stop                    # Stop playback
next                    # Play next track
prev                    # Play previous track
```

#### Volume Control
```bash
vol <0-100>             # Set volume to specific level
vol+                    # Increase volume by 10%
vol-                    # Decrease volume by 10%
```

#### Playlists
```bash
playlist create <name>  # Create a new playlist
playlist add <name>     # Add current track to playlist
playlist show           # Show all your playlists
playlist load <name>    # Load and play a playlist
shuffle                 # Shuffle current playlist
```

#### Spotify Integration
```bash
spotify playlists       # Show your Spotify playlists
spotify show <number>   # Show tracks in a Spotify playlist
spotify load <number>   # Load and play a Spotify playlist
```

#### Navigation & Settings
```bash
page <number>           # Navigate to specific page
settings                # Show current settings
set <setting> <value>   # Update a setting
now                     # Show now playing info
help                    # Show all commands
quit                    # Exit player
```

![Screenshot](Screenshots/Screenshot%202025-11-13%20125951.png)

## ⚙️ Configuration

### Spotify Setup (Optional)

To access your Spotify playlists:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. In app settings, add Redirect URI: `http://127.0.0.1:8888/callback`
4. Copy your Client ID and Client Secret
5. Run the player and use the `config` command
6. Enter your credentials when prompted
7. Restart the player

**Note:** Spotify is only used for accessing your playlists. Actual playback uses YouTube Music (free).

See [SPOTIFY_SETUP.md](SPOTIFY_SETUP.md) for detailed instructions.

### Settings

Customize your experience with these settings:

```bash
set default_volume 80           # Set default volume (0-100)
set auto_play_next true         # Enable/disable auto-play next track
set results_per_page 30         # Number of results per page (5-100)
```

Settings are saved in `~/.music_player/config.json`

## 📖 Examples

### Example 1: Search and Play
```bash
♪ > search never gonna give you up
# Shows search results
♪ > play 1
# Plays the first result
```

### Example 2: Create and Use Playlist
```bash
♪ > playlist create favorites
♪ > search bohemian rhapsody
♪ > play 1
♪ > playlist add favorites
♪ > playlist load favorites
```

### Example 3: Spotify Playlist
```bash
♪ > spotify playlists
# Shows your Spotify playlists
♪ > spotify show 1
# Shows tracks in playlist #1
♪ > play 5
# Plays track #5 from that playlist
♪ > shuffle
# Shuffles and continues playing
```

![Screenshot](Screenshots/Screenshot%202025-11-13%20125921.png)

## 🗂️ File Structure

```
kaiyafi/
├── main.py              # Main application entry point
├── player.py            # Music player logic (pygame-based)
├── music_sources.py     # YouTube Music & Spotify integration
├── ui.py                # Terminal UI components
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── SPOTIFY_SETUP.md    # Detailed Spotify setup guide
└── .gitignore          # Git ignore rules
```

## 🔧 How It Works

1. **YouTube Music** - Primary source for free music streaming
   - Uses `ytmusicapi` for searching
   - Uses `yt-dlp` for downloading audio streams
   - No API key required!

2. **Spotify** - Optional integration for playlist access
   - Uses `spotipy` for API access
   - Requires developer credentials
   - When playing Spotify tracks, the app searches YouTube Music for the same song

3. **Audio Playback** - Uses pygame mixer
   - Downloads audio to temporary files
   - Converts to MP3 using FFmpeg
   - Supports volume control and seeking

4. **Storage** - All data stored locally
   - Config: `~/.music_player/config.json`
   - Playlists: `~/.music_player/playlists.json`
   - Cache: `~/.music_player/cache/`

## 🐛 Troubleshooting

### No audio playback
- Ensure FFmpeg is installed and in your PATH
- Check system volume settings
- Try adjusting volume with `vol 50`

### Spotify authentication fails
- Verify Client ID and Client Secret are correct
- Ensure redirect URI is exactly `http://127.0.0.1:8888/callback` (not localhost)
- Make sure you clicked "Add" and "Save" in Spotify dashboard
- A browser window will open for first-time authentication

### YouTube download errors
- Update yt-dlp: `pip install --upgrade yt-dlp`
- Some videos may be region-restricted or unavailable

### Permission denied errors
- The app uses temporary files - ensure you have write access to temp directory
- On Windows, try running as administrator if issues persist

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📝 License

MIT License - Feel free to use and modify!

## 🙏 Acknowledgments

- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - YouTube Music API
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [spotipy](https://github.com/spotipy-dev/spotipy) - Spotify API wrapper
- [pygame](https://www.pygame.org/) - Audio playback
- [rich](https://github.com/Textualize/rich) - Terminal formatting

## 📧 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Enjoy your music! 🎵**







