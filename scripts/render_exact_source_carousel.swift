import AppKit
import Foundation

struct SlideMap: Decodable {
    let slides: [Slide]
    let excludedFromRender: [Excluded]?

    enum CodingKeys: String, CodingKey {
        case slides
        case excludedFromRender = "excluded_from_render"
    }
}

struct Excluded: Codable {
    let slide: Int
    let reason: String
}

struct Slide: Decodable {
    let slide: Int
    let sourceImage: String?
    let text: String?
    let segments: [Segment]?

    enum CodingKeys: String, CodingKey {
        case slide
        case sourceImage = "source_image"
        case text
        case segments
    }
}

struct Segment: Decodable {
    let text: String
    let italic: Bool
}

let repoRoot = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let runId = "2026-06-14_17-51_ig-reference-concept"
let runRoot = repoRoot.appendingPathComponent("runs/\(runId)")
let mapURL = runRoot.appendingPathComponent("planning/exact_source_slide_map.json")
let outputDir = runRoot.appendingPathComponent("corrected-exact-source-carousel")
try FileManager.default.createDirectory(at: outputDir, withIntermediateDirectories: true)

let data = try Data(contentsOf: mapURL)
let decoder = JSONDecoder()
let slideMap = try decoder.decode(SlideMap.self, from: data)

let width = 1080
let height = 1350
let canvas = NSRect(x: 0, y: 0, width: width, height: height)

func font(_ size: CGFloat, italic: Bool = false, weight: NSFont.Weight = .semibold) -> NSFont {
    if italic {
        return NSFontManager.shared.convert(font(size, italic: false, weight: weight), toHaveTrait: .italicFontMask)
    }
    if let newYork = NSFont(name: "NewYork", size: size) {
        return newYork
    }
    if let baskerville = NSFont(name: "Baskerville", size: size) {
        return baskerville
    }
    return NSFont.systemFont(ofSize: size, weight: weight)
}

func scriptFont(_ size: CGFloat) -> NSFont {
    for name in ["Bradley Hand Bold", "Bradley Hand ITC", "Apple Chancery", "Marker Felt"] {
        if let candidate = NSFont(name: name, size: size) {
            return candidate
        }
    }
    return NSFont.systemFont(ofSize: size, weight: .regular)
}

func textSize(for count: Int) -> CGFloat {
    if count > 150 { return 54 }
    if count > 105 { return 62 }
    if count > 72 { return 70 }
    return 76
}

func drawBackground() {
    NSColor(calibratedRed: 0.965, green: 0.943, blue: 0.902, alpha: 1).setFill()
    canvas.fill()

    let washColors: [(NSColor, NSRect)] = [
        (NSColor(calibratedRed: 0.52, green: 0.65, blue: 0.55, alpha: 0.16), NSRect(x: 40, y: 86, width: 360, height: 230)),
        (NSColor(calibratedRed: 0.73, green: 0.58, blue: 0.44, alpha: 0.14), NSRect(x: 598, y: 100, width: 360, height: 250)),
        (NSColor(calibratedRed: 0.45, green: 0.55, blue: 0.68, alpha: 0.10), NSRect(x: 310, y: 136, width: 420, height: 190))
    ]

    for (color, rect) in washColors {
        color.setFill()
        let path = NSBezierPath(ovalIn: rect)
        path.fill()
    }

    NSColor(calibratedWhite: 0.10, alpha: 0.045).setStroke()
    for y in stride(from: 0, through: height, by: 7) {
        let p = NSBezierPath()
        p.move(to: NSPoint(x: 0, y: y))
        p.line(to: NSPoint(x: width, y: y))
        p.lineWidth = 0.5
        p.stroke()
    }
    for x in stride(from: 0, through: width, by: 9) {
        let p = NSBezierPath()
        p.move(to: NSPoint(x: x, y: 0))
        p.line(to: NSPoint(x: x, y: height))
        p.lineWidth = 0.35
        p.stroke()
    }
}

func drawLinework() {
    NSColor(calibratedWhite: 0.14, alpha: 0.22).setStroke()
    let base = NSBezierPath()
    base.move(to: NSPoint(x: 90, y: 118))
    base.curve(to: NSPoint(x: 990, y: 120), controlPoint1: NSPoint(x: 338, y: 96), controlPoint2: NSPoint(x: 710, y: 143))
    base.lineWidth = 2.0
    base.stroke()

    for (x, w, h, tilt) in [(170.0, 238.0, 120.0, -8.0), (650.0, 230.0, 118.0, 7.0)] {
        let path = NSBezierPath()
        path.move(to: NSPoint(x: x, y: 120))
        path.curve(to: NSPoint(x: x + w, y: 120),
                   controlPoint1: NSPoint(x: x + w * 0.22, y: 40 + tilt),
                   controlPoint2: NSPoint(x: x + w * 0.78, y: 40 - tilt))
        path.curve(to: NSPoint(x: x, y: 120),
                   controlPoint1: NSPoint(x: x + w * 0.82, y: 120 + h * 0.20),
                   controlPoint2: NSPoint(x: x + w * 0.18, y: 120 + h * 0.18))
        path.lineWidth = 1.4
        path.stroke()
    }
}

func attributedText(for slide: Slide, baseSize: CGFloat) -> NSAttributedString {
    let paragraph = NSMutableParagraphStyle()
    paragraph.alignment = .center
    paragraph.lineSpacing = baseSize * 0.08
    paragraph.paragraphSpacing = baseSize * 0.18

    let result = NSMutableAttributedString()
    for segment in slide.segments ?? [] {
        let attrs: [NSAttributedString.Key: Any] = [
            .font: font(baseSize, italic: segment.italic),
            .foregroundColor: NSColor(calibratedWhite: 0.13, alpha: 1),
            .paragraphStyle: paragraph,
            .kern: 0
        ]
        result.append(NSAttributedString(string: segment.text, attributes: attrs))
    }
    return result
}

func drawCentered(_ attributed: NSAttributedString, baseRect: NSRect) {
    let measured = attributed.boundingRect(with: baseRect.size, options: [.usesLineFragmentOrigin, .usesFontLeading])
    let y = baseRect.midY - measured.height / 2
    let rect = NSRect(x: baseRect.minX, y: y, width: baseRect.width, height: measured.height + 20)
    attributed.draw(with: rect, options: [.usesLineFragmentOrigin, .usesFontLeading])
}

var manifestSlides: [[String: Any]] = []

for slide in slideMap.slides where slide.slide <= 18 {
    guard let text = slide.text else { continue }
    let image = NSImage(size: NSSize(width: width, height: height))
    image.lockFocus()

    drawBackground()
    drawLinework()

    let brandAttrs: [NSAttributedString.Key: Any] = [
        .font: scriptFont(30),
        .foregroundColor: NSColor(calibratedWhite: 0.12, alpha: 0.72)
    ]
    let brand = "@a.storyof.two" as NSString
    brand.draw(at: NSPoint(x: 842, y: 1284), withAttributes: brandAttrs)

    let baseSize = textSize(for: text.count)
    let textRect = NSRect(x: 108, y: 355, width: 864, height: 760)
    drawCentered(attributedText(for: slide, baseSize: baseSize), baseRect: textRect)

    let footerAttrs: [NSAttributedString.Key: Any] = [
        .font: scriptFont(26),
        .foregroundColor: NSColor(calibratedWhite: 0.12, alpha: 0.40)
    ]
    let footer = "a story of two" as NSString
    let footerSize = footer.size(withAttributes: footerAttrs)
    footer.draw(at: NSPoint(x: CGFloat(width) / 2 - footerSize.width / 2, y: 44), withAttributes: footerAttrs)

    image.unlockFocus()

    guard let tiff = image.tiffRepresentation,
          let bitmap = NSBitmapImageRep(data: tiff),
          let png = bitmap.representation(using: .png, properties: [:]) else {
        throw NSError(domain: "render", code: 1, userInfo: [NSLocalizedDescriptionKey: "Failed to encode slide \(slide.slide)"])
    }

    let fileName = "slide-\(String(format: "%02d", slide.slide)).png"
    try png.write(to: outputDir.appendingPathComponent(fileName))
    manifestSlides.append([
        "slide": slide.slide,
        "file": fileName,
        "source_image": slide.sourceImage ?? "",
        "on_image_text": text,
        "pixel_width": width,
        "pixel_height": height
    ])
}

let manifest: [String: Any] = [
    "schema_version": "1.0",
    "run_id": runId,
    "created_at": ISO8601DateFormatter().string(from: Date()),
    "correction": "Exact source text rendered deterministically in A Story visual/design theme. Previous invented variant package remains rejected.",
    "format": ["pixel_width": width, "pixel_height": height],
    "rendered_slide_count": manifestSlides.count,
    "slides": manifestSlides,
    "excluded_source_slides": slideMap.excludedFromRender?.map { ["slide": $0.slide, "reason": $0.reason] } ?? []
]

let manifestData = try JSONSerialization.data(withJSONObject: manifest, options: [.prettyPrinted, .sortedKeys])
try manifestData.write(to: outputDir.appendingPathComponent("manifest.json"))

print("Rendered \(manifestSlides.count) slides to \(outputDir.path)")
