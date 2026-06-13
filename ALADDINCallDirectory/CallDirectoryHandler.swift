import CallKit
import Foundation

final class CallDirectoryHandler: CXCallDirectoryProvider {

    override func beginRequest(with context: CXCallDirectoryExtensionContext) {
        context.delegate = self
        let snapshot = AntifakeCallDirectoryStore.load()

        for entry in snapshot.blockedNumbers.sorted() {
            context.addBlockingEntry(withNextSequentialPhoneNumber: entry)
        }

        for entry in snapshot.identifiedNumbers.sorted(by: { $0.phoneNumber < $1.phoneNumber }) {
            context.addIdentificationEntry(
                withNextSequentialPhoneNumber: entry.phoneNumber,
                label: entry.label
            )
        }

        context.completeRequest()
    }
}

extension CallDirectoryHandler: CXCallDirectoryExtensionContextDelegate {
    func requestFailed(for extensionContext: CXCallDirectoryExtensionContext, withError error: Error) {
        extensionContext.cancelRequest(withError: error)
    }
}
