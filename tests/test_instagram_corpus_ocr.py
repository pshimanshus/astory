import tempfile
import unittest
import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

from scripts.instagram_corpus.ocr import (
    FixtureOcrEngine,
    OcrLine,
    OcrResult,
    RapidOcrEngine,
    run_ocr,
)


class InstagramCorpusOcrTests(unittest.TestCase):
    def test_fixture_engine_returns_accepted_ocr_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "slide.jpg"
            image_path.write_bytes(b"not real image bytes")
            engine = FixtureOcrEngine(
                {
                    str(image_path): [
                        OcrLine(text="You saved the last bite", box=(10, 20, 300, 60), confidence=0.95),
                        OcrLine(text="and called it love", box=(10, 70, 260, 110), confidence=0.85),
                    ]
                }
            )

            result = run_ocr(image_path, engine)

            self.assertIsInstance(result, OcrResult)
            self.assertEqual(result.status, "accepted")
            self.assertEqual(result.engine, "fixture")
            self.assertEqual(result.full_text, "You saved the last bite\nand called it love")
            self.assertAlmostEqual(result.mean_confidence, 0.9)
            self.assertTrue(result.confidence_calibrated)
            self.assertEqual(result.lines[0].box, (10, 20, 300, 60))

    def test_low_confidence_text_needs_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "slide.jpg"
            image_path.write_bytes(b"not real image bytes")
            engine = FixtureOcrEngine(
                {str(image_path): [OcrLine(text="maybe text", box=(0, 0, 10, 10), confidence=0.41)]}
            )

            result = run_ocr(image_path, engine, min_confidence=0.75)

            self.assertEqual(result.status, "needs_review")
            self.assertEqual(result.full_text, "maybe text")
            self.assertAlmostEqual(result.mean_confidence, 0.41)

    def test_blank_likely_text_asset_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "slide.jpg"
            image_path.write_bytes(b"not real image bytes")
            engine = FixtureOcrEngine({str(image_path): []})

            result = run_ocr(image_path, engine, likely_text=True)

            self.assertEqual(result.status, "failed")
            self.assertEqual(result.full_text, "")
            self.assertIsNone(result.mean_confidence)

    def test_vlm_fallback_confidence_is_uncalibrated(self):
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "slide.jpg"
            image_path.write_bytes(b"not real image bytes")
            engine = FixtureOcrEngine(
                {str(image_path): [OcrLine(text="fallback read", box=(1, 2, 3, 4), confidence=0.88)]},
                engine_name="fixture-vlm",
                is_vlm_fallback=True,
            )

            result = run_ocr(image_path, engine)

            self.assertEqual(result.status, "accepted")
            self.assertEqual(result.fallback_engine, "fixture-vlm")
            self.assertFalse(result.confidence_calibrated)

    @unittest.skipUnless(
        importlib.util.find_spec("rapidocr_onnxruntime"),
        "rapidocr_onnxruntime is not installed",
    )
    def test_rapidocr_engine_reads_generated_image_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "slide.png"
            image = Image.new("RGB", (420, 120), "white")
            draw = ImageDraw.Draw(image)
            draw.text((20, 40), "hello love", fill="black")
            image.save(image_path)

            result = run_ocr(image_path, RapidOcrEngine(), min_confidence=0.5)

            self.assertEqual(result.status, "accepted")
            self.assertIn("hello", result.full_text.lower())
            self.assertTrue(result.lines)
            self.assertEqual(result.engine, "rapidocr")


if __name__ == "__main__":
    unittest.main()
