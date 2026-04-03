# Auto Sketch Drawer — Instagram DM Doodle Edition

An automated drawing tool that converts any image (photo or illustration) into clean, doodle-style outlines and draws them on any canvas via mouse automation.

This tool is explicitly optimised for the small, vertical **Instagram Direct Message doodle canvas**.

## Key Features

- **Instagram DM Optimized**: Aggressive downscaling, smoothing, and feature removal (no shading, no texture dots) to keep doodles looking clean on small canvases.
- **Path Linking engine**: Connects fragmented paths to dramatically reduce pen-lift travel time, resulting in faster and smoother drawings.
- **Multiscale Edge Detection**: Tuned Canny edge detection with detail thresholds.
- **Automatic Drawing**: Automates your mouse to draw the detected polylines continuously.
- **Preview & Dry Run**: Generate a preview image to verify the doodle before moving your mouse.
- **Interactive Canvas Calibration**: Defines canvas boundaries safely via hotkeys.
- **Abortion & Pause Supports**: F6 to pause, F7 to abort at any time.

## Requirements

- Python 3.7+
- Windows, macOS, or Linux
- Administrator/root privileges (for keyboard hotkeys on some operating systems)

## Installation

1. Clone or download this repository.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

*Note: On Windows, run your terminal as Administrator for the keyboard hotkeys to accurately register during calibration and drawing.*

## Usage

### Instagram Doodle via Windows Phone Link

This tool is perfect for drawing automated sketches on Instagram Direct Message doodles using the Windows Phone Link app.

1. Open the **Windows Phone Link** app and mirror your phone screen to your PC.
2. Navigate into an Instagram chat and open the **doodle canvas**.
3. Select your brush and color.
4. Run the script with your desired image via terminal (e.g., `python main.py --image path/to/your/image.jpg`).
5. When the calibration step starts:
   - Hover your mouse over the **top-left corner** of the doodle canvas and press **F8**.
   - Hover your mouse over the **bottom-right corner** of the doodle canvas and press **F9**.
   - Press **F10** to confirm the drawing area and start the drawing process!

## Command Line Options

### Core Options
- `--image` (required): Path to the input image file (photo or illustration).
- `--detail`: Outline detail level - `low` (minimal lines), `med` (default), or `high` (more lines).
- `--speed`: Drawing speed multiplier (default: 1.0). Higher values draw faster.
- `--fit`: How the image maps onto the canvas - `contain` (default, preserves ratio) or `fill` (fills canvas).
- `--invert`: Invert colors before edge detection (useful for dark backgrounds).
- `--dry-run`: Compute paths completely without moving the mouse to ensure safety.
- `--preview`: Show a preview window of the generated doodle before drawing.
- `--save-preview`: Path to save the preview image (e.g., `preview.png`).

### Advanced Tuning Options
- `--max-dim` (default: 500): Downscale image so the longest side is at most this many pixels (ideal for IG's canvas).
- `--link-dist` (default: 8.0): Max pixel distance to automatically link nearby path endpoints.
- `--min-path-len` (default: 25): Discard small, isolated paths shorter than this length in pixels.
- `--pps` (default: 1200): Target points per second limit to pace the dragging operations.
- `--max-stroke-len` (default: 800): Break down continuous paths into maximum lengths for mouse buffer safety.
- `--spacing-px` (default: 2): Max pixel gap between resampled points in a path.
- `--drag-duration` (default: 0.0): Add forced duration latency for drag steps.
- `--use-move`: Use `mouseDown` + `moveTo` instead of `dragTo` for apps that handle move events better.

## Example Commands

```bash
# Basic drawing with a setup preview
python main.py --image path/to/your/image.jpg --preview

# High detail, 50% drawing speed
python main.py --image path/to/your/image.jpg --detail high --speed 0.5

# Minimal paths, fill ratio, and export preview
python main.py --image path/to/your/image.jpg --detail low --fit fill --save-preview preview.png

# Dry run to test path extraction
python main.py --image path/to/your/image.jpg --dry-run --preview
```

## Controls During Execution

- **F8**: Set top-left bounds of the canvas
- **F9**: Set bottom-right bounds of the canvas
- **F10**: Confirm calibration and execute draw loop
- **F6**: Pause/Resume drawing
- **F7**: Abort drawing entirely
- **ESC**: Cancel calibration loop

## Troubleshooting

- **Hotkeys not registering**: Ensure your terminal is running as an Administrator.
- **Drawing too fast or missing details**: Reduce `--speed` or lower `--pps`.
- **Canvas app acts weird**: Try passing the `--use-move` flag.
- **No lines detected**: Try passing `--invert` if your source image has a dark background with light contours.

## License

This project is provided as-is for personal and educational use.
