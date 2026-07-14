import Foundation

/// Remembers the last channel you were watching so the app reopens straight into it.
enum RecentChannelStore {
    private static let key = "YTSpecific.currentChannel"

    static func save(_ channel: YouTubeChannel) {
        guard let data = try? JSONEncoder().encode(channel) else { return }
        UserDefaults.standard.set(data, forKey: key)
    }

    static func load() -> YouTubeChannel? {
        guard let data = UserDefaults.standard.data(forKey: key) else { return nil }
        return try? JSONDecoder().decode(YouTubeChannel.self, from: data)
    }

    static func clear() {
        UserDefaults.standard.removeObject(forKey: key)
    }
}
