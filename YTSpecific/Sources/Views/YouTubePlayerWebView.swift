import SwiftUI
@preconcurrency import WebKit

/// Wraps YouTube's own IFrame Player API in a WKWebView. This is the only
/// legitimate way to play YouTube video content on iOS — the app just controls
/// *which* video ID loads next, playback itself is YouTube's official player.
struct YouTubePlayerWebView: UIViewRepresentable {
    let videoId: String
    let onEnded: () -> Void
    let onError: () -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(onEnded: onEnded, onError: onError)
    }

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.allowsInlineMediaPlayback = true
        configuration.mediaTypesRequiringUserActionForPlayback = []
        configuration.userContentController.add(context.coordinator, name: "playerEvents")

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.scrollView.isScrollEnabled = false
        webView.isOpaque = false
        webView.backgroundColor = .black
        context.coordinator.currentVideoId = videoId
        webView.loadHTMLString(Self.html(videoId: videoId), baseURL: URL(string: "https://www.youtube.com"))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        if context.coordinator.currentVideoId != videoId {
            context.coordinator.currentVideoId = videoId
            webView.loadHTMLString(Self.html(videoId: videoId), baseURL: URL(string: "https://www.youtube.com"))
        }
    }

    static func dismantleUIView(_ webView: WKWebView, coordinator: Coordinator) {
        webView.configuration.userContentController.removeScriptMessageHandler(forName: "playerEvents")
    }

    private static func html(videoId: String) -> String {
        """
        <!DOCTYPE html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
        <style>html,body,#player{margin:0;padding:0;width:100%;height:100%;background:#000;}</style>
        </head>
        <body>
        <div id="player"></div>
        <script src="https://www.youtube.com/iframe_api"></script>
        <script>
          var player;
          function onYouTubeIframeAPIReady() {
            player = new YT.Player('player', {
              height: '100%',
              width: '100%',
              videoId: '\(videoId)',
              playerVars: { playsinline: 1, autoplay: 1, rel: 0 },
              events: {
                'onStateChange': onPlayerStateChange,
                'onError': onPlayerError
              }
            });
          }
          function onPlayerStateChange(event) {
            window.webkit.messageHandlers.playerEvents.postMessage({ event: 'stateChange', data: event.data });
          }
          function onPlayerError(event) {
            window.webkit.messageHandlers.playerEvents.postMessage({ event: 'error', data: event.data });
          }
        </script>
        </body>
        </html>
        """
    }

    final class Coordinator: NSObject, WKScriptMessageHandler {
        let onEnded: () -> Void
        let onError: () -> Void
        var currentVideoId: String = ""

        init(onEnded: @escaping () -> Void, onError: @escaping () -> Void) {
            self.onEnded = onEnded
            self.onError = onError
        }

        func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
            guard let body = message.body as? [String: Any],
                  let event = body["event"] as? String else { return }

            // YT.PlayerState.ENDED == 0
            if event == "stateChange", let data = body["data"] as? Int, data == 0 {
                DispatchQueue.main.async { self.onEnded() }
            } else if event == "error" {
                DispatchQueue.main.async { self.onError() }
            }
        }
    }
}
