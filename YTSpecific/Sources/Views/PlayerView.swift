import SwiftUI
import SwiftData

struct PlayerView: View {
    let channel: YouTubeChannel
    var queueManager: PlaybackQueueManager
    let onChangeChannel: () -> Void

    @Environment(\.modelContext) private var modelContext
    @Query private var likedRecords: [LikedVideoRecord]
    @State private var aspectRatio: CGFloat = 16.0 / 9.0

    var body: some View {
        GeometryReader { geometry in
            let isLandscape = geometry.size.width > geometry.size.height

            Group {
                if queueManager.isLoading {
                    centered {
                        ProgressView("Loading \(queueManager.activeSourceTitle ?? channel.title)...")
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
                            Button("Retry") {
                                Task { await queueManager.retry() }
                            }
                            .buttonStyle(.borderedProminent)
                        }
                    }
                } else if let video = queueManager.currentVideo {
                    // IMPORTANT: the player itself stays in the same position
                    // in this VStack regardless of orientation — only its
                    // frame/modifiers change. Wrapping it in an if/landscape
                    // else/portrait branch (two structurally different view
                    // trees) made SwiftUI tear down and recreate the whole
                    // WKWebView on rotation, resetting playback to the start.
                    VStack(alignment: .leading, spacing: 8) {
                        Text(queueManager.activeSourceTitle ?? channel.title)
                            .font(isLandscape ? .caption : .headline)
                            .lineLimit(2)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.horizontal)
                            .padding(.top, isLandscape ? 4 : 8)

                        YouTubePlayerWebView(
                            videoId: video.id,
                            onEnded: { queueManager.advance() },
                            onError: { queueManager.advance() }
                        )
                        .aspectRatio(aspectRatio, contentMode: .fit)
                        .frame(maxWidth: .infinity, maxHeight: isLandscape ? .infinity : geometry.size.height * 0.6)
                        .background(Color.black)

                        if !isLandscape {
                            ScrollView {
                                videoDetails(video: video)
                                    .padding()
                            }
                        }
                    }
                    .task(id: video.id) {
                        aspectRatio = await YouTubeAPIService.shared.fetchAspectRatio(videoId: video.id)
                    }
                } else if queueManager.isExhausted {
                    centered {
                        VStack(spacing: 12) {
                            Image(systemName: "checkmark.seal")
                                .font(.largeTitle)
                                .foregroundStyle(.green)
                            Text("You're all caught up")
                                .font(.headline)
                            Text("You've watched everything currently available in \(queueManager.activeSourceTitle ?? channel.title). Check back later for new uploads.")
                                .multilineTextAlignment(.center)
                                .foregroundStyle(.secondary)
                                .padding(.horizontal)
                        }
                    }
                }
            }
            .frame(width: geometry.size.width, height: geometry.size.height)
        }
        .navigationTitle("YTSpecific")
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
    private func videoDetails(video: YouTubeVideo) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(video.title)
                .font(.headline)
                .lineLimit(3)
            Text("Uploaded \(video.publishedAt.formatted(date: .abbreviated, time: .omitted))")
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
                thumbnailURLString: video.thumbnailURLString,
                publishedAt: video.publishedAt
            )
            modelContext.insert(record)
        }
        try? modelContext.save()
    }
}
