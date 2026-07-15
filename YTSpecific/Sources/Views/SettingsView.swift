import SwiftUI

struct SettingsView: View {
    var onOrderChange: () -> Void

    @Environment(\.dismiss) private var dismiss
    @AppStorage("YTSpecific.playbackOrder") private var playbackOrderRaw: String = PlaybackOrder.newestFirst.rawValue
    @State private var apiKeyInput: String = APIKeyStore.load() ?? ""
    @State private var savedConfirmation = false

    var body: some View {
        NavigationStack {
            Form {
                Section("Playback Order") {
                    Picker("Order", selection: $playbackOrderRaw) {
                        ForEach(PlaybackOrder.allCases) { order in
                            Text(order.displayName).tag(order.rawValue)
                        }
                    }
                    .pickerStyle(.inline)
                    .onChange(of: playbackOrderRaw) {
                        onOrderChange()
                    }
                }

                Section {
                    SecureField("YouTube Data API Key", text: $apiKeyInput)
                        .autocorrectionDisabled()
                        .textInputAutocapitalization(.never)
                    Button("Save Key") {
                        APIKeyStore.save(apiKeyInput.trimmingCharacters(in: .whitespacesAndNewlines))
                        savedConfirmation = true
                    }
                    .disabled(apiKeyInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                    if savedConfirmation {
                        Text("Saved to the device Keychain.")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                } header: {
                    Text("YouTube Data API Key")
                } footer: {
                    Text("Create a free key in Google Cloud Console (YouTube Data API v3) and paste it here. It's stored only in this device's Keychain and used solely to look up channels and video lists.")
                }
            }
            .navigationTitle("Settings")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }
}
