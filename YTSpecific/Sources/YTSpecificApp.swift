import SwiftUI
import SwiftData

@main
struct YTSpecificApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [WatchedVideoRecord.self, LikedVideoRecord.self])
    }
}
