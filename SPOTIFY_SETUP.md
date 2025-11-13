# Spotify Setup Guide

## Step 1: Create Spotify App

1. Go to https://developer.spotify.com/dashboard
2. Click "Create app"
3. Fill in:
   - **App name**: KaiyaFi (or anything you want)
   - **App description**: Personal music player
   - **Redirect URI**: `http://127.0.0.1:8888/callback`
   - **API**: Check "Web API"
4. Click "Save"

## Step 2: Get Credentials

1. Click on your newly created app
2. Click "Settings"
3. Copy your **Client ID**
4. Click "View client secret" and copy your **Client Secret**

## Step 3: Add Redirect URI (IMPORTANT!)

1. In your app settings, find "Redirect URIs"
2. Click "Edit"
3. Add: `http://127.0.0.1:8888/callback`
4. Click "Add"
5. Click "Save" at the bottom

**Note**: Use `127.0.0.1` NOT `localhost` (Spotify's new requirement)

## Step 4: Configure the Player

1. Run the music player: `python main.py`
2. Type: `config`
3. Paste your Client ID when prompted
4. Paste your Client Secret when prompted
5. Restart the player

## Step 5: First Time Authentication

1. When you first use Spotify features (like `spotify playlists`), a browser will open
2. Log in to Spotify if needed
3. Click "Agree" to authorize the app
4. You'll be redirected to `http://localhost:8888/callback?code=...`
5. Copy the ENTIRE URL from your browser
6. Paste it back into the terminal when prompted
7. Done! You won't need to do this again

## Troubleshooting

**"Invalid redirect URI" error:**
- Make sure you added `http://127.0.0.1:8888/callback` in your Spotify app settings (NOT localhost)
- Make sure you clicked "Add" then "Save" after adding it

**Browser doesn't open:**
- Manually go to the URL shown in the terminal
- Complete the authorization
- Copy the redirect URL back

**"INVALID_CLIENT" error:**
- Double-check your Client ID and Client Secret
- Make sure there are no extra spaces when pasting

## Note

You only need Spotify setup if you want to:
- Access your Spotify playlists
- Search your Spotify library

YouTube Music works without any setup and is used for actual playback!
