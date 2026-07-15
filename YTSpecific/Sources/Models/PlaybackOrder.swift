import Foundation

enum PlaybackOrder: String, CaseIterable, Identifiable {
    case newestFirst
    case oldestFirst
    case shuffle

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .newestFirst: return "Newest First"
        case .oldestFirst: return "Oldest First"
        case .shuffle: return "Shuffle"
        }
    }
}
