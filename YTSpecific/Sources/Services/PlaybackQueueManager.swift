import Foundation
import SwiftData
import Observation

/// Drives the "just keep playing this channel (or playlist)" experience:
/// loads a video list, filters out anything already in local watch history,
/// orders what's left per the user's preference, and reports when nothing
/// unwatched remains.
@Observable
final class PlaybackQueueManager {
    private(set) var channel: YouTubeChannel?
    /// Human-readable label for whatever is currently loaded — the channel
    /// name, or "Channel — Playlist Name" when a specific playlist is active.
    private(set) var activeSourceTitle: String?
    private(set) var currentVideo: YouTubeVideo?
    private(set) var isLoading = false
    private(set) var isExhausted = false
    private(set) var errorMessage: String?

    private enum Source {
        case channelUploads(YouTubeChannel)
        case playlist(YouTubePlaylist, channel: YouTubeChannel)
    }

    private var allVideos: [YouTubeVideo] = []
    private var queue: [YouTubeVideo] = []
    private var modelContext: ModelContext?
    private var lastSource: Source?
    private var lastOrder: PlaybackOrder = .newestFirst

    func configure(modelContext: ModelContext) {
        self.modelContext = modelContext
    }

    func loadChannel(_ channel: YouTubeChannel, order: PlaybackOrder) async {
        self.channel = channel
        RecentChannelStore.save(channel)
        await performLoad(sourceTitle: channel.title, source: .channelUploads(channel), order: order) {
            try await YouTubeAPIService.shared.fetchAllUploads(for: channel)
        }
    }

    func loadPlaylist(_ playlist: YouTubePlaylist, channel: YouTubeChannel, order: PlaybackOrder) async {
        self.channel = channel
        RecentChannelStore.save(channel)
        let sourceTitle = "\(channel.title) \u{2014} \(playlist.title)"
        await performLoad(sourceTitle: sourceTitle, source: .playlist(playlist, channel: channel), order: order) {
            try await YouTubeAPIService.shared.fetchAllVideos(inPlaylist: playlist.id, channelId: channel.id)
        }
    }

    /// Re-runs whatever was last loaded (channel uploads or a specific
    /// playlist) — used by the Retry button after a connection failure.
    func retry() async {
        guard let lastSource else { return }
        switch lastSource {
        case .channelUploads(let channel):
            await loadChannel(channel, order: lastOrder)
        case .playlist(let playlist, let channel):
            await loadPlaylist(playlist, channel: channel, order: lastOrder)
        }
    }

    private func performLoad(sourceTitle: String, source: Source, order: PlaybackOrder, fetch: () async throws -> [YouTubeVideo]) async {
        isLoading = true
        errorMessage = nil
        isExhausted = false
        currentVideo = nil
        activeSourceTitle = sourceTitle
        lastSource = source
        lastOrder = order

        do {
            allVideos = try await fetch()
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
            thumbnailURLString: video.thumbnailURLString,
            publishedAt: video.publishedAt
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
