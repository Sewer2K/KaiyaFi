import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".music_player"
CONFIG_FILE = CONFIG_DIR / "config.json"
PLAYLISTS_FILE = CONFIG_DIR / "playlists.json"
CACHE_DIR = CONFIG_DIR / "cache"

def ensure_config_dir():
    """Create config directory if it doesn't exist"""
    CONFIG_DIR.mkdir(exist_ok=True)
    CACHE_DIR.mkdir(exist_ok=True)

def load_config():
    """Load configuration from file"""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "spotify": {
            "client_id": "",
            "client_secret": "",
            "redirect_uri": "http://127.0.0.1:8888/callback"
        },
        "soundcloud": {
            "auth_token": ""
        },
        "settings": {
            "default_volume": 50,
            "auto_play_next": True,
            "results_per_page": 20
        }
    }

def save_config(config):
    """Save configuration to file"""
    ensure_config_dir()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_playlists():
    """Load playlists from file"""
    ensure_config_dir()
    if PLAYLISTS_FILE.exists():
        with open(PLAYLISTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_playlists(playlists):
    """Save playlists to file"""
    ensure_config_dir()
    with open(PLAYLISTS_FILE, 'w') as f:
        json.dump(playlists, f, indent=2)
