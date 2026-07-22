import SwiftUI
import YouTubeiOSPlayerHelper

/// Wraps Google's own `youtube-ios-player-helper` (YTPlayerView) — the
/// officially sanctioned way to embed YouTube playback on iOS. A hand-rolled
/// WKWebView pointed at a spoofed "https://www.youtube.com" baseURL gets
/// rejected by YouTube for every video (looks like an origin-spoofing
/// attempt); this library sets up the embed origin correctly.
struct YouTubePlayerWebView: UIViewRepresentable {
    let videoId: String
    let startSeconds: Double
    let autoplay: Bool
    let onEnded: () -> Void
    let onError: () -> Void
    let onTimeUpdate: (Double) -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(onEnded: onEnded, onError: onError, onTimeUpdate: onTimeUpdate)
    }

    func makeUIView(context: Context) -> YTPlayerView {
        let playerView = YTPlayerView()
        playerView.delegate = context.coordinator
        context.coordinator.currentVideoId = videoId
        load(into: playerView)
        return playerView
    }

    func updateUIView(_ playerView: YTPlayerView, context: Context) {
        if context.coordinator.currentVideoId != videoId {
            context.coordinator.currentVideoId = videoId
            load(into: playerView)
        }
    }

    private func load(into playerView: YTPlayerView) {
        if autoplay {
            _ = playerView.load(withVideoId: videoId, playerVars: [
                "playsinline": 1,
                "rel": 0,
                "start": Int(startSeconds)
            ])
        } else {
            playerView.cueVideo(byId: videoId, startSeconds: Float(startSeconds))
        }
    }

    final class Coordinator: NSObject, YTPlayerViewDelegate {
        let onEnded: () -> Void
        let onError: () -> Void
        let onTimeUpdate: (Double) -> Void
        var currentVideoId: String = ""

        init(onEnded: @escaping () -> Void, onError: @escaping () -> Void, onTimeUpdate: @escaping (Double) -> Void) {
            self.onEnded = onEnded
            self.onError = onError
            self.onTimeUpdate = onTimeUpdate
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

        @objc(playerView:didPlayTime:)
        func playerView(_ playerView: YTPlayerView, didPlayTime playTime: Float) {
            onTimeUpdate(Double(playTime))
        }
    }
}
