#!/usr/bin/env python3
import sys
import time
from rich.console import Console
from music_sources import YouTubeMusicSource, SpotifySource
from player import MusicPlayer
from ui import (
    display_search_results, display_now_playing, display_playlists,
    display_menu, clear_screen, get_input, console
)
from config import load_config, save_config, load_playlists, save_playlists

class MusicPlayerApp:
    def __init__(self):
        self.player = MusicPlayer()
        self.youtube = YouTubeMusicSource()
        self.spotify = SpotifySource()
        self.search_results = []
        self.playlists = load_playlists()
        self.config = load_config()
        self.running = True
        self.current_page = 1
        self.results_per_page = self.config.get('settings', {}).get('results_per_page', 20)
        
        # Set default volume
        default_vol = self.config.get('settings', {}).get('default_volume', 50)
        self.player.set_volume(default_vol)
        
        # Start auto-play thread
        import threading
        self.auto_play_thread = threading.Thread(target=self._auto_play_loop, daemon=True)
        self.auto_play_thread.start()
    
    def _auto_play_loop(self):
        """Background thread to auto-play next track when current ends"""
        import time
        last_track_id = None
        track_start_time = 0
        
        while self.running:
            try:
                current_track = self.player.current_track
                is_playing = self.player.is_playing_state()
                is_paused = self.player.is_paused
                has_playlist = len(self.player.playlist) > 0
                
                # Track the current track ID
                current_track_id = current_track.get('id') if current_track else None
                
                # Detect if track changed (new track started)
                if current_track_id and current_track_id != last_track_id:
                    last_track_id = current_track_id
                    track_start_time = time.time()
                
                # Only auto-play if:
                # 1. Auto-play is enabled
                # 2. There's a current track
                # 3. Music is not playing (track ended)
                # 4. NOT manually paused by user
                # 5. There's a playlist loaded
                # 6. Track has been playing for at least 5 seconds (to avoid triggering on manual stops)
                if (self.config.get('settings', {}).get('auto_play_next', True) and
                    current_track and 
                    not is_playing and 
                    not is_paused and
                    has_playlist and
                    time.time() - track_start_time > 5):
                    
                    # Wait a moment to confirm it's really finished
                    time.sleep(1)
                    
                    # Triple check: still not playing, NOT paused, still has track, still has playlist
                    if (not self.player.is_playing_state() and 
                        not self.player.is_paused and
                        self.player.current_track and 
                        len(self.player.playlist) > 0):
                        
                        # Play next track
                        track = self.player.play_next()
                        if track:
                            self.play_track_from_info(track)
                            # Reset the track start time for the new track
                            track_start_time = time.time()
                
            except Exception as e:
                pass
            
            time.sleep(2)
    
    def search_music(self, query):
        """Search for music across sources"""
        console.print(f"[cyan]Searching for: {query}[/cyan]")
        
        # Search YouTube Music (primary source for playback)
        yt_results = self.youtube.search(query, limit=30)
        
        # Search Spotify if configured
        sp_results = []
        if self.spotify.sp:
            sp_results = self.spotify.search(query, limit=20)
        
        self.search_results = yt_results + sp_results
        self.current_page = 1
        self.display_paginated_results()
    
    def play_track(self, index):
        """Play a track from search results"""
        if not self.search_results or index < 1 or index > len(self.search_results):
            console.print("[red]Invalid track number[/red]")
            return
        
        track = self.search_results[index - 1]
        console.print(f"[cyan]Loading: {track['title']} by {track['artist']}[/cyan]")
        
        # Check if this track is part of the current playlist
        track_in_playlist = False
        if self.player.playlist:
            try:
                # Find the track in the playlist
                for i, pl_track in enumerate(self.player.playlist):
                    if pl_track['id'] == track['id']:
                        self.player.current_index = i - 1  # Set to one before so play_next works
                        track_in_playlist = True
                        break
            except:
                pass
        
        # If track is NOT in current playlist, this is a standalone play - clear playlist
        if not track_in_playlist:
            self.player.playlist = []
            self.player.current_index = -1
        
        # If Spotify track, search YouTube for playback
        if track['source'] == 'spotify':
            search_query = f"{track['title']} {track['artist']}"
            yt_results = self.youtube.search(search_query, limit=1)
            if yt_results:
                track = yt_results[0]
            else:
                console.print("[red]Could not find playback source[/red]")
                return
        
        # Play using video ID
        if self.player.play(track['id'], track):
            time.sleep(1)
            display_now_playing(track, self.player)
        else:
            console.print("[red]Playback failed[/red]")
    
    def create_playlist(self, name):
        """Create a new playlist"""
        if name in self.playlists:
            console.print(f"[yellow]Playlist '{name}' already exists[/yellow]")
        else:
            self.playlists[name] = []
            save_playlists(self.playlists)
            console.print(f"[green]✓ Created playlist: {name}[/green]")
    
    def add_to_playlist(self, name):
        """Add current track to playlist"""
        if not self.player.current_track:
            console.print("[yellow]No track currently playing[/yellow]")
            return
        
        if name not in self.playlists:
            console.print(f"[red]Playlist '{name}' not found[/red]")
            return
        
        self.playlists[name].append(self.player.current_track)
        save_playlists(self.playlists)
        console.print(f"[green]✓ Added to playlist: {name}[/green]")
    
    def show_playlists(self):
        """Show all playlists"""
        display_playlists(self.playlists)
    
    def load_playlist(self, name):
        """Load and play a playlist"""
        if name not in self.playlists:
            console.print(f"[red]Playlist '{name}' not found[/red]")
            return
        
        tracks = self.playlists[name]
        if not tracks:
            console.print("[yellow]Playlist is empty[/yellow]")
            return
        
        self.player.load_playlist(tracks)
        console.print(f"[green]✓ Loaded playlist: {name} ({len(tracks)} tracks)[/green]")
        
        # Play first track
        track = self.player.play_next()
        if track:
            self.play_track_from_info(track)
    
    def play_track_from_info(self, track):
        """Play a track from track info"""
        # If Spotify track, search YouTube for playback
        play_track = track
        if track.get('source') == 'spotify':
            console.print(f"[cyan]Searching YouTube for: {track['title']} by {track['artist']}[/cyan]")
            search_query = f"{track['title']} {track['artist']}"
            yt_results = self.youtube.search(search_query, limit=1)
            if yt_results:
                play_track = yt_results[0]
            else:
                console.print(f"[red]Could not find YouTube version of: {track['title']}[/red]")
                return
        
        if self.player.play(play_track['id'], play_track):
            time.sleep(1)
            display_now_playing(play_track, self.player)
        else:
            console.print(f"[red]Failed to play: {track['title']}[/red]")
    
    def show_spotify_playlists(self):
        """Show Spotify playlists"""
        if not self.spotify.sp:
            console.print("[red]Spotify not configured. Use 'config' command.[/red]")
            return
        
        playlists = self.spotify.get_user_playlists()
        if not playlists:
            console.print("[yellow]No Spotify playlists found[/yellow]")
            return
        
        from rich.table import Table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Name", style="cyan")
        table.add_column("Tracks", justify="right")
        
        for idx, pl in enumerate(playlists, 1):
            table.add_row(str(idx), pl['name'], str(pl['tracks']))
        
        console.print(table)
        self.spotify_playlists = playlists
    
    def display_paginated_results(self):
        """Display search results with pagination"""
        if not self.search_results:
            console.print("[yellow]No results[/yellow]")
            return
        
        total_pages = (len(self.search_results) - 1) // self.results_per_page + 1
        start_idx = (self.current_page - 1) * self.results_per_page
        end_idx = min(start_idx + self.results_per_page, len(self.search_results))
        
        page_results = self.search_results[start_idx:end_idx]
        
        # Adjust display indices to show actual position in full list
        from rich.table import Table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Title", style="cyan")
        table.add_column("Artist", style="green")
        table.add_column("Album", style="blue")
        table.add_column("Duration", justify="right")
        table.add_column("Source", style="yellow")
        
        for idx, track in enumerate(page_results, start_idx + 1):
            table.add_row(
                str(idx),
                track['title'][:40],
                track['artist'][:30],
                track['album'][:30],
                track['duration'],
                track['source']
            )
        
        console.print(table)
        console.print(f"\n[dim]Page {self.current_page}/{total_pages} | Total: {len(self.search_results)} tracks[/dim]")
        if total_pages > 1:
            console.print("[dim]Use 'page <number>' to navigate pages[/dim]")
    
    def show_spotify_playlist_tracks(self, index):
        """Show tracks in a Spotify playlist"""
        if not hasattr(self, 'spotify_playlists'):
            console.print("[yellow]Run 'spotify playlists' first[/yellow]")
            return
        
        if index < 1 or index > len(self.spotify_playlists):
            console.print("[red]Invalid playlist number[/red]")
            return
        
        playlist = self.spotify_playlists[index - 1]
        console.print(f"[cyan]Loading tracks from: {playlist['name']}...[/cyan]")
        tracks = self.spotify.get_playlist_tracks(playlist['id'])
        
        if tracks:
            # Store as search results so user can play individual tracks
            self.search_results = tracks
            self.player.load_playlist(tracks)
            self.current_page = 1
            self.display_paginated_results()
            console.print(f"\n[green]✓ Loaded {len(tracks)} tracks[/green]")
            console.print("[dim]Type 'play <number>' to play a specific track[/dim]")
            console.print("[dim]Type 'shuffle' to shuffle and play[/dim]")
            console.print("[dim]Type 'next' to play from the beginning[/dim]")
    
    def load_spotify_playlist(self, index):
        """Load and play a Spotify playlist"""
        if not hasattr(self, 'spotify_playlists'):
            console.print("[yellow]Run 'spotify playlists' first[/yellow]")
            return
        
        if index < 1 or index > len(self.spotify_playlists):
            console.print("[red]Invalid playlist number[/red]")
            return
        
        playlist = self.spotify_playlists[index - 1]
        tracks = self.spotify.get_playlist_tracks(playlist['id'])
        
        if tracks:
            self.search_results = tracks
            self.player.load_playlist(tracks)
            console.print(f"[green]✓ Loaded: {playlist['name']} ({len(tracks)} tracks)[/green]")
            
            # Play first track
            track = self.player.play_next()
            if track:
                self.play_track_from_info(track)
    
    def show_settings(self):
        """Show current settings"""
        settings = self.config.get('settings', {})
        console.print("\n[bold cyan]⚙️  Current Settings[/bold cyan]\n")
        console.print(f"[green]default_volume[/green]: {settings.get('default_volume', 50)}")
        console.print(f"[green]auto_play_next[/green]: {settings.get('auto_play_next', True)}")
        console.print(f"[green]results_per_page[/green]: {settings.get('results_per_page', 20)}")
        console.print("\n[dim]Use 'set <setting> <value>' to change[/dim]")
        console.print("[dim]Example: set default_volume 80[/dim]")
    
    def update_setting(self, args):
        """Update a setting"""
        parts = args.split(maxsplit=1)
        if len(parts) != 2:
            console.print("[yellow]Usage: set <setting> <value>[/yellow]")
            return
        
        setting, value = parts
        
        if 'settings' not in self.config:
            self.config['settings'] = {}
        
        if setting == "default_volume":
            try:
                vol = int(value)
                if 0 <= vol <= 100:
                    self.config['settings']['default_volume'] = vol
                    self.player.set_volume(vol)
                    save_config(self.config)
                    console.print(f"[green]✓ Default volume set to {vol}%[/green]")
                else:
                    console.print("[red]Volume must be 0-100[/red]")
            except ValueError:
                console.print("[red]Invalid volume value[/red]")
        
        elif setting == "auto_play_next":
            if value.lower() in ['true', 'yes', '1']:
                self.config['settings']['auto_play_next'] = True
                save_config(self.config)
                console.print("[green]✓ Auto-play next enabled[/green]")
            elif value.lower() in ['false', 'no', '0']:
                self.config['settings']['auto_play_next'] = False
                save_config(self.config)
                console.print("[green]✓ Auto-play next disabled[/green]")
            else:
                console.print("[red]Value must be true/false[/red]")
        
        elif setting == "results_per_page":
            try:
                num = int(value)
                if 5 <= num <= 100:
                    self.config['settings']['results_per_page'] = num
                    self.results_per_page = num
                    save_config(self.config)
                    console.print(f"[green]✓ Results per page set to {num}[/green]")
                else:
                    console.print("[red]Must be between 5-100[/red]")
            except ValueError:
                console.print("[red]Invalid number[/red]")
        else:
            console.print(f"[red]Unknown setting: {setting}[/red]")
            console.print("[dim]Available: default_volume, auto_play_next, results_per_page[/dim]")
    
    def configure(self):
        """Configure API keys"""
        console.print("\n[bold cyan]Spotify Configuration[/bold cyan]\n")
        console.print("[bold yellow]IMPORTANT:[/bold yellow] Before entering credentials:")
        console.print("1. Go to: https://developer.spotify.com/dashboard")
        console.print("2. Create an app (or use existing)")
        console.print("3. In app settings, add Redirect URI: [green]http://127.0.0.1:8888/callback[/green]")
        console.print("   [yellow](Use 127.0.0.1 NOT localhost - Spotify requirement)[/yellow]")
        console.print("4. Click ADD then SAVE in Spotify dashboard")
        console.print("\n[dim]See SPOTIFY_SETUP.md for detailed instructions[/dim]\n")
        
        client_id = get_input("Spotify Client ID (or press Enter to skip): ").strip()
        if not client_id:
            console.print("[yellow]Skipped Spotify configuration[/yellow]")
            return
            
        client_secret = get_input("Spotify Client Secret: ").strip()
        
        if client_id:
            self.config['spotify']['client_id'] = client_id
        if client_secret:
            self.config['spotify']['client_secret'] = client_secret
        
        save_config(self.config)
        console.print("\n[green]✓ Configuration saved[/green]")
        console.print("[yellow]Restart the player to apply changes[/yellow]")
        console.print("\n[dim]Note: YouTube Music works without any configuration![/dim]")
    
    def handle_command(self, command):
        """Handle user commands"""
        parts = command.strip().split(maxsplit=1)
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == "search":
            if args:
                self.search_music(args)
            else:
                console.print("[yellow]Usage: search <query>[/yellow]")
        
        elif cmd == "play":
            try:
                index = int(args)
                self.play_track(index)
            except ValueError:
                console.print("[yellow]Usage: play <number>[/yellow]")
        
        elif cmd == "pause":
            self.player.pause()
            console.print("[yellow]⏸️  Paused[/yellow]")
        
        elif cmd == "resume":
            self.player.resume()
            console.print("[green]▶️  Resumed[/green]")
        
        elif cmd == "stop":
            self.player.stop()
            console.print("[red]⏹️  Stopped[/red]")
            console.print("[dim]Playlist cleared[/dim]")
        
        elif cmd == "next":
            track = self.player.play_next()
            if track:
                self.play_track_from_info(track)
            else:
                console.print("[yellow]No next track[/yellow]")
        
        elif cmd == "prev":
            track = self.player.play_previous()
            if track:
                self.play_track_from_info(track)
            else:
                console.print("[yellow]No previous track[/yellow]")
        
        elif cmd == "vol":
            if args == "+":
                self.player.set_volume(self.player.get_volume() + 10)
                console.print(f"[cyan]🔊 Volume: {self.player.get_volume()}%[/cyan]")
            elif args == "-":
                self.player.set_volume(self.player.get_volume() - 10)
                console.print(f"[cyan]🔊 Volume: {self.player.get_volume()}%[/cyan]")
            else:
                try:
                    vol = int(args)
                    self.player.set_volume(vol)
                    console.print(f"[cyan]🔊 Volume: {vol}%[/cyan]")
                except ValueError:
                    console.print("[yellow]Usage: vol <0-100> or vol+/vol-[/yellow]")
        
        elif cmd == "vol+":
            self.player.set_volume(self.player.get_volume() + 10)
            console.print(f"[cyan]🔊 Volume: {self.player.get_volume()}%[/cyan]")
        
        elif cmd == "vol-":
            self.player.set_volume(self.player.get_volume() - 10)
            console.print(f"[cyan]🔊 Volume: {self.player.get_volume()}%[/cyan]")
        
        elif cmd == "playlist":
            sub_parts = args.split(maxsplit=1)
            if not sub_parts:
                console.print("[yellow]Usage: playlist <create|add|show|load> [name][/yellow]")
                return
            
            sub_cmd = sub_parts[0].lower()
            sub_args = sub_parts[1] if len(sub_parts) > 1 else ""
            
            if sub_cmd == "create" and sub_args:
                self.create_playlist(sub_args)
            elif sub_cmd == "add" and sub_args:
                self.add_to_playlist(sub_args)
            elif sub_cmd == "show":
                self.show_playlists()
            elif sub_cmd == "load" and sub_args:
                self.load_playlist(sub_args)
            else:
                console.print("[yellow]Usage: playlist <create|add|show|load> [name][/yellow]")
        
        elif cmd == "spotify":
            sub_parts = args.split(maxsplit=1)
            if not sub_parts:
                console.print("[yellow]Usage: spotify <playlists|show|load> [number][/yellow]")
                return
            
            sub_cmd = sub_parts[0].lower()
            sub_args = sub_parts[1] if len(sub_parts) > 1 else ""
            
            if sub_cmd == "playlists":
                self.show_spotify_playlists()
            elif sub_cmd == "show" and sub_args:
                try:
                    index = int(sub_args)
                    self.show_spotify_playlist_tracks(index)
                except ValueError:
                    console.print("[yellow]Usage: spotify show <number>[/yellow]")
            elif sub_cmd == "load" and sub_args:
                try:
                    index = int(sub_args)
                    self.load_spotify_playlist(index)
                except ValueError:
                    console.print("[yellow]Usage: spotify load <number>[/yellow]")
            else:
                console.print("[yellow]Usage: spotify <playlists|show|load> [number][/yellow]")
        
        elif cmd == "page":
            try:
                page_num = int(args)
                total_pages = (len(self.search_results) - 1) // self.results_per_page + 1
                if 1 <= page_num <= total_pages:
                    self.current_page = page_num
                    self.display_paginated_results()
                else:
                    console.print(f"[red]Invalid page. Must be 1-{total_pages}[/red]")
            except ValueError:
                console.print("[yellow]Usage: page <number>[/yellow]")
        
        elif cmd == "settings":
            self.show_settings()
        
        elif cmd == "set":
            self.update_setting(args)
        
        elif cmd == "config":
            self.configure()
        
        elif cmd == "shuffle":
            if self.player.playlist:
                self.player.shuffle_playlist()
                console.print("[green]✓ Playlist shuffled[/green]")
                # Play first track after shuffle
                track = self.player.play_next()
                if track:
                    self.play_track_from_info(track)
            else:
                console.print("[yellow]No playlist loaded[/yellow]")
        
        elif cmd == "now":
            if self.player.current_track:
                display_now_playing(self.player.current_track, self.player)
            else:
                console.print("[yellow]No track playing[/yellow]")
        
        elif cmd == "help":
            display_menu()
        
        elif cmd in ["quit", "exit", "q"]:
            self.running = False
            console.print("[cyan]Goodbye! 👋[/cyan]")
        
        else:
            console.print(f"[red]Unknown command: {cmd}[/red]")
            console.print("[dim]Type 'help' for available commands[/dim]")
    
    def run(self):
        """Main application loop"""
        clear_screen()
        console.print("[bold green]🎵 KaiyaFi[/bold green]")
        console.print("[dim]Type 'help' for commands[/dim]\n")
        
        while self.running:
            try:
                command = get_input("♪ >")
                if command:
                    self.handle_command(command)
            except KeyboardInterrupt:
                console.print("\n[cyan]Use 'quit' to exit[/cyan]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
        
        self.player.stop()

def main():
    app = MusicPlayerApp()
    app.run()

if __name__ == "__main__":
    main()
