import SwiftUI
import SwiftData

struct PlayerView: View {
    let channel: YouTubeChannel
    var queueManager: PlaybackQueueManager
    let onChangeChannel: () -> Void

    @Environment(\.modelContext) private var modelContext
    @Query private var likedRecords: [LikedVideoRecord]

    var body: some View {
        VStack(spacing: 0) {
            if queueManager.isLoading {
                Spacer()
                ProgressView("Loading \(channel.title)...")
                Spacer()
            } else if let errorMessage = queueManager.errorMessage {
                Spacer()
                VStack(spacing: 12) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.largeTitle)
                        .foregroundStyle(.orange)
                    Text(errorMessage)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                Spacer()
            } else if let video = queueManager.currentVideo {
                YouTubePlayerWebView(
                    videoId: video.id,
                    onEnded: { queueManager.advance() },
                    onError: { queueManager.advance() }
                )
                .aspectRatio(16.0 / 9.0, contentMode: .fit)
                .background(Color.black)

                ScrollView {
                    VStack(alignment: .leading, spacing: 12) {
                        Text(video.title)
                            .font(.headline)
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
                    .padding()
                }
            } else if queueManager.isExhausted {
                Spacer()
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
                Spacer()
            }
        }
        .navigationTitle(channel.title)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button("Change Channel", action: onChangeChannel)
            }
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
