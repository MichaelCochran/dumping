import Foundation

struct YouTubeChannel: Identifiable, Codable, Equatable, Hashable {
    let id: String
    let title: String
    let thumbnailURLString: String?
    let uploadsPlaylistId: String

    var thumbnailURL: URL? {
        thumbnailURLString.flatMap(URL.init(string:))
    }
}
