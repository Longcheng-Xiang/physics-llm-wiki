// Package the user-approved first generated italic psi image without redrawing it.
// Run on macOS: swift viewer/desktop/icons/generate.swift
import AppKit
import Foundation

let folder = URL(fileURLWithPath: #filePath).deletingLastPathComponent()
let source = NSImage(contentsOf: folder.appendingPathComponent("italic-psi-original.png"))!
let original = source.cgImage(forProposedRect: nil, context: nil, hints: nil)!
let web = folder.deletingLastPathComponent().deletingLastPathComponent().appendingPathComponent("frontend/public")

func png(_ size: Int, native: Bool = true) -> Data {
    let c = CGContext(data: nil, width: size, height: size, bitsPerComponent: 8, bytesPerRow: 0,
        space: CGColorSpace(name: CGColorSpace.sRGB)!, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    c.interpolationQuality = .high
    c.scaleBy(x: CGFloat(size) / 1024, y: CGFloat(size) / 1024)
    if native {
        // Standard app-icon inset. The approved image is only scaled, not sheared.
        c.translateBy(x: 72, y: 72); c.scaleBy(x: 880.0 / 1024, y: 880.0 / 1024)
    }
    c.addPath(CGPath(roundedRect: CGRect(x: 0, y: 0, width: 1024, height: 1024),
        cornerWidth: 242, cornerHeight: 242, transform: nil))
    c.clip()
    c.draw(original, in: CGRect(x: 0, y: 0, width: 1024, height: 1024))
    return NSBitmapImageRep(cgImage: c.makeImage()!).representation(using: .png, properties: [:])!
}
try png(256, native: false).write(to: web.appendingPathComponent("brand-mark.png"))
try png(64, native: false).write(to: web.appendingPathComponent("favicon.png"))
let iconset = folder.appendingPathComponent("PhysicsWiki.iconset")
try FileManager.default.createDirectory(at: iconset, withIntermediateDirectories: true)
for size in [16, 32, 128, 256, 512] {
    try png(size).write(to: iconset.appendingPathComponent("icon_\(size)x\(size).png"))
    try png(size * 2).write(to: iconset.appendingPathComponent("icon_\(size)x\(size)@2x.png"))
}
try png(256).write(to: folder.appendingPathComponent("preview.png"))
// ICO supports embedded PNG images on supported Windows versions.
func u16(_ value: Int) -> Data { var n = UInt16(value).littleEndian; return withUnsafeBytes(of: &n) { Data($0) } }
func u32(_ value: Int) -> Data { var n = UInt32(value).littleEndian; return withUnsafeBytes(of: &n) { Data($0) } }
let sizes = [16, 24, 32, 48, 64, 128, 256]
let images = sizes.map { png($0) }
var ico = u16(0) + u16(1) + u16(sizes.count)
var offset = 6 + sizes.count * 16
for (index, size) in sizes.enumerated() {
    ico += Data([UInt8(size == 256 ? 0 : size), UInt8(size == 256 ? 0 : size), 0, 0])
    ico += u16(1) + u16(32) + u32(images[index].count) + u32(offset)
    offset += images[index].count
}
for data in images { ico += data }
try ico.write(to: folder.appendingPathComponent("PhysicsWiki.ico"))
