"""
Auto Sketch Drawer — Instagram DM Doodle Edition
==================================================
Converts any image (photo or illustration) into clean doodle-style outlines
and draws them on any canvas via mouse automation.

Optimised for the small, vertical Instagram Direct Message doodle canvas:
  • Aggressive downscaling and smoothing to eliminate clutter
  • Only major structural outlines are kept (no shading, no texture dots)
  • Paths are linked together and short fragments are discarded
  • Preview window lets you verify before drawing
"""

import argparse
import sys
import time
import threading
from dataclasses import dataclass
from typing import List, Tuple, Optional

import numpy as np
import cv2

# ---------------------------------------------------------------------------
# Optional dependency imports with friendly error handling
# ---------------------------------------------------------------------------
try:
    import pyautogui  # type: ignore
except Exception as exc:
    pyautogui = None  # type: ignore
    _pyautogui_err = exc
else:
    _pyautogui_err = None

try:
    import keyboard  # type: ignore
except Exception as exc:
    keyboard = None  # type: ignore
    _keyboard_err = exc
else:
    _keyboard_err = None

try:
    from skimage.morphology import skeletonize  # type: ignore
except Exception:
    skeletonize = None  # type: ignore

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------
Point = Tuple[int, int]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class CanvasRect:
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return max(0, self.x2 - self.x1)

    @property
    def height(self) -> int:
        return max(0, self.y2 - self.y1)


# ===================================================================
#  CLI
# ===================================================================
def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Instagram DM Doodle Drawer — convert any image to clean outline strokes"
    )
    p.add_argument("--image", required=True, help="Path to input image (photo or drawing)")
    p.add_argument("--detail", choices=["low", "med", "high"], default="med",
                   help="Outline detail level (low = minimal lines, high = more lines)")
    p.add_argument("--speed", type=float, default=1.0, help="Drawing speed multiplier")
    p.add_argument("--fit", choices=["contain", "fill"], default="contain",
                   help="How the image maps onto the canvas")
    p.add_argument("--invert", action="store_true",
                   help="Invert colours before edge detection (for dark backgrounds)")
    p.add_argument("--dry-run", action="store_true",
                   help="Compute paths without moving mouse")
    p.add_argument("--preview", action="store_true",
                   help="Show a preview window of the doodle before drawing")
    p.add_argument("--save-preview", type=str, default=None,
                   help="Save preview image to this path (e.g. preview.png)")
    # Advanced tuning
    p.add_argument("--max-stroke-len", type=int, default=800)
    p.add_argument("--pps", type=int, default=1200,
                   help="Points per second while drawing")
    p.add_argument("--min-path-len", type=int, default=25,
                   help="Discard paths shorter than this (in pixels)")
    p.add_argument("--spacing-px", type=int, default=2,
                   help="Max pixel gap between resampled points")
    p.add_argument("--drag-duration", type=float, default=0.0)
    p.add_argument("--use-move", action="store_true")
    p.add_argument("--max-dim", type=int, default=500,
                   help="Downscale image so longest side is at most this many pixels")
    p.add_argument("--link-dist", type=float, default=8.0,
                   help="Max pixel distance to link nearby path endpoints")
    return p.parse_args(argv)


# ===================================================================
#  IMAGE PROCESSING PIPELINE  —  Doodle Outline Extraction
# ===================================================================

def load_and_prepare(path: str, max_dim: int, invert: bool) -> np.ndarray:
    """Load image, downscale for the tiny IG canvas, convert to grayscale."""
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {path}")

    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / float(max(h, w))
        img = cv2.resize(img, (int(w * scale), int(h * scale)),
                         interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if invert:
        gray = cv2.bitwise_not(gray)
    return gray


def extract_doodle_edges(gray: np.ndarray, detail: str) -> np.ndarray:
    """
    Convert a grayscale image into clean doodle outlines.

    Pipeline:
      1. CLAHE contrast normalisation (handles dark / blown-out photos)
      2. Heavy bilateral + median blur to destroy texture & keep edges
      3. Canny edge detection with thresholds tuned per detail level
      4. Morphological close to bridge small gaps
      5. Remove tiny isolated blobs (area filter)
    """
    # --- 1. Normalise contrast so any photo looks similar ----------------
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    norm = clahe.apply(gray)

    # --- 2. Aggressive smoothing -----------------------------------------
    # Bilateral preserves strong edges while flattening gradients
    smooth = cv2.bilateralFilter(norm, d=9, sigmaColor=75, sigmaSpace=75)

    # Median blur destroys remaining texture (hair, fabric, skin pores …)
    if detail == "high":
        median_k = 7
    elif detail == "med":
        median_k = 11
    else:
        median_k = 15
    smooth = cv2.medianBlur(smooth, median_k)

    # --- 3. Canny with detail-dependent thresholds -----------------------
    # Higher thresholds → fewer, bolder lines
    if detail == "high":
        canny_lo, canny_hi = 30, 80
    elif detail == "med":
        canny_lo, canny_hi = 50, 120
    else:
        canny_lo, canny_hi = 80, 160

    edges = cv2.Canny(smooth, canny_lo, canny_hi)

    # --- 4. Close small gaps so outlines stay continuous ------------------
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # --- 5. Remove tiny isolated blobs (noise dots) ----------------------
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(edges, connectivity=8)
    min_area = 30 if detail == "high" else 50 if detail == "med" else 80
    clean = np.zeros_like(edges)
    for i in range(1, n_labels):  # skip background label 0
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            clean[labels == i] = 255

    return clean


def thin_edges(edge_img: np.ndarray) -> np.ndarray:
    """Thin edges to 1-pixel-wide skeleton for single-stroke drawing."""
    if skeletonize is not None:
        skel = skeletonize(edge_img > 0)
        return (skel.astype(np.uint8)) * 255
    # Fallback morphological thinning
    kernel = np.ones((3, 3), np.uint8)
    return cv2.morphologyEx(edge_img, cv2.MORPH_OPEN, kernel, iterations=1)


# ===================================================================
#  PATH EXTRACTION & OPTIMISATION
# ===================================================================

def extract_polylines(edge_img: np.ndarray, min_len: int) -> List[np.ndarray]:
    """Find contours and discard anything shorter than min_len."""
    contours, _ = cv2.findContours(edge_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    polylines: List[np.ndarray] = []
    for cnt in contours:
        if cnt is None or len(cnt) < min_len:
            continue
        pts = cnt.squeeze(1)
        if pts.ndim != 2 or pts.shape[0] < min_len:
            continue
        polylines.append(pts.astype(np.int32))
    return polylines


def order_paths(polylines: List[np.ndarray]) -> List[np.ndarray]:
    """Sort paths top-to-bottom, left-to-right to minimise pen-lift travel."""
    def key(arr: np.ndarray) -> Tuple[int, int]:
        return (int(arr[0][1]), int(arr[0][0]))
    return sorted(polylines, key=key)


def link_close_paths(polylines: List[np.ndarray],
                     max_dist: float = 8.0) -> List[np.ndarray]:
    """
    Greedily merge paths whose endpoints are within max_dist pixels.
    Reduces the number of pen-lifts on the IG canvas dramatically.
    Has a hard safety cap so it never freezes on noisy images.
    """
    if not polylines or len(polylines) > 1500:
        return polylines          # safety: too many paths → skip linking

    paths = list(polylines)
    linked: List[np.ndarray] = []

    while paths:
        curr = paths.pop()
        changed = True
        while changed:
            changed = False
            best_i = -1
            best_d = max_dist + 1.0
            best_how = ""

            cs, ce = curr[0], curr[-1]
            for i, p in enumerate(paths):
                ps, pe = p[0], p[-1]
                d_es = abs(int(ce[0]) - int(ps[0])) + abs(int(ce[1]) - int(ps[1]))
                if d_es <= best_d:
                    best_d, best_i, best_how = d_es, i, "es"
                d_ee = abs(int(ce[0]) - int(pe[0])) + abs(int(ce[1]) - int(pe[1]))
                if d_ee < best_d:
                    best_d, best_i, best_how = d_ee, i, "ee"
                d_ss = abs(int(cs[0]) - int(ps[0])) + abs(int(cs[1]) - int(ps[1]))
                if d_ss < best_d:
                    best_d, best_i, best_how = d_ss, i, "ss"
                d_se = abs(int(cs[0]) - int(pe[0])) + abs(int(cs[1]) - int(pe[1]))
                if d_se < best_d:
                    best_d, best_i, best_how = d_se, i, "se"

            if best_i >= 0 and best_d <= max_dist * 1.42:
                # 1.42 ≈ √2 to convert Manhattan → approx Euclidean guard
                p = paths.pop(best_i)
                if best_how == "es":
                    curr = np.vstack((curr, p))
                elif best_how == "ee":
                    curr = np.vstack((curr, p[::-1]))
                elif best_how == "ss":
                    curr = np.vstack((p[::-1], curr))
                else:
                    curr = np.vstack((p, curr))
                changed = True

        linked.append(curr)
    return linked


def split_long_paths(path: np.ndarray, max_pts: int) -> List[np.ndarray]:
    if len(path) <= max_pts:
        return [path]
    return [path[i:i + max_pts] for i in range(0, len(path), max_pts)
            if len(path[i:i + max_pts]) >= 2]


# ===================================================================
#  COORDINATE MAPPING & RESAMPLING
# ===================================================================

def compute_fit(src_w: int, src_h: int,
                rect: CanvasRect, mode: str) -> Tuple[float, float, float, float]:
    if mode == "fill":
        sx = rect.width / max(1.0, float(src_w))
        sy = rect.height / max(1.0, float(src_h))
        return sx, sy, float(rect.x1), float(rect.y1)
    scale = min(rect.width / max(1.0, float(src_w)),
                rect.height / max(1.0, float(src_h)))
    ow = rect.x1 + (rect.width - scale * src_w) / 2.0
    oh = rect.y1 + (rect.height - scale * src_h) / 2.0
    return scale, scale, ow, oh


def map_pt(ix: int, iy: int,
           sx: float, sy: float, ox: float, oy: float) -> Point:
    return (int(round(ox + ix * sx)), int(round(oy + iy * sy)))


def resample(points: List[Point], max_step: int) -> List[Point]:
    """Ensure consecutive points are at most max_step px apart."""
    if not points:
        return []
    step = max(1, int(max_step))
    out: List[Point] = [points[0]]
    px, py = points[0]
    for cx, cy in points[1:]:
        dx, dy = cx - px, cy - py
        dist = max(abs(dx), abs(dy)) if (dx == 0 or dy == 0) else int(np.hypot(dx, dy))
        if dist <= step:
            if out[-1] != (cx, cy):
                out.append((cx, cy))
        else:
            n = max(1, int(np.ceil(dist / float(step))))
            for s in range(1, n + 1):
                t = s / float(n)
                nx = int(round(px + t * dx))
                ny = int(round(py + t * dy))
                if out[-1] != (nx, ny):
                    out.append((nx, ny))
        px, py = cx, cy
    if len(out) == 1 and out[0] != points[-1]:
        out.append(points[-1])
    return out


# ===================================================================
#  CALIBRATION & DRAWING CONTROL
# ===================================================================

class Calibrator:
    def __init__(self) -> None:
        self.tl: Optional[Point] = None
        self.br: Optional[Point] = None
        self.confirmed = False
        self._lock = threading.Lock()

    def _set_tl(self) -> None:
        if pyautogui:
            pos = pyautogui.position()
            with self._lock:
                self.tl = (int(pos.x), int(pos.y))

    def _set_br(self) -> None:
        if pyautogui:
            pos = pyautogui.position()
            with self._lock:
                self.br = (int(pos.x), int(pos.y))

    def _confirm(self) -> None:
        with self._lock:
            self.confirmed = True

    def run(self) -> CanvasRect:
        if keyboard is None:
            raise RuntimeError("keyboard module not available")
        print("Bring your drawing app to front, select your brush and color.")
        print("Hover mouse over TOP-LEFT of the canvas and press F8.")
        print("Hover mouse over BOTTOM-RIGHT of the canvas and press F9.")
        print("Press F10 to confirm. Press ESC to cancel.")

        keyboard.add_hotkey("f8", self._set_tl)
        keyboard.add_hotkey("f9", self._set_br)
        keyboard.add_hotkey("f10", self._confirm)
        try:
            while True:
                if keyboard.is_pressed("esc"):
                    raise KeyboardInterrupt
                with self._lock:
                    tl, br, ok = self.tl, self.br, self.confirmed
                print(f"[Calibrate] TL={tl} BR={br}    ", end="\r", flush=True)
                if ok and tl and br:
                    x1, y1 = tl
                    x2, y2 = br
                    if x1 > x2: x1, x2 = x2, x1
                    if y1 > y2: y1, y2 = y2, y1
                    print()
                    return CanvasRect(x1, y1, x2, y2)
                time.sleep(0.05)
        finally:
            for k in ("f8", "f9", "f10"):
                try:
                    keyboard.remove_hotkey(k)
                except Exception:
                    pass


class DrawController:
    def __init__(self) -> None:
        self.paused = False
        self.aborted = False

    def install(self) -> None:
        if keyboard is None:
            return
        keyboard.add_hotkey("f6", self._pause)
        keyboard.add_hotkey("f7", self._abort)

    def uninstall(self) -> None:
        if keyboard is None:
            return
        for k in ("f6", "f7"):
            try:
                keyboard.remove_hotkey(k)
            except Exception:
                pass

    def _pause(self) -> None:
        self.paused = not self.paused
        print(f"[Control] Paused={self.paused}")

    def _abort(self) -> None:
        self.aborted = True
        print("[Control] Abort requested")


# ===================================================================
#  PREVIEW
# ===================================================================

def preview_paths(gray: np.ndarray, polylines: List[np.ndarray],
                  save_path: Optional[str] = None) -> None:
    """Show (and optionally save) a black-on-white preview of the doodle."""
    h, w = gray.shape[:2]
    canvas = np.ones((h, w), dtype=np.uint8) * 255   # white background
    for pts in polylines:
        for i in range(1, len(pts)):
            cv2.line(canvas,
                     (int(pts[i - 1][0]), int(pts[i - 1][1])),
                     (int(pts[i][0]), int(pts[i][1])),
                     0, 1, cv2.LINE_AA)
    if save_path:
        cv2.imwrite(save_path, canvas)
        print(f"Preview saved to {save_path}")
    cv2.imshow("Doodle Preview", canvas)
    print("Close the preview window or press any key to continue…")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# ===================================================================
#  DRAWING ENGINE
# ===================================================================

def draw_on_canvas(polylines: List[np.ndarray], img_shape: Tuple[int, int],
                   rect: CanvasRect, fit_mode: str, pps: int, speed: float,
                   max_stroke_len: int, ctrl: DrawController, dry_run: bool,
                   spacing_px: int, drag_dur: float, use_move: bool) -> None:
    if pyautogui is None and not dry_run:
        raise RuntimeError(f"pyautogui not available: {_pyautogui_err}")

    ih, iw = img_shape
    sx, sy, ox, oy = compute_fit(iw, ih, rect, fit_mode)

    if not dry_run:
        for n in (3, 2, 1):
            print(f"{n}…")
            time.sleep(1)

    ctrl.install()
    try:
        if not dry_run:
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0
            for attr in ("MINIMUM_DURATION", "MINIMUM_SLEEP"):
                if hasattr(pyautogui, attr):
                    setattr(pyautogui, attr, 0)

        rate = max(60, int(pps * max(0.2, speed)))
        delay = 1.0 / rate
        spacing_px = max(1, spacing_px)

        focused = False
        total = len(polylines)
        for idx, path in enumerate(polylines):
            if ctrl.aborted:
                break
            # Progress
            print(f"\r[Drawing] stroke {idx + 1}/{total}", end="", flush=True)

            for chunk in split_long_paths(path, max_stroke_len):
                if ctrl.aborted:
                    break
                mapped = [map_pt(int(pt[0]), int(pt[1]), sx, sy, ox, oy)
                          for pt in chunk]
                mapped = resample(mapped, spacing_px)
                if len(mapped) < 2:
                    continue

                if dry_run:
                    continue   # skip actual drawing

                if not focused:
                    pyautogui.click(mapped[0][0], mapped[0][1])
                    time.sleep(0.03)
                    focused = True

                pyautogui.moveTo(mapped[0][0], mapped[0][1], duration=0)
                pyautogui.mouseDown(button="left")
                time.sleep(0.01)

                for mx, my in mapped[1:]:
                    while ctrl.paused and not ctrl.aborted:
                        time.sleep(0.05)
                    if ctrl.aborted:
                        break
                    if use_move:
                        pyautogui.moveTo(mx, my, duration=max(0.0, drag_dur))
                    else:
                        pyautogui.dragTo(mx, my, duration=max(0.0, drag_dur),
                                         button="left")
                    if drag_dur <= 0.0 and delay > 0:
                        time.sleep(delay)

                pyautogui.mouseUp(button="left")
                time.sleep(0.01)

        print()  # newline after progress
    finally:
        ctrl.uninstall()


# ===================================================================
#  MAIN
# ===================================================================

def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    # Early validation
    if not args.dry_run and _pyautogui_err:
        print(f"pyautogui required for drawing: {_pyautogui_err}", file=sys.stderr)
        return 2
    if _keyboard_err and not args.dry_run:
        print(f"keyboard required: {_keyboard_err}", file=sys.stderr)

    # ---- Image processing pipeline ------------------------------------
    gray = load_and_prepare(args.image, max_dim=args.max_dim, invert=args.invert)
    print(f"[Info] Working image size: {gray.shape[1]}x{gray.shape[0]}")

    edges = extract_doodle_edges(gray, args.detail)
    thin = thin_edges(edges)

    polylines = extract_polylines(thin, min_len=args.min_path_len)
    polylines = order_paths(polylines)
    print(f"[Info] Extracted {len(polylines)} outline paths")

    if len(polylines) > 1:
        polylines = link_close_paths(polylines, max_dist=args.link_dist)
        print(f"[Info] After linking: {len(polylines)} paths")

    if not polylines:
        print("No drawable paths found. Try --detail high or a different image.",
              file=sys.stderr)
        return 1

    # ---- Preview ------------------------------------------------------
    if args.preview or args.save_preview:
        preview_paths(gray, polylines, save_path=args.save_preview)

    if args.dry_run:
        print("Dry run complete.")
        return 0

    # ---- Calibration & drawing ----------------------------------------
    rect = Calibrator().run()
    if rect.width < 5 or rect.height < 5:
        print("Canvas rect too small.", file=sys.stderr)
        return 3

    draw_on_canvas(
        polylines=polylines,
        img_shape=gray.shape[:2],
        rect=rect,
        fit_mode=args.fit,
        pps=args.pps,
        speed=args.speed,
        max_stroke_len=args.max_stroke_len,
        ctrl=DrawController(),
        dry_run=False,
        spacing_px=args.spacing_px,
        drag_dur=args.drag_duration,
        use_move=args.use_move,
    )

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
