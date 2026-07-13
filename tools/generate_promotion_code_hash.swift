#!/usr/bin/env swift

// Promotion code hash generator
//
// Run these commands from the app-config repository root:
//
// 1. Generate a random 10-character code with a new random salt:
//    swift tools/generate_promotion_code_hash.swift
//
// 2. Generate the hash and a new random salt for a code you choose:
//    swift tools/generate_promotion_code_hash.swift Ab12X9
//
// 3. Recalculate a code hash with an existing Base64 salt:
//    swift tools/generate_promotion_code_hash.swift Ab12X9 TExnGcq1+TcVuLMPURcRkw==
//
// A code must contain 1-10 ASCII letters or digits and is case-sensitive.
// Give the printed "Promotion code" to users. Copy only "salt" and
// "codeHash" into promotion.json; never put the plaintext code in that file.

import CryptoKit
import Foundation

private func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data("\(message)\n".utf8))
    exit(1)
}

let arguments = CommandLine.arguments
guard arguments.count <= 3 else {
    fail("Usage: swift tools/generate_promotion_code_hash.swift [code] [base64-salt]")
}

let allowedCharacters = Array("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
let code: String
if arguments.count >= 2 {
    code = arguments[1].trimmingCharacters(in: .whitespacesAndNewlines)
} else {
    var generator = SystemRandomNumberGenerator()
    code = String((0..<10).map { _ in allowedCharacters.randomElement(using: &generator)! })
}

guard (1...10).contains(code.count),
      code.unicodeScalars.allSatisfy({ $0.isASCII && CharacterSet.alphanumerics.contains($0) }) else {
    fail("Promotion code must contain 1-10 ASCII letters or digits.")
}

let salt: Data
if arguments.count == 3 {
    guard let decodedSalt = Data(base64Encoded: arguments[2]), !decodedSalt.isEmpty else {
        fail("The optional salt must be non-empty Base64 data.")
    }
    salt = decodedSalt
} else {
    var generator = SystemRandomNumberGenerator()
    salt = Data((0..<16).map { _ in UInt8.random(in: .min ... .max, using: &generator) })
}

var payload = salt
payload.append(Data(code.utf8))
let codeHash = Data(SHA256.hash(data: payload))
let output = [
    "salt": salt.base64EncodedString(),
    "codeHash": codeHash.base64EncodedString()
]
let outputData = try JSONSerialization.data(withJSONObject: output, options: [.prettyPrinted, .sortedKeys])
print("Promotion code: \(code)")
print(String(decoding: outputData, as: UTF8.self))
