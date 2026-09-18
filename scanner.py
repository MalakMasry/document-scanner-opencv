import cv2
import numpy as np

def load_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image at path: '{image_path}'. Check file location.")
    return img

def preprocess_image(img):
    # img = cv2.resize(img, (600, 800))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    canny = cv2.Canny(blurred, 50, 150)
    return canny

def find_contours(canny):
    contours, _ = cv2.findContours(canny.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            return approx

    raise ValueError("No document found in image.")

def reorder_points(contour_vertices):
    pts = contour_vertices.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]


    return rect

def warp_image(img, ordered_points):
    (tl, tr, br, bl) = ordered_points

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(ordered_points, dst)
    warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))

    return warped

def adaptive_threshold(warped):
    gray_warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    blurred = cv2.bilateralFilter(gray_warped, d=5, sigmaColor=50, sigmaSpace=50)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 25, 8
    )
    
    return thresh

def scan_image(image_path):
    img = load_image(image_path)
    canny = preprocess_image(img)
    contour_vertices = find_contours(canny)
    ordered_points = reorder_points(contour_vertices)

    (tl, tr, br, bl) = ordered_points
    warped = warp_image(img, ordered_points)
    thresh = adaptive_threshold(warped)

    return thresh

if __name__ == "__main__":
    image_path = "sample_images/sample.jpg"
    try:
        scanned_image = scan_image(image_path)
        cv2.imshow("Scanned Image", scanned_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except ValueError as e:
        print(e)