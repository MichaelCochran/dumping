import SwiftUI

struct PlaylistsView: View {
    let channel: YouTubeChannel
    /// Pass nil to switch back to the channel's full uploads feed.
    let onSelect: (YouTubePlaylist?) -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var playlists: [YouTubePlaylist] = []
    @State private var isLoading = true
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            Group {
                if isLoading {
                    ProgressView("Loading playlists...")
                } else if let errorMessage {
                    VStack(spacing: 12) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.largeTitle)
                            .foregroundStyle(.orange)
                        Text(errorMessage)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                        Button("Retry") {
                            Task { await load() }
                        }
                        .buttonStyle(.borderedProminent)
                    }
                } else {
                    List {
                        Button {
                            onSelect(nil)
                            dismiss()
                        } label: {
                            Label("All Uploads", systemImage: "square.stack")
                        }

                        if playlists.isEmpty {
                            Text("This channel has no public playlists.")
                                .foregroundStyle(.secondary)
                        } else {
                            Section("Playlists") {
                                ForEach(playlists) { playlist in
                                    Button {
                                        onSelect(playlist)
                                        dismiss()
                                    } label: {
                                        HStack(spacing: 12) {
                                            AsyncImage(url: playlist.thumbnailURL) { image in
                                                image.resizable().aspectRatio(contentMode: .fill)
                                            } placeholder: {
                                                Rectangle().fill(Color.secondary.opacity(0.2))
                                            }
                                            .frame(width: 48, height: 32)
                                            .clipShape(RoundedRectangle(cornerRadius: 4))

                                            VStack(alignment: .leading, spacing: 2) {
                                                Text(playlist.title)
                                                    .foregroundStyle(.primary)
                                                if let itemCount = playlist.itemCount {
                                                    Text("\(itemCount) videos")
                                                        .font(.caption)
                                                        .foregroundStyle(.secondary)
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            .navigationTitle("Playlists")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
            }
            .task {
                await load()
            }
        }
    }

    private func load() async {
        isLoading = true
        errorMessage = nil
        do {
            playlists = try await YouTubeAPIService.shared.fetchPlaylists(channelId: channel.id)
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }
}
