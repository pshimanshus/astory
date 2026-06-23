from dataclasses import dataclass
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Optional, Sequence, Tuple, Union


@dataclass(frozen=True)
class OcrLine:
    text: str
    box: Tuple[float, float, float, float]
    confidence: float


@dataclass(frozen=True)
class OcrResult:
    engine: str
    status: str
    full_text: str
    mean_confidence: Optional[float]
    lines: Tuple[OcrLine, ...]
    fallback_engine: Optional[str] = None
    confidence_calibrated: bool = True
    error: Optional[str] = None


@dataclass(frozen=True)
class FixtureOcrEngine:
    fixtures: Mapping[str, Sequence[OcrLine]]
    engine_name: str = "fixture"
    is_vlm_fallback: bool = False

    def recognize(self, media_path: Union[str, Path]) -> Tuple[OcrLine, ...]:
        path = Path(media_path)
        lines = self.fixtures.get(str(path))
        if lines is None:
            lines = self.fixtures.get(path.name, ())
        return tuple(lines)


class RapidOcrEngine:
    engine_name = "rapidocr"
    is_vlm_fallback = False

    def __init__(self):
        try:
            from rapidocr_onnxruntime import RapidOCR
        except ImportError as exc:
            raise RuntimeError("rapidocr_onnxruntime is not installed") from exc
        self._ocr = RapidOCR()

    def recognize(self, media_path: Union[str, Path]) -> Tuple[OcrLine, ...]:
        result, _elapsed = self._ocr(str(media_path))
        lines = []
        for item in result or []:
            if len(item) < 3:
                continue
            polygon, text, confidence = item[:3]
            lines.append(
                OcrLine(
                    text=str(text),
                    box=_bbox_from_polygon(polygon),
                    confidence=float(confidence),
                )
            )
        return tuple(lines)


def run_ocr(
    media_path: Union[str, Path],
    engine: FixtureOcrEngine,
    *,
    likely_text: bool = True,
    min_confidence: float = 0.80,
) -> OcrResult:
    fallback_engine = engine.engine_name if engine.is_vlm_fallback else None
    confidence_calibrated = not engine.is_vlm_fallback

    try:
        lines = engine.recognize(media_path)
    except Exception as exc:
        return OcrResult(
            engine=engine.engine_name,
            status="failed",
            full_text="",
            mean_confidence=None,
            lines=(),
            fallback_engine=fallback_engine,
            confidence_calibrated=confidence_calibrated,
            error=str(exc),
        )

    full_text = "\n".join(line.text for line in lines if line.text.strip())
    mean_confidence = _mean_confidence(lines)
    status = _status_for(full_text, mean_confidence, likely_text, min_confidence)

    return OcrResult(
        engine=engine.engine_name,
        status=status,
        full_text=full_text,
        mean_confidence=mean_confidence,
        lines=lines,
        fallback_engine=fallback_engine,
        confidence_calibrated=confidence_calibrated,
    )


def _mean_confidence(lines: Sequence[OcrLine]) -> Optional[float]:
    if not lines:
        return None
    return sum(line.confidence for line in lines) / len(lines)


def _status_for(
    full_text: str,
    mean_confidence: Optional[float],
    likely_text: bool,
    min_confidence: float,
) -> str:
    if not full_text:
        return "failed" if likely_text else "accepted"
    if mean_confidence is None or mean_confidence < min_confidence:
        return "needs_review"
    return "accepted"


def run_ocr_for_media_files(conn, engine=None, *, min_confidence: float = 0.80) -> dict:
    engine = engine or RapidOcrEngine()
    rows = conn.execute(
        """
        SELECT a.asset_id, mf.local_path
        FROM media_files mf
        JOIN assets a ON a.media_file_id = mf.media_file_id
        WHERE mf.local_path IS NOT NULL
        ORDER BY a.post_id, a.asset_index
        """
    ).fetchall()
    attempted = 0
    accepted = 0
    needs_review = 0
    failed = 0
    now = _utc_now()
    for row in rows:
        asset_id = row["asset_id"] if hasattr(row, "keys") else row[0]
        local_path = row["local_path"] if hasattr(row, "keys") else row[1]
        result = run_ocr(local_path, engine, min_confidence=min_confidence)
        attempted += 1
        if result.status == "accepted":
            accepted += 1
        elif result.status == "needs_review":
            needs_review += 1
        else:
            failed += 1
        conn.execute(
            """
            INSERT OR REPLACE INTO ocr_results(
                ocr_result_id, asset_id, engine, status, full_text,
                mean_confidence, lines_json, created_at, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"{asset_id}_{result.engine}",
                asset_id,
                result.engine,
                result.status,
                result.full_text,
                result.mean_confidence,
                json.dumps(
                    [
                        {
                            "text": line.text,
                            "box": list(line.box),
                            "confidence": line.confidence,
                        }
                        for line in result.lines
                    ],
                    sort_keys=True,
                ),
                now,
                json.dumps(
                    {
                        "fallback_engine": result.fallback_engine,
                        "confidence_calibrated": result.confidence_calibrated,
                        "error": result.error,
                    },
                    sort_keys=True,
                ),
            ),
        )
    conn.commit()
    return {
        "attempted": attempted,
        "accepted": accepted,
        "needs_review": needs_review,
        "failed": failed,
    }


def _bbox_from_polygon(polygon) -> Tuple[float, float, float, float]:
    points = []
    for point in polygon or []:
        if isinstance(point, (list, tuple)) and len(point) >= 2:
            points.append((float(point[0]), float(point[1])))
    if not points:
        return (0.0, 0.0, 0.0, 0.0)
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return (min(xs), min(ys), max(xs), max(ys))


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
