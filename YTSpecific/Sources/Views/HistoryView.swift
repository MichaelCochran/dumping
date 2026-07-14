import SwiftUI
import SwiftData

struct HistoryView: View {
    @Environment(\.dismiss) private var dismiss
    @Query(sort: \WatchedVideoRecord.watchedAt, order: .reverse) private var history: [WatchedVideoRecord]

    var body: some View {
        NavigationStack {
            Group {
                if history.isEmpty {
                    ContentUnavailableView("No history yet", systemImage: "clock", description: Text("Videos you watch will show up here."))
                } else {
                    List(history) { record in
                        VStack(alignment: .leading, spacing: 4) {
                            Text(record.title)
                                .font(.subheadline)
                            Text("\(record.channelTitle) \u{00B7} \(record.watchedAt.formatted(date: .abbreviated, time: .shortened))")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
            }
            .navigationTitle("History")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }
}
