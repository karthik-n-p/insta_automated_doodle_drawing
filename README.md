# Auto Sketch Drawer

An automated drawing tool that converts images into edge-based sketches and draws them on any canvas application using mouse automation.

## Features

- **Edge Detection**: Uses multiscale Canny edge detection to extract drawing paths from images
- **Automatic Drawing**: Automatically draws detected edges on any canvas application
- **Customizable Detail**: Choose between low, medium, or high detail levels
- **Speed Control**: Adjustable drawing speed and points per second
- **Preview Mode**: Preview detected paths before drawing
- **Canvas Calibration**: Interactive calibration to define your drawing canvas area
- **Pause/Abort Controls**: Hotkey support for pausing or aborting the drawing process

## Requirements

- Python 3.7+
- Windows, macOS, or Linux
- Administrator/root privileges (for keyboard hotkeys on some systems)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

**Note**: On Windows, you may need to run as Administrator for keyboard hotkeys to work properly.

## Usage

### Instagram Doodle via Windows Phone Link

This tool is perfect for drawing automated sketches on Instagram Direct Message doodles using the Windows Phone Link app.

1. Open the **Windows Phone Link** app and mirror your phone screen.
2. Open Instagram and navigate to a chat where you want to send a doodle.
3. Open the **doodle canvas** in the chat.
4. Run the script with your desired image (e.g., `python main.py --image photo.jpg`).
5. When the calibration step starts:
   - Hover your mouse over the **top-left edge** of the doodle canvas and press **F8**.
   - Hover over the **bottom-right edge** of the doodle canvas and press **F9**.
   - Press **F10** to confirm the drawing area and start the drawing process!

### Basic Usage

```bash
python draw_sketch.py --image path/to/your/image.jpg
```

### Command Line Options

- `--image` (required): Path to the input image file
- `--speed` (default: 1.0): Drawing speed multiplier (higher = faster)
- `--detail` (default: "high"): Edge detail level - `low`, `med`, or `high`
- `--fit` (default: "contain"): Fit mode - `contain` (preserves aspect ratio) or `fill` (fills canvas)
- `--invert`: Invert image colors before edge detection
- `--preview`: Show a preview window of detected paths before drawing
- `--dry-run`: Compute paths without actually moving the mouse
- `--max-stroke-len` (default: 800): Maximum points per continuous stroke segment
- `--pps` (default: 1200): Target points per second while dragging
- `--min-path-len` (default: 5): Minimum polyline length to keep (in points)
- `--spacing-px` (default: 2): Maximum pixel spacing between points after resampling
- `--drag-duration` (default: 0.0): Per-step duration for drag/move operations
- `--use-move`: Use mouseDown + moveTo instead of dragTo (for apps that handle move events better)

### Example Commands

```bash
# Basic drawing with preview
python draw_sketch.py --image frieren.PNG --preview

# High detail, slower speed
python draw_sketch.py --image maomao.PNG --detail high --speed 0.5

# Inverted image, fill canvas
python draw_sketch.py --image frieren-2.PNG --invert --fit fill

# Dry run to test without drawing
python draw_sketch.py --image frieren-3.jpg --dry-run --preview
```

## How It Works

1. **Image Processing**: The tool loads your image and converts it to grayscale
2. **Edge Detection**: Uses multiscale Canny edge detection to find edges at different scales
3. **Thinning**: Thins the detected edges to single-pixel width using skeletonization
4. **Path Extraction**: Extracts continuous paths (polylines) from the thinned edges
5. **Calibration**: You define the canvas area by:
   - Hovering over the top-left corner and pressing **F8**
   - Hovering over the bottom-right corner and pressing **F9**
   - Pressing **F10** to confirm (or **ESC** to cancel)
6. **Drawing**: The tool automatically draws the paths on your canvas using mouse automation

## Controls During Drawing

- **F6**: Pause/Resume drawing
- **F7**: Abort drawing
- **ESC**: Cancel calibration

## Tips

- **Canvas Setup**: Before running, open your drawing application, select your brush and color, and position the canvas window
- **Preview First**: Use `--preview` to see what will be drawn before starting
- **Speed Adjustment**: Start with default speed and adjust `--speed` if needed. Lower values = slower, more precise drawing
- **Detail Level**:
  - `low`: Fewer, simpler paths (faster drawing)
  - `med`: Balanced detail
  - `high`: Maximum detail (slower drawing, more paths)
- **Spacing**: Adjust `--spacing-px` based on your brush size (typically 25-40% of brush diameter)
- **Compatibility**: If your drawing app doesn't respond well to `dragTo`, try the `--use-move` flag

## Troubleshooting

- **Hotkeys not working**: On Windows, try running as Administrator
- **Drawing too fast/slow**: Adjust `--speed` or `--pps` parameters
- **Missing edges**: Try `--detail high` or `--invert` if edges aren't detected properly
- **Canvas not responding**: Try `--use-move` or adjust `--drag-duration`

## License

This project is provided as-is for personal and educational use.
