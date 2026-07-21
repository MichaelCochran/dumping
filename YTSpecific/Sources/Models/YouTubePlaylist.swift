import Foundation

struct YouTubePlaylist: Identifiable, Codable, Equatable, Hashable {
    let id: String
    let title: String
    let thumbnailURLString: String?
    let itemCount: Int?

    var thumbnailURL: URL? {
        thumbnailURLString.flatMap(URL.init(string:))
    }
}
