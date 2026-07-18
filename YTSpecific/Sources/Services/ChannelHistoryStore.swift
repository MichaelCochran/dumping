import Foundation

/// Most-recently-used list of channels you've watched, so you don't have to
/// retype a name/handle every time you switch. Purely local (UserDefaults).
enum ChannelHistoryStore {
    private static let key = "YTSpecific.channelHistoryList"
    private static let maxEntries = 15

    static func recent() -> [YouTubeChannel] {
        guard let data = UserDefaults.standard.data(forKey: key) else { return [] }
        return (try? JSONDecoder().decode([YouTubeChannel].self, from: data)) ?? []
    }

    static func record(_ channel: YouTubeChannel) {
        var channels = recent()
        channels.removeAll { $0.id == channel.id }
        channels.insert(channel, at: 0)
        if channels.count > maxEntries {
            channels = Array(channels.prefix(maxEntries))
        }
        save(channels)
    }

    static func remove(_ channel: YouTubeChannel) {
        var channels = recent()
        channels.removeAll { $0.id == channel.id }
        save(channels)
    }

    private static func save(_ channels: [YouTubeChannel]) {
        guard let data = try? JSONEncoder().encode(channels) else { return }
        UserDefaults.standard.set(data, forKey: key)
    }
}
