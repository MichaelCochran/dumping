import SwiftUI
import SwiftData

struct PlayerView: View {
    let channel: YouTubeChannel
    var queueManager: PlaybackQueueManager
    let onChangeChannel: () -> Void

    @Environment(\.modelContext) private var modelContext
    @Query private var likedRecords: [LikedVideoRecord]

    var body: some View {
        GeometryReader { geometry in
            let isLandscape = geometry.size.width > geometry.size.height

            Group {
                if queueManager.isLoading {
                    centered {
                        ProgressView("Loading \(channel.title)...")
                    }
                } else if let errorMessage = queueManager.errorMessage {
                    centered {
                        VStack(spacing: 12) {
                            Image(systemName: "exclamationmark.triangle")
                                .font(.largeTitle)
                                .foregroundStyle(.orange)
                            Text(errorMessage)
                                .multilineTextAlignment(.center)
                                .padding(.horizontal)
                        }
                    }
                } else if let video = queueManager.currentVideo {
                    if isLandscape {
                        landscapePlayer(video: video)
                    } else {
                        portraitPlayer(video: video)
                    }
                } else if queueManager.isExhausted {
                    centered {
                        VStack(spacing: 12) {
                            Image(systemName: "checkmark.seal")
                                .font(.largeTitle)
                                .foregroundStyle(.green)
                            Text("You're all caught up")
                                .font(.headline)
                            Text("You've watched every \(channel.title) video currently available. Check back later for new uploads.")
                                .multilineTextAlignment(.center)
                                .foregroundStyle(.secondary)
                                .padding(.horizontal)
                        }
                    }
                }
            }
            .frame(width: geometry.size.width, height: geometry.size.height)
        }
        .navigationTitle(channel.title)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button("Change Channel", action: onChangeChannel)
            }
        }
    }

    @ViewBuilder
    private func centered<Content: View>(@ViewBuilder content: () -> Content) -> some View {
        VStack {
            Spacer()
            content()
            Spacer()
        }
    }

    @ViewBuilder
    private func portraitPlayer(video: YouTubeVideo) -> some View {
        VStack(spacing: 0) {
            YouTubePlayerWebView(
                videoId: video.id,
                onEnded: { queueManager.advance() },
                onError: { queueManager.advance() }
            )
            .aspectRatio(16.0 / 9.0, contentMode: .fit)
            .frame(maxWidth: .infinity)
            .background(Color.black)

            ScrollView {
                videoDetails(video: video)
                    .padding()
            }
        }
    }

    @ViewBuilder
    private func landscapePlayer(video: YouTubeVideo) -> some View {
        // In landscape the video fills the whole available space (YouTube's
        // own player letterboxes to the right aspect ratio internally); a
        // translucent bar keeps title/like/skip reachable without shrinking
        // the video.
        ZStack(alignment: .bottom) {
            YouTubePlayerWebView(
                videoId: video.id,
                onEnded: { queueManager.advance() },
                onError: { queueManager.advance() }
            )
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Color.black)

            videoDetails(video: video)
                .padding(.horizontal)
                .padding(.vertical, 10)
                .background(.ultraThinMaterial)
        }
    }

    @ViewBuilder
    private func videoDetails(video: YouTubeVideo) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(video.title)
                .font(.headline)
                .lineLimit(2)
            Text(channel.title)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            HStack(spacing: 16) {
                Button {
                    toggleLike(video)
                } label: {
                    Label(isLiked(video) ? "Liked" : "Like", systemImage: isLiked(video) ? "heart.fill" : "heart")
                }
                .tint(isLiked(video) ? .red : .primary)

                Button {
                    queueManager.skip()
                } label: {
                    Label("Skip", systemImage: "forward.end")
                }
            }
            .buttonStyle(.bordered)
        }
    }

    private func isLiked(_ video: YouTubeVideo) -> Bool {
        likedRecords.contains { $0.videoId == video.id }
    }

    private func toggleLike(_ video: YouTubeVideo) {
        if let existing = likedRecords.first(where: { $0.videoId == video.id }) {
            modelContext.delete(existing)
        } else {
            let record = LikedVideoRecord(
                videoId: video.id,
                channelId: video.channelId,
                channelTitle: channel.title,
                title: video.title,
                thumbnailURLString: video.thumbnailURLString
            )
            modelContext.insert(record)
        }
        try? modelContext.save()
    }
}
