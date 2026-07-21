import Foundation
import SwiftData

@Model
final class LikedVideoRecord {
    @Attribute(.unique) var videoId: String
    var channelId: String
    var channelTitle: String
    var title: String
    var thumbnailURLString: String?
    var likedAt: Date
    /// When the video itself was uploaded (distinct from likedAt). Optional
    /// so existing local records without it still load fine.
    var publishedAt: Date?

    init(videoId: String, channelId: String, channelTitle: String, title: String, thumbnailURLString: String?, likedAt: Date = .now, publishedAt: Date? = nil) {
        self.videoId = videoId
        self.channelId = channelId
        self.channelTitle = channelTitle
        self.title = title
        self.thumbnailURLString = thumbnailURLString
        self.likedAt = likedAt
        self.publishedAt = publishedAt
    }
}
