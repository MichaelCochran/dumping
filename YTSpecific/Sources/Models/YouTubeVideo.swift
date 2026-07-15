import Foundation

struct YouTubeVideo: Identifiable, Codable, Equatable, Hashable {
    let id: String
    let channelId: String
    let title: String
    let thumbnailURLString: String?
    let publishedAt: Date

    var thumbnailURL: URL? {
        thumbnailURLString.flatMap(URL.init(string:))
    }
}
