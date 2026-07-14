import SwiftUI
import SwiftData

struct LikedVideosView: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \LikedVideoRecord.likedAt, order: .reverse) private var liked: [LikedVideoRecord]

    var body: some View {
        NavigationStack {
            Group {
                if liked.isEmpty {
                    ContentUnavailableView("No liked videos", systemImage: "heart", description: Text("Videos you like stay private to this app — they're never sent to YouTube."))
                } else {
                    List {
                        ForEach(liked) { record in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(record.title)
                                    .font(.subheadline)
                                Text(record.channelTitle)
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                        }
                        .onDelete(perform: unlike)
                    }
                }
            }
            .navigationTitle("Liked")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }

    private func unlike(at offsets: IndexSet) {
        for index in offsets {
            modelContext.delete(liked[index])
        }
        try? modelContext.save()
    }
}
