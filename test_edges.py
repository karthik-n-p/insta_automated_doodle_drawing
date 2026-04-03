import cv2
import numpy as np

def xdog_edges(gray: np.ndarray, detail: str) -> np.ndarray:
    # Based on XDoG (eXtended Difference of Gaussians)
    img = gray.astype(np.float32) / 255.0
    
    if detail == "high":
        kappa = 4.5
        sigma = 0.5
        tau = 0.95
        epsilon = -0.1
        phi = 10
    elif detail == "med":
        kappa = 4.5
        sigma = 1.0
        tau = 0.98
        epsilon = 0.1
        phi = 10
    else: # low
        kappa = 4.0
        sigma = 1.5
        tau = 0.99
        epsilon = 0.2
        phi = 10

    g1 = cv2.GaussianBlur(img, (0, 0), sigma)
    g2 = cv2.GaussianBlur(img, (0, 0), sigma * kappa)
    
    # Difference of Gaussians (DoG)
    d = g1 - tau * g2
    
    # Extended DoG thresholding
    edges = np.where(d >= epsilon, 1.0, 1.0 + np.tanh(phi * d))
    
    # Convert to 8-bit image
    edges = (edges * 255).astype(np.uint8)
    
    # Invert so lines are white and background is black for thinning algorithm
    edges = cv2.bitwise_not(edges)
    
    # Threshold to binary (as xdog result is continuous)
    _, binary_edges = cv2.threshold(edges, 127, 255, cv2.THRESH_BINARY)
    
    return binary_edges

def extract_polylines(edge_img: np.ndarray, min_len: int):
    contours, _ = cv2.findContours(edge_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    polylines = []
    for cnt in contours:
        if cnt is None or len(cnt) < min_len:
            continue
        pts = cnt.squeeze(1)
        if pts.ndim != 2 or pts.shape[0] < min_len:
            continue
        polylines.append(pts.astype(np.int32))
    return polylines

def main():
    img_path = "frieren.PNG"
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    if img is None:
        print("Image not found")
        return
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    xdog = xdog_edges(gray, "high")
    xdog_poly = extract_polylines(xdog, 5)
    
    print(f"XDoG: {len(xdog_poly)} polylines")
    cv2.imwrite("test_xdog.png", xdog)

if __name__ == '__main__':
    main()
