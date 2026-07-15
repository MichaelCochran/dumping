import Foundation
import SwiftData

@Model
final class WatchedVideoRecord {
    @Attribute(.unique) var videoId: String
    var channelId: String
    var channelTitle: String
    var title: String
    var thumbnailURLString: String?
    var watchedAt: Date

    init(videoId: String, channelId: String, channelTitle: String, title: String, thumbnailURLString: String?, watchedAt: Date = .now) {
        self.videoId = videoId
        self.channelId = channelId
        self.channelTitle = channelTitle
        self.title = title
        self.thumbnailURLString = thumbnailURLString
        self.watchedAt = watchedAt
    }
}
