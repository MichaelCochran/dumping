import SwiftUI

struct ChannelSearchView: View {
    let onSelect: (YouTubeChannel) -> Void

    @State private var query = ""
    @State private var isSearching = false
    @State private var errorMessage: String?
    @State private var recentChannels: [YouTubeChannel] = ChannelHistoryStore.recent()

    var body: some View {
        VStack(spacing: 12) {
            VStack(spacing: 12) {
                Image(systemName: "play.tv")
                    .font(.system(size: 40))
                    .foregroundStyle(.secondary)
                Text("Watch one channel at a time")
                    .font(.title2.bold())
                Text("Type a channel name or @handle to start an endless queue of just their videos.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)

                HStack {
                    TextField("Channel name or @handle", text: $query)
                        .textFieldStyle(.roundedBorder)
                        .autocorrectionDisabled()
                        .textInputAutocapitalization(.never)
                        .onSubmit(search)
                    Button("Go", action: search)
                        .disabled(query.trimmingCharacters(in: .whitespaces).isEmpty || isSearching)
                }
                .padding(.horizontal)

                if isSearching {
                    ProgressView()
                }
                if let errorMessage {
                    Text(errorMessage)
                        .font(.footnote)
                        .foregroundStyle(.red)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
            }
            .padding(.top, 24)

            if recentChannels.isEmpty {
                Spacer()
            } else {
                List {
                    Section("Recent Channels") {
                        ForEach(recentChannels) { channel in
                            Button {
                                onSelect(channel)
                            } label: {
                                HStack(spacing: 12) {
                                    AsyncImage(url: channel.thumbnailURL) { image in
                                        image.resizable().aspectRatio(contentMode: .fill)
                                    } placeholder: {
                                        Circle().fill(Color.secondary.opacity(0.2))
                                    }
                                    .frame(width: 36, height: 36)
                                    .clipShape(Circle())

                                    Text(channel.title)
                                        .foregroundStyle(.primary)

                                    Spacer()
                                }
                            }
                        }
                        .onDelete(perform: removeRecent)
                    }
                }
                .listStyle(.plain)
            }
        }
    }

    private func removeRecent(at offsets: IndexSet) {
        for index in offsets {
            ChannelHistoryStore.remove(recentChannels[index])
        }
        recentChannels = ChannelHistoryStore.recent()
    }

    private func search() {
        errorMessage = nil
        isSearching = true
        Task {
            do {
                let channel = try await YouTubeAPIService.shared.resolveChannel(query: query)
                isSearching = false
                onSelect(channel)
            } catch {
                isSearching = false
                errorMessage = error.localizedDescription
            }
        }
    }
}
