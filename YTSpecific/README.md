# YTSpecific

An iOS app that plays videos from **one YouTube channel at a time**: pick a
channel, it queues up that channel's uploads and just keeps playing, skipping
anything you've already watched, and tells you when you're caught up. View
history and likes are tracked locally on-device only — likes are never sent
to YouTube.

## How it works

- **Channel picker** — search by channel name or `@handle`, resolved via the
  YouTube Data API v3. Previously watched channels show up as a "Recent
  Channels" list so you don't have to retype a name each time (local-only,
  swipe to remove an entry).
- **Playback** — videos play through Google's own
  [`youtube-ios-player-helper`](https://github.com/youtube/youtube-ios-player-helper)
  library (a `WKWebView`-based wrapper with the embed origin set up
  correctly). This is the only ToS-compliant way to play YouTube content on
  iOS; the app just decides *which* video ID loads next and auto-advances
  when a video ends. Pulled in via Swift Package Manager — Xcode downloads it
  automatically the first time you open/build the project (needs internet).
- **Queue** — built from the channel's full uploads list (or a single
  playlist — see below), filtered to exclude anything in your local watch
  history, ordered newest-first / oldest-first / shuffled (configurable in
  Settings). When the filtered queue is empty, the app tells you you're
  caught up instead of silently stopping.
- **Playlists** — the "•••" menu's **Playlists** entry (shown while a channel
  is active) lists that channel's public playlists; picking one plays just
  that playlist instead of the full uploads feed, and "All Uploads" switches
  back.
- **History & Likes** — stored locally with SwiftData. Liking a video never
  makes a network call; it's purely a local record you can review or remove.
  Both show the video's original upload date alongside when you watched/liked
  it.
- **Orientation & sizing** — each video's real aspect ratio and tags are
  fetched from the Data API (`videos.list?part=snippet,player`, one call) and
  used to size the player box, so portrait uploads (Shorts) display tall
  instead of being squeezed into a fixed 16:9 strip. Rotating the device to
  landscape expands the video to fill the screen; rotating back to portrait
  returns to the normal layout with title/like/skip below the video — the
  player view stays the same instance across the rotation, so playback
  position isn't lost.
- **Tags** — YouTube never shows a video's creator-set tags in its own UI,
  but they're part of the Data API response; shown as a scrollable row of
  chips under the video title when present.
- **Retry** — if a channel, playlist, or search lookup fails (e.g. a
  connection hiccup), a Retry button re-runs the same request instead of
  leaving you stuck.
- **Resume position** — the current video and timestamp are saved whenever
  the app leaves the foreground. Relaunching (even after iOS has fully killed
  the process — the "locked the phone for a while" case) seeks back to that
  exact spot instead of jumping to the next unwatched video. Note this is
  position memory, not background audio: YouTube's embed terms don't allow
  continuing playback while the app isn't visible, so it does pause when you
  leave, same as before — it just won't lose your place.
- **Autoplay** — toggle in Settings. On (default), each video starts playing
  immediately; off, each video loads paused and you tap play to start it.
- **API key** — stored in the device Keychain via Settings, not committed to
  git, not bundled in the app.

## Setup

### 1. Get a YouTube Data API v3 key

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project (or reuse one) and enable **YouTube Data API v3**.
3. Create an **API key** under *APIs & Services → Credentials*.
4. (Optional but recommended) restrict the key to the YouTube Data API v3.

The free quota (10,000 units/day) comfortably covers personal use — resolving
a channel costs ~100 units and listing its uploads costs ~1 unit per 50
videos.

### 2. Generate the Xcode project

This repo only contains source files plus a project spec — the `.xcodeproj`
itself is generated (and gitignored) so it never goes stale. On a Mac with
Xcode installed:

```bash
brew install xcodegen
cd YTSpecific
xcodegen generate
open YTSpecific.xcodeproj
```

Select an iOS 17+ simulator or device and hit Run.

### 3. Add your API key

Launch the app, tap the gear icon, paste your API key into **Settings →
YouTube Data API Key**, and tap **Save Key**. It's stored in the Keychain —
no rebuild needed, and you can update it any time.

## Project layout

```
YTSpecific/
  project.yml                  # xcodegen spec (generates the .xcodeproj)
  Sources/
    YTSpecificApp.swift
    Models/                    # YouTubeChannel, YouTubeVideo, YouTubePlaylist, PlaybackOrder
    Persistence/                # SwiftData models: WatchedVideoRecord, LikedVideoRecord
    Services/                  # YouTubeAPIService, PlaybackQueueManager, APIKeyStore, RecentChannelStore, ChannelHistoryStore, PlaybackPositionStore
    Views/                     # ContentView, ChannelSearchView, PlayerView, PlaylistsView, YouTubePlayerWebView, HistoryView, LikedVideosView, SettingsView
  Resources/
    Assets.xcassets
```

## Notes / limitations

- Playback still counts as a normal YouTube view under the hood (embedding is
  the only legal playback path) — but likes and history are 100% local.
  A channel that disables embedding for its videos will surface as a
  playback error for that video; the app just skips to the next one.
- "Caught up" is scoped to *unwatched* videos for the active channel. Your
  watch history persists across channel switches, so re-selecting a channel
  later resumes where you left off rather than replaying everything.
