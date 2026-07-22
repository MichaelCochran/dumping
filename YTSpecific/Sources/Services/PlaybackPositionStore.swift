import Foundation

/// The single "resume point" for whatever video was last playing, so
/// relaunching after iOS fully kills the app (long background time, memory
/// pressure) can seek back to where you left off instead of starting over.
struct PlaybackPosition: Codable {
    let videoId: String
    let channelId: String
    let positionSeconds: Double
    let savedAt: Date
}

enum PlaybackPositionStore {
    private static let key = "YTSpecific.playbackPosition"

    static func save(_ position: PlaybackPosition) {
        guard let data = try? JSONEncoder().encode(position) else { return }
        UserDefaults.standard.set(data, forKey: key)
    }

    static func load() -> PlaybackPosition? {
        guard let data = UserDefaults.standard.data(forKey: key) else { return nil }
        return try? JSONDecoder().decode(PlaybackPosition.self, from: data)
    }
}
