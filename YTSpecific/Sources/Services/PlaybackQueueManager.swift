import Foundation
import SwiftData
import Observation

/// Drives the "just keep playing this channel" experience: loads a channel's
/// uploads, filters out anything already in local watch history, orders what's
/// left per the user's preference, and reports when nothing unwatched remains.
@Observable
final class PlaybackQueueManager {
    private(set) var channel: YouTubeChannel?
    private(set) var currentVideo: YouTubeVideo?
    private(set) var isLoading = false
    private(set) var isExhausted = false
    private(set) var errorMessage: String?

    private var allVideos: [YouTubeVideo] = []
    private var queue: [YouTubeVideo] = []
    private var modelContext: ModelContext?

    func configure(modelContext: ModelContext) {
        self.modelContext = modelContext
    }

    func loadChannel(_ channel: YouTubeChannel, order: PlaybackOrder) async {
        isLoading = true
        errorMessage = nil
        isExhausted = false
        currentVideo = nil
        self.channel = channel
        RecentChannelStore.save(channel)

        do {
            allVideos = try await YouTubeAPIService.shared.fetchAllUploads(for: channel)
            rebuildQueue(order: order)
            advance()
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }

    func rebuildQueue(order: PlaybackOrder) {
        let watchedIds = watchedVideoIds()
        var unwatched = allVideos.filter { !watchedIds.contains($0.id) }

        switch order {
        case .newestFirst:
            unwatched.sort { $0.publishedAt > $1.publishedAt }
        case .oldestFirst:
            unwatched.sort { $0.publishedAt < $1.publishedAt }
        case .shuffle:
            unwatched.shuffle()
        }

        queue = unwatched
    }

    func advance() {
        guard !queue.isEmpty else {
            currentVideo = nil
            isExhausted = !allVideos.isEmpty
            return
        }
        let next = queue.removeFirst()
        currentVideo = next
        isExhausted = false
        recordWatched(next)
    }

    func skip() {
        advance()
    }

    private func recordWatched(_ video: YouTubeVideo) {
        guard let modelContext, let channel else { return }
        let videoId = video.id
        let descriptor = FetchDescriptor<WatchedVideoRecord>(predicate: #Predicate { $0.videoId == videoId })
        if let existing = try? modelContext.fetch(descriptor), !existing.isEmpty {
            return
        }
        let record = WatchedVideoRecord(
            videoId: video.id,
            channelId: video.channelId,
            channelTitle: channel.title,
            title: video.title,
            thumbnailURLString: video.thumbnailURLString
        )
        modelContext.insert(record)
        try? modelContext.save()
    }

    private func watchedVideoIds() -> Set<String> {
        guard let modelContext else { return [] }
        let descriptor = FetchDescriptor<WatchedVideoRecord>()
        let records = (try? modelContext.fetch(descriptor)) ?? []
        return Set(records.map { $0.videoId })
    }
}
