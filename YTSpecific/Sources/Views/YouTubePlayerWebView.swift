import SwiftUI
import YouTubeiOSPlayerHelper

/// Wraps Google's own `youtube-ios-player-helper` (YTPlayerView) — the
/// officially sanctioned way to embed YouTube playback on iOS. A hand-rolled
/// WKWebView pointed at a spoofed "https://www.youtube.com" baseURL gets
/// rejected by YouTube for every video (looks like an origin-spoofing
/// attempt); this library sets up the embed origin correctly.
struct YouTubePlayerWebView: UIViewRepresentable {
    let videoId: String
    let onEnded: () -> Void
    let onError: () -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(onEnded: onEnded, onError: onError)
    }

    func makeUIView(context: Context) -> YTPlayerView {
        let playerView = YTPlayerView()
        playerView.delegate = context.coordinator
        context.coordinator.currentVideoId = videoId
        _ = playerView.load(withVideoId: videoId, playerVars: [
            "playsinline": 1,
            "rel": 0
        ])
        return playerView
    }

    func updateUIView(_ playerView: YTPlayerView, context: Context) {
        if context.coordinator.currentVideoId != videoId {
            context.coordinator.currentVideoId = videoId
            _ = playerView.load(withVideoId: videoId, playerVars: [
                "playsinline": 1,
                "rel": 0
            ])
        }
    }

    final class Coordinator: NSObject, YTPlayerViewDelegate {
        let onEnded: () -> Void
        let onError: () -> Void
        var currentVideoId: String = ""

        init(onEnded: @escaping () -> Void, onError: @escaping () -> Void) {
            self.onEnded = onEnded
            self.onError = onError
        }

        // Explicit selectors so conformance doesn't depend on guessing the
        // Swift name the ObjC importer would have generated for these
        // @optional protocol methods.
        @objc(playerView:didChangeToState:)
        func playerView(_ playerView: YTPlayerView, didChangeTo state: YTPlayerState) {
            // kYTPlayerStateEnded == 1
            if state.rawValue == 1 {
                onEnded()
            }
        }

        @objc(playerView:receivedError:)
        func playerView(_ playerView: YTPlayerView, receivedError error: YTPlayerError) {
            onError()
        }
    }
}
