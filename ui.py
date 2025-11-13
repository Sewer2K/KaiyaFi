from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
import requests
from PIL import Image
from io import BytesIO
import os

console = Console()

def display_search_results(tracks):
    """Display search results in a table"""
    if not tracks:
        console.print("[yellow]No results found[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", style="cyan")
    table.add_column("Artist", style="green")
    table.add_column("Album", style="blue")
    table.add_column("Duration", justify="right")
    table.add_column("Source", style="yellow")
    
    for idx, track in enumerate(tracks, 1):
        table.add_row(
            str(idx),
            track['title'][:40],
            track['artist'][:30],
            track['album'][:30],
            track['duration'],
            track['source']
        )
    
    console.print(table)

def display_now_playing(track, player):
    """Display now playing information"""
    import os
    
    # Clear previous display (Windows compatible)
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    
    if not track:
        console.print("[dim]No track playing[/dim]")
        return
    
    title = f"🎵 {track['title']}"
    artist = f"👤 {track['artist']}"
    album = f"💿 {track['album']}"
    source = f"📡 {track['source'].upper()}"
    
    # Progress bar
    length = player.get_length()
    current = player.get_time()
    
    if length > 0:
        progress = current / length
        current_time = f"{current // 60000}:{(current // 1000) % 60:02d}"
        total_time = f"{length // 60000}:{(length // 1000) % 60:02d}"
        bar_width = 40
        filled = int(bar_width * progress)
        bar = "█" * filled + "░" * (bar_width - filled)
        progress_text = f"{current_time} {bar} {total_time}"
    else:
        progress_text = "Loading..."
    
    volume = f"🔊 Volume: {player.get_volume()}%"
    state = "▶️  Playing" if player.is_playing_state() else "⏸️  Paused"
    
    # Next track info
    next_track_info = ""
    if player.playlist and player.current_index < len(player.playlist) - 1:
        next_track = player.playlist[player.current_index + 1]
        next_track_info = f"\n⏭️  Next: {next_track['title']} - {next_track['artist']}"
    
    panel_content = f"""
{title}
{artist}
{album}
{source}

{progress_text}

{state} | {volume}{next_track_info}
"""
    
    panel = Panel(
        panel_content,
        title="[bold green]♪ Now Playing ♪[/bold green]",
        border_style="green"
    )
    
    console.print(panel)

def display_playlists(playlists):
    """Display playlists"""
    if not playlists:
        console.print("[yellow]No playlists found[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="cyan")
    table.add_column("Tracks", justify="right")
    
    for idx, (name, tracks) in enumerate(playlists.items(), 1):
        table.add_row(str(idx), name, str(len(tracks)))
    
    console.print(table)

def display_menu():
    """Display main menu"""
    menu = """
[bold cyan]🎵 KaiyaFi[/bold cyan]

[bold]Commands:[/bold]
  [green]search <query>[/green]          - Search for music
  [green]play <number>[/green]           - Play track from search results
  [green]pause[/green]                   - Pause playback
  [green]resume[/green]                  - Resume playback
  [green]stop[/green]                    - Stop playback
  [green]next[/green]                    - Next track
  [green]prev[/green]                    - Previous track
  [green]vol <0-100>[/green]             - Set volume
  [green]vol+ / vol-[/green]             - Increase/decrease volume
  [green]playlist create <name>[/green]  - Create playlist
  [green]playlist add <name>[/green]     - Add current track to playlist
  [green]playlist show[/green]           - Show all playlists
  [green]playlist load <name>[/green]    - Load and play playlist
  [green]spotify playlists[/green]       - Show Spotify playlists
  [green]spotify show <number>[/green]   - Show tracks in Spotify playlist
  [green]spotify load <number>[/green]   - Load and play Spotify playlist
  [green]shuffle[/green]                 - Shuffle current playlist and play
  [green]page <number>[/green]           - Navigate to page number
  [green]settings[/green]                - Show current settings
  [green]set <setting> <value>[/green]   - Update a setting
  [green]config[/green]                  - Configure API keys
  [green]now[/green]                     - Show now playing (auto-refreshes)
  [green]help[/green]                    - Show this menu
  [green]quit[/green]                    - Exit player

[dim]Tip: Use YouTube Music for free playback, Spotify for library access[/dim]
"""
    console.print(menu)

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_input(prompt=""):
    """Get user input with prompt"""
    return console.input(f"[bold yellow]{prompt}[/bold yellow] ")
