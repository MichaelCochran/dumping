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

    private var playbackOrder: PlaybackOrder {
        PlaybackOrder(rawValue: playbackOrderRaw) ?? .newestFirst
    }

    var body: some View {
        NavigationStack {
            Group {
                if let channel {
                    PlayerView(channel: channel, queueManager: queueManager, onChangeChannel: {
                        self.channel = nil
                        RecentChannelStore.clear()
                    })
                } else {
                    ChannelSearchView { selected in
                        selectChannel(selected)
                    }
                }
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
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
}
