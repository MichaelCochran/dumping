import SwiftUI
import SwiftData

struct ContentView: View {
    @Environment(\.modelContext) private var modelContext
    @AppStorage("YTSpecific.playbackOrder") private var playbackOrderRaw: String = PlaybackOrder.newestFirst.rawValue
    @State private var queueManager = PlaybackQueueManager()
    @State private var channel: YouTubeChannel?
    @State private var showingHistory = false
    @State private var showingLiked = false
    @State private var showingSettings = false
    @State private var showingPlaylists = false

    private var playbackOrder: PlaybackOrder {
        PlaybackOrder(rawValue: playbackOrderRaw) ?? .newestFirst
    }

    var body: some View {
        NavigationStack {
            Group {
                if let channel {
                    PlayerView(
                        channel: channel,
                        queueManager: queueManager,
                        onChangeChannel: {
                            self.channel = nil
                            RecentChannelStore.clear()
                        }
                    )
                } else {
                    ChannelSearchView { selected in
                        selectChannel(selected)
                    }
                }
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        if channel != nil {
                            Button {
                                showingPlaylists = true
                            } label: {
                                Label("Playlists", systemImage: "list.bullet")
                            }
                        }
                        Button {
                            showingHistory = true
                        } label: {
                            Label("History", systemImage: "clock.arrow.circlepath")
                        }
                        Button {
                            showingLiked = true
                        } label: {
                            Label("Liked", systemImage: "heart")
                        }
                        Button {
                            showingSettings = true
                        } label: {
                            Label("Settings", systemImage: "gearshape")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
            .sheet(isPresented: $showingHistory) { HistoryView() }
            .sheet(isPresented: $showingLiked) { LikedVideosView() }
            .sheet(isPresented: $showingSettings) {
                SettingsView(onOrderChange: {
                    queueManager.rebuildQueue(order: playbackOrder)
                })
            }
            .sheet(isPresented: $showingPlaylists) {
                if let channel {
                    PlaylistsView(channel: channel) { selectedPlaylist in
                        selectPlaylist(selectedPlaylist, channel: channel)
                    }
                }
            }
        }
        .onAppear {
            queueManager.configure(modelContext: modelContext)
            if let saved = RecentChannelStore.load() {
                channel = saved
                Task { await queueManager.loadChannel(saved, order: playbackOrder) }
            }
        }
    }

    private func selectChannel(_ selected: YouTubeChannel) {
        ChannelHistoryStore.record(selected)
        channel = selected
        Task {
            queueManager.configure(modelContext: modelContext)
            await queueManager.loadChannel(selected, order: playbackOrder)
        }
    }

    private func selectPlaylist(_ playlist: YouTubePlaylist?, channel: YouTubeChannel) {
        Task {
            queueManager.configure(modelContext: modelContext)
            if let playlist {
                await queueManager.loadPlaylist(playlist, channel: channel, order: playbackOrder)
            } else {
                await queueManager.loadChannel(channel, order: playbackOrder)
            }
        }
    }
}
