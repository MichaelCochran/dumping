import CoreGraphics
import Foundation

enum YouTubeAPIError: LocalizedError {
    case missingAPIKey
    case channelNotFound
    case requestFailed(String)
    case decodingFailed

    var errorDescription: String? {
        switch self {
        case .missingAPIKey:
            return "No YouTube API key is set. Add one in Settings."
        case .channelNotFound:
            return "Couldn't find a channel matching that name."
        case .requestFailed(let message):
            return message
        case .decodingFailed:
            return "Received an unexpected response from YouTube."
        }
    }
}

/// Talks to the YouTube Data API v3 to resolve a channel by name/handle and
/// enumerate its uploads. This is the only network-facing service in the app —
/// watch history and likes never leave the device.
actor YouTubeAPIService {
    static let shared = YouTubeAPIService()

    private let baseURL = URL(string: "https://www.googleapis.com/youtube/v3/")!
    private let session = URLSession.shared
    private let maxUploadPages = 10 // caps a single channel load at ~500 videos

    private var apiKey: String {
        get throws {
            guard let key = APIKeyStore.load(), !key.isEmpty else {
                throw YouTubeAPIError.missingAPIKey
            }
            return key
        }
    }

    func resolveChannel(query: String) async throws -> YouTubeChannel {
        let trimmed = query.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { throw YouTubeAPIError.channelNotFound }

        if trimmed.hasPrefix("@"), let channel = try? await fetchChannel(forHandle: trimmed) {
            return channel
        }
        return try await searchChannel(byName: trimmed)
    }

    func fetchAllUploads(for channel: YouTubeChannel) async throws -> [YouTubeVideo] {
        var videos: [YouTubeVideo] = []
        var pageToken: String?
        var pagesFetched = 0

        repeat {
            let (items, nextToken) = try await fetchUploadsPage(playlistId: channel.uploadsPlaylistId, pageToken: pageToken, channelId: channel.id)
            videos.append(contentsOf: items)
            pageToken = nextToken
            pagesFetched += 1
        } while pageToken != nil && pagesFetched < maxUploadPages

        return videos
    }

    /// The video's true aspect ratio (width / height), so portrait uploads
    /// (e.g. Shorts) aren't squeezed into a fixed 16:9 box. Falls back to
    /// standard 16:9 on any failure — never throws, since this is only used
    /// to size a view.
    func fetchAspectRatio(videoId: String) async -> CGFloat {
        let standardRatio: CGFloat = 16.0 / 9.0
        guard let key = APIKeyStore.load(), !key.isEmpty else { return standardRatio }

        var components = URLComponents(url: baseURL.appendingPathComponent("videos"), resolvingAgainstBaseURL: false)!
        components.queryItems = [
            URLQueryItem(name: "part", value: "player"),
            URLQueryItem(name: "id", value: videoId),
            // Requesting maxHeight guarantees embedWidth/embedHeight come back
            // scaled to the video's actual aspect ratio.
            URLQueryItem(name: "maxHeight", value: "9999"),
            URLQueryItem(name: "key", value: key)
        ]
        guard let url = components.url,
              let response: VideoPlayerResponse = try? await fetch(url),
              let player = response.items?.first?.player,
              let width = player.embedWidth,
              let height = player.embedHeight,
              width > 0, height > 0 else {
            return standardRatio
        }
        return CGFloat(width) / CGFloat(height)
    }

    // MARK: - Channel resolution

    private func fetchChannel(forHandle handle: String) async throws -> YouTubeChannel {
        var components = URLComponents(url: baseURL.appendingPathComponent("channels"), resolvingAgainstBaseURL: false)!
        components.queryItems = [
            URLQueryItem(name: "part", value: "snippet,contentDetails"),
            URLQueryItem(name: "forHandle", value: handle),
            URLQueryItem(name: "key", value: try apiKey)
        ]
        let response: ChannelListResponse = try await fetch(components.url!)
        guard let item = response.items?.first else { throw YouTubeAPIError.channelNotFound }
        return makeChannel(from: item)
    }

    private func searchChannel(byName name: String) async throws -> YouTubeChannel {
        var searchComponents = URLComponents(url: baseURL.appendingPathComponent("search"), resolvingAgainstBaseURL: false)!
        searchComponents.queryItems = [
            URLQueryItem(name: "part", value: "snippet"),
            URLQueryItem(name: "type", value: "channel"),
            URLQueryItem(name: "maxResults", value: "1"),
            URLQueryItem(name: "q", value: name),
            URLQueryItem(name: "key", value: try apiKey)
        ]
        let searchResponse: SearchListResponse = try await fetch(searchComponents.url!)
        guard let channelId = searchResponse.items?.first?.id.channelId else {
            throw YouTubeAPIError.channelNotFound
        }

        var channelComponents = URLComponents(url: baseURL.appendingPathComponent("channels"), resolvingAgainstBaseURL: false)!
        channelComponents.queryItems = [
            URLQueryItem(name: "part", value: "snippet,contentDetails"),
            URLQueryItem(name: "id", value: channelId),
            URLQueryItem(name: "key", value: try apiKey)
        ]
        let channelResponse: ChannelListResponse = try await fetch(channelComponents.url!)
        guard let item = channelResponse.items?.first else { throw YouTubeAPIError.channelNotFound }
        return makeChannel(from: item)
    }

    private func makeChannel(from item: ChannelListResponse.Item) -> YouTubeChannel {
        YouTubeChannel(
            id: item.id,
            title: item.snippet.title,
            thumbnailURLString: item.snippet.thumbnails.medium?.url ?? item.snippet.thumbnails.defaultThumbnail?.url,
            uploadsPlaylistId: item.contentDetails.relatedPlaylists.uploads
        )
    }

    // MARK: - Uploads

    private func fetchUploadsPage(playlistId: String, pageToken: String?, channelId: String) async throws -> ([YouTubeVideo], String?) {
        var components = URLComponents(url: baseURL.appendingPathComponent("playlistItems"), resolvingAgainstBaseURL: false)!
        var queryItems = [
            URLQueryItem(name: "part", value: "snippet,contentDetails"),
            URLQueryItem(name: "playlistId", value: playlistId),
            URLQueryItem(name: "maxResults", value: "50"),
            URLQueryItem(name: "key", value: try apiKey)
        ]
        if let pageToken {
            queryItems.append(URLQueryItem(name: "pageToken", value: pageToken))
        }
        components.queryItems = queryItems

        let response: PlaylistItemsResponse = try await fetch(components.url!)
        let formatter = ISO8601DateFormatter()
        let videos: [YouTubeVideo] = (response.items ?? []).compactMap { item in
            guard let videoId = item.contentDetails?.videoId else { return nil }
            let publishedString = item.contentDetails?.videoPublishedAt ?? item.snippet.publishedAt
            let publishedAt = formatter.date(from: publishedString) ?? .distantPast
            return YouTubeVideo(
                id: videoId,
                channelId: channelId,
                title: item.snippet.title,
                thumbnailURLString: item.snippet.thumbnails.medium?.url ?? item.snippet.thumbnails.defaultThumbnail?.url,
                publishedAt: publishedAt
            )
        }
        return (videos, response.nextPageToken)
    }

    // MARK: - Networking

    private func fetch<T: Decodable>(_ url: URL) async throws -> T {
        let (data, response) = try await session.data(from: url)
        guard let httpResponse = response as? HTTPURLResponse else {
            throw YouTubeAPIError.requestFailed("No response from YouTube.")
        }
        guard (200..<300).contains(httpResponse.statusCode) else {
            if let apiError = try? JSONDecoder().decode(APIErrorResponse.self, from: data) {
                throw YouTubeAPIError.requestFailed(apiError.error.message)
            }
            throw YouTubeAPIError.requestFailed("YouTube returned status \(httpResponse.statusCode).")
        }
        do {
            return try JSONDecoder().decode(T.self, from: data)
        } catch {
            throw YouTubeAPIError.decodingFailed
        }
    }
}

// MARK: - Response models

private struct APIErrorResponse: Decodable {
    struct ErrorBody: Decodable { let message: String }
    let error: ErrorBody
}

private struct Thumbnails: Decodable {
    struct Thumbnail: Decodable { let url: String }
    let medium: Thumbnail?
    let defaultThumbnail: Thumbnail?

    private enum CodingKeys: String, CodingKey {
        case medium
        case defaultThumbnail = "default"
    }
}

private struct Snippet: Decodable {
    let title: String
    let publishedAt: String
    let thumbnails: Thumbnails
}

private struct RelatedPlaylists: Decodable {
    let uploads: String
}

private struct ContentDetails: Decodable {
    let relatedPlaylists: RelatedPlaylists
}

private struct ChannelListResponse: Decodable {
    struct Item: Decodable {
        let id: String
        let snippet: Snippet
        let contentDetails: ContentDetails
    }
    let items: [Item]?
}

private struct SearchListResponse: Decodable {
    struct ItemId: Decodable { let channelId: String? }
    struct Item: Decodable {
        let id: ItemId
    }
    let items: [Item]?
}

private struct PlaylistItemContentDetails: Decodable {
    let videoId: String?
    let videoPublishedAt: String?
}

private struct PlaylistItemsResponse: Decodable {
    struct Item: Decodable {
        let snippet: Snippet
        let contentDetails: PlaylistItemContentDetails?
    }
    let items: [Item]?
    let nextPageToken: String?
}

private struct VideoPlayerResponse: Decodable {
    struct Player: Decodable {
        let embedWidth: Int?
        let embedHeight: Int?
    }
    struct Item: Decodable {
        let player: Player
    }
    let items: [Item]?
}
