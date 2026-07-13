#!/usr/bin/env swift

// Validate promotion configuration files.
//
// Run from the app-config repository root:
//   swift tools/validate_promotion_json.swift
//
// Validate another file:
//   swift tools/validate_promotion_json.swift path/to/promotion.json

import Foundation

private struct Configuration: Decodable {
    let promotions: [Promotion]
}

private struct Promotion: Decodable {
    let id: String
    let salt: String
    let codeHash: String
    let isEnabled: Bool
    let targets: [String]
    let startAt: String?
    let endAt: String?
    let entitlementDays: Int?
}

private enum ValidationError: Error, CustomStringConvertible {
    case invalid(String)

    var description: String {
        switch self {
        case .invalid(let message):
            return message
        }
    }
}

private func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data("Validation failed: \(message)\n".utf8))
    exit(1)
}

private func normalized(_ value: String?) -> String? {
    guard let value else {
        return nil
    }
    let result = value.trimmingCharacters(in: .whitespacesAndNewlines)
    return result.isEmpty ? nil : result
}

private func parseDate(_ value: String?, field: String, promotionID: String) throws -> Date? {
    guard let value = normalized(value) else {
        return nil
    }

    let formatter = DateFormatter()
    formatter.calendar = Calendar(identifier: .gregorian)
    formatter.locale = Locale(identifier: "en_US_POSIX")
    formatter.timeZone = TimeZone(secondsFromGMT: 0)
    formatter.dateFormat = "yyyy-MM-dd"
    formatter.isLenient = false

    guard let date = formatter.date(from: value), formatter.string(from: date) == value else {
        throw ValidationError.invalid("promotion '\(promotionID)' has invalid \(field) '\(value)'; expected yyyy-MM-dd")
    }
    return date
}

let arguments = CommandLine.arguments
guard arguments.count <= 2 else {
    fail("Usage: swift tools/validate_promotion_json.swift [path]")
}

let path = arguments.count == 2 ? arguments[1] : "promotion.json"

do {
    let data = try Data(contentsOf: URL(fileURLWithPath: path))
    let configuration = try JSONDecoder().decode(Configuration.self, from: data)
    guard !configuration.promotions.isEmpty else {
        throw ValidationError.invalid("promotions must contain at least one item")
    }

    var promotionIDs = Set<String>()
    for (index, promotion) in configuration.promotions.enumerated() {
        let id = promotion.id.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !id.isEmpty else {
            throw ValidationError.invalid("promotions[\(index)].id cannot be empty")
        }
        guard promotionIDs.insert(id).inserted else {
            throw ValidationError.invalid("duplicate promotion id '\(id)'")
        }
        guard let salt = Data(base64Encoded: promotion.salt), !salt.isEmpty else {
            throw ValidationError.invalid("promotion '\(id)' has an invalid or empty Base64 salt")
        }
        guard let codeHash = Data(base64Encoded: promotion.codeHash), codeHash.count == 32 else {
            throw ValidationError.invalid("promotion '\(id)' codeHash must be a 32-byte SHA-256 value encoded as Base64")
        }
        guard !promotion.targets.isEmpty,
              promotion.targets.allSatisfy({ !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }) else {
            throw ValidationError.invalid("promotion '\(id)' targets must contain at least one non-empty app id or '*'")
        }

        let startAt = try parseDate(promotion.startAt, field: "startAt", promotionID: id)
        let endAt = try parseDate(promotion.endAt, field: "endAt", promotionID: id)
        if let startAt, let endAt, startAt > endAt {
            throw ValidationError.invalid("promotion '\(id)' startAt must not be later than endAt")
        }
        if let entitlementDays = promotion.entitlementDays, entitlementDays <= 0 {
            throw ValidationError.invalid("promotion '\(id)' entitlementDays must be greater than 0 when set")
        }
    }

    print("Valid promotion configuration: \(path) (\(configuration.promotions.count) promotion(s))")
} catch let error as DecodingError {
    fail("invalid JSON structure: \(error)")
} catch let error as ValidationError {
    fail(error.description)
} catch {
    fail(error.localizedDescription)
}
