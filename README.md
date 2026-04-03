# Instagram DM Automaton for doodles

This repository provides an algorithmic engine engineered to transform ordinary photographs or illustrations into streamlined, single-stroke drawing instructions. The script subsequently interfaces directly with your machine's input stream, physically reproducing the computed path onto any digital painting interface. It is uniquely tailored for generating sketches inside the miniature, mobile-oriented Instagram Direct Message canvas via desktop sharing.

## Capabilities & Engineering Focus

*   **Designed for Miniature Interfaces**: The application prioritizes aggressive downsizing and noise eradication, preventing visual clutter when drawing on confined pixel dimensions.
*   **Intelligent Stroke Connections**: An embedded path-linking protocol evaluates endpoint proximity to merge separated curves, drastically decreasing the duration the emulated stylus spends hovering between strokes.
*   **Dynamic Visual Evaluation**: Validate your computational outputs through a preliminary visualizer window, avoiding botched executions on a live canvas.
*   **Fail-Safe Interventions**: Physical keyboard hooks intercept processes instantaneously—providing on-demand halting or permanent cancellation mechanisms.
*   **Coordinate Calibration System**: An interactive loop secures physical screen coordinates to ensure the drawing strictly persists within a designated software container.

## Algorithmic Pipeline & Mathematical Approaches

The conversion of a dense, rasterized image into a sequential drawing path involves a robust mathematical sequence:

1.  **Adaptive Histogram Equalization (CLAHE)**: Initial normalization stabilizes the structural contrast, mitigating the impacts of overly exposed or underexposed elements in amateur photography.
2.  **Topological Smoothing**: A heavy bilateral filter flattens chromatic variations while respecting hard structural dividers, followed by median blurring to obliterate microscopic textures (like skin pores or clothing weave).
3.  **Contour Harvesting (Canny)**: The application deploys adjustable Canny threshold limits, allowing structural borders to emerge while disregarding insignificant gradients.
4.  **Morphological Bridging & Filtering**: Elliptical closing kernels seal microscopic fractures in the lines, and a Connected Components analysis dynamically rips out orphaned graphical clusters utilizing area thresholds.
5.  **Skeletonization**: The dense borders are mathematically constrained down to a unilinear centerline, stripping thickness into a purely one-dimensional mathematical instruction set.
6.  **Path Routing Optimization**: A heuristic routing algorithm sequentially organizes the stroke commands top-to-bottom and links contiguous terminations (greedy metric approximation), minimizing non-drawing transit periods for maximum speed.

## Prerequisites for Operation

*   A local installation of Python version 3.7 or newer.
*   A functioning workstation on Windows, Apple macOS, or an X11-based Linux environment.
*   Administrative execution permissions, strictly to grant global intercept capabilities for the physical keyboard hooks.

## System Deployment

Clone the source code onto your local drive and initialize the Python libraries via the standard package manager protocol:

```bash
pip install -r requirements.txt
```

*Attention Windows Administrators: You must invoke your command prompt with elevated administrative rights to enable the failsafe trigger mapping to function properly.*

## Operational Walkthrough (Phone Link Integration)

The software excels entirely when bridged to an active mobile instance, particularly using the Windows Phone Link application to transmit inputs directly into the Instagram ecosystem. 

1.  Initialize the **Windows Phone Link** client and project your device's interface onto your desktop monitor.
2.  Navigate specifically to your targeted Instagram dialogue and activate the freehand sketch interface.
3.  Prime your digital pen thickness and designated pigment.
4.  Launch the execution engine against your desired target file via your terminal (`python main.py --image your_photo.jpg`).
5.  As the spatial boundary mapping sequence triggers:
    *   Position your cursor precisely over the topmost left pixel of your target drawing region and tap **F8**.
    *   Mirror this process by positioning the cursor over the furthest bottom right pixel and trigger **F9**.
    *   Lock in the coordinates and unleash the drawing sequence by engaging **F10**.

## Configuration Dictionary

The runtime supports an extensive spectrum of flags to modulate the algorithm's behavior.

### Foundational Parameters
*   `--image` (Mandatory): The absolute or relative trajectory pointing toward your source graphic.
*   `--detail`: Architectural fidelity setting consisting of `low` (bare minimum boundaries), `med` (factory standard), and `high` (dense contour discovery).
*   `--speed`: Operational multiplier overriding default execution bounds. Values exceeding 1.0 accelerate the robotic output.
*   `--fit`: Mapping proportion toggle. Deploy `contain` to lock original proportions or `fill` to stretch data across the target space.
*   `--invert`: Reverses luminosity scaling algorithms prior to evaluation, saving the system when analyzing inverted or dark-mode compositions.
*   `--dry-run`: Generates path math without injecting mouse instructions into the operating system.
*   `--preview`: Prompts a local visualizer rendering the geometric outcome prior to mechanical execution.
*   `--save-preview`: Specifies a destination output file for exporting the computed stroke schematic (e.g., `schematic.png`).

### Engine Calibration Switches
*   `--max-dim` (defaulting to 500): Instructs the pre-processor to collapse image bounds preventing memory or operational overflows.
*   `--link-dist` (defaulting to 8.0): The maximum radial tolerance deployed by the routing engine to artificially merge shattered geometry endpoints.
*   `--min-path-len` (defaulting to 25): A destructive filter threshold discarding short, visually insignificant line fragments.
*   `--pps` (defaulting to 1200): Coordinates emitted toward the system bus every simulated second, stabilizing input buffers.
*   `--max-stroke-len` (defaulting to 800): Chunks unbroken operations into arrays to bypass operating system buffer lockouts.
*   `--spacing-px` (defaulting to 2): Internal pixel gaps retained during final vector interpolation sweeps.
*   `--drag-duration` (defaulting to 0.0): Injects physical delays between linear traversals.
*   `--use-move`: Bypasses the native `dragTo` API, substituting a `mouseDown` supplemented sequential traversal loop if the primary instruction gets discarded by native applications.

## Execution Scenarios

```bash
# Standard workflow encompassing visual confirmation
python main.py --image photo.jpg --preview

# Detailed mapping rendered efficiently at halved velocity
python main.py --image photo.jpg --detail high --speed 0.5

# Maximum spatial utilization paired with schematic logging
python main.py --image photo.jpg --detail low --fit fill --save-preview preview.png

# Algorithmic pathing diagnostic run
python main.py --image photo.jpg --dry-run --preview
```

## Physical System Interrupts

*   **F8**: Registers the minimal boundary coordinates.
*   **F9**: Registers the maximal boundary coordinates.
*   **F10**: Commits structural bounds and fires the robotic process.
*   **F6**: Toggles the suspension of current mechanical actions.
*   **F7**: Commands an immediate system death for the robotic output.
*   **ESC**: Nullifies the boundary staging loop entirely.

## System Fault Troubleshooting

*   **Lethargic Key Recognition**: Escalate your terminal application to root/administrative access level.
*   **Erratic Line Emission Processing**: Attenuate the mechanical throughput by shrinking the `--speed` ratio or dragging down the `--pps` configuration.
*   **Target Interface Rejection**: Counteract native drag dismissal by invoking `--use-move`.
*   **Missing Topological Signatures**: Inject the `--invert` modifier if dealing with a high-contrast negative composition, or ramp detail levels upwards.

## Distribution Protocol

These computational structures are released entirely as-is, oriented around investigative experimentation, educational observation, and individual deployment.
