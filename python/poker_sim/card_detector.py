"""
Playing card detection from images using OpenCV.
Adapted from EdjeElectronics/OpenCV-Playing-Card-Detector.
Card index: 0-51 (rank 0-12, suit 0-3). rank=card%13, suit=card//13.
"""

import os
from pathlib import Path
from typing import List

RANK_NAMES = ['Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight',
              'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace']
SUIT_NAMES = ['Clubs', 'Diamonds', 'Hearts', 'Spades']

# Edje repo URL (for reference; images are bundled in card_imgs/)
RANK_MAP = {name: i for i, name in enumerate(RANK_NAMES)}
SUIT_MAP = {name: i for i, name in enumerate(SUIT_NAMES)}



def _ensure_card_imgs() -> str:
    """Return path to bundled Card_Imgs (from Edje repo)."""
    pkg_dir = Path(__file__).resolve().parent
    return str(pkg_dir / 'card_imgs')


def _rank_suit_to_card(rank_name: str, suit_name: str) -> int | None:
    """Map rank+suit names to card index 0-51. Returns None if unknown."""
    ri = RANK_MAP.get(rank_name)
    si = SUIT_MAP.get(suit_name)
    if ri is not None and si is not None:
        return ri + si * 13
    return None


def detect_cards_from_image(image_bytes: bytes) -> List[int]:
    """Detect playing cards from image. Returns list of card indices (0-51)."""
    cards, _, _, _ = detect_cards_with_boxes(image_bytes)
    return cards


def detect_cards_with_boxes(image_bytes: bytes) -> tuple[List[int], List[tuple[int, int, int, int]], int, int]:
    """
    Detect playing cards from image. Returns (card_indices, boxes, img_w, img_h).
    boxes: list of (x, y, w, h) in image coords.
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        return [], [], 0, 0

    imgs_path = _ensure_card_imgs()
    narray = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(narray, cv2.IMREAD_COLOR)
    if img is None:
        return [], [], 0, 0
    img_h, img_w = img.shape[:2]

    train_ranks = _load_ranks(imgs_path)
    train_suits = _load_suits(imgs_path)
    thresh = _preprocess_image(img)
    cnts_sort, cnt_is_card = _find_cards(thresh)
    if not cnts_sort:
        return [], [], img_w, img_h

    cards: List[int] = []
    boxes: List[tuple[int, int, int, int]] = []
    for i, is_card in enumerate(cnt_is_card):
        if is_card != 1:
            continue
        x, y, w, h = cv2.boundingRect(cnts_sort[i])
        boxes.append((int(x), int(y), int(w), int(h)))
        if train_ranks and train_suits:
            qcard = _preprocess_card(cnts_sort[i], img)
            if qcard is not None:
                rank_name, suit_name = _match_card(qcard, train_ranks, train_suits)
                c = _rank_suit_to_card(rank_name, suit_name)
                if c is not None:
                    cards.append(c)
    return cards, boxes, img_w, img_h


# --- Internal (adapted from Edje Cards.py) ---

BKG_THRESH = 60
CARD_THRESH = 30
CORNER_WIDTH = 32
CORNER_HEIGHT = 84
RANK_WIDTH = 70
RANK_HEIGHT = 125
SUIT_WIDTH = 70
SUIT_HEIGHT = 100
RANK_DIFF_MAX = 5000
SUIT_DIFF_MAX = 1800
CARD_MAX_AREA = 250000
CARD_MIN_AREA = 5000


def _load_ranks(filepath: str) -> list:
    import cv2
    train = []
    for name in RANK_NAMES:
        path = os.path.join(filepath, f'{name}.jpg')
        if os.path.exists(path):
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                train.append({'name': name, 'img': img})
    return train


def _load_suits(filepath: str) -> list:
    import cv2
    train = []
    for name in SUIT_NAMES:
        path = os.path.join(filepath, f'{name}.jpg')
        if os.path.exists(path):
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                train.append({'name': name, 'img': img})
    return train


def _preprocess_image(image) -> "cv2.Mat":
    import cv2
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    h, w = image.shape[:2]
    bkg_level = int(gray[int(h / 100)][int(w / 2)])
    thresh_level = min(255, bkg_level + BKG_THRESH)
    _, thresh = cv2.threshold(blur, thresh_level, 255, cv2.THRESH_BINARY)
    return thresh


def _find_cards(thresh_image):
    import cv2
    import numpy as np

    result = cv2.findContours(thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = result[0] if len(result) == 2 else result[1]
    hier = result[1] if len(result) == 2 else result[0]
    if not cnts:
        return [], []

    index_sort = sorted(range(len(cnts)), key=lambda i: cv2.contourArea(cnts[i]), reverse=True)
    cnts_sort = [cnts[i] for i in index_sort]
    hier_arr = np.array(hier)
    if hier_arr.ndim == 3:
        hier_arr = hier_arr[0]
    hier_sort = [hier_arr[index_sort[i]] if index_sort[i] < len(hier_arr) else [-1, -1, -1, -1]
                 for i in range(len(cnts_sort))]

    cnt_is_card = []
    for i, cnt in enumerate(cnts_sort):
        size = cv2.contourArea(cnt)
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.01 * peri, True)
        parent = int(hier_sort[i][3]) if i < len(hier_sort) else -1
        if (CARD_MIN_AREA < size < CARD_MAX_AREA and parent == -1 and len(approx) == 4):
            cnt_is_card.append(1)
        else:
            cnt_is_card.append(0)
    return cnts_sort, cnt_is_card


def _flattener(image, pts, w, h):
    import cv2
    import numpy as np

    pts = np.array(pts, dtype=np.float32).reshape(4, 2)
    s = np.sum(pts, axis=1)
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]

    temp_rect = np.zeros((4, 2), dtype=np.float32)
    if w <= 0.8 * h:
        temp_rect[0], temp_rect[1], temp_rect[2], temp_rect[3] = tl, tr, br, bl
    elif w >= 1.2 * h:
        temp_rect[0], temp_rect[1], temp_rect[2], temp_rect[3] = bl, tl, tr, br
    else:
        if pts[1, 1] <= pts[3, 1]:
            temp_rect[0], temp_rect[1], temp_rect[2], temp_rect[3] = pts[1], pts[0], pts[3], pts[2]
        else:
            temp_rect[0], temp_rect[1], temp_rect[2], temp_rect[3] = pts[0], pts[3], pts[2], pts[1]

    dst = np.array([[0, 0], [199, 0], [199, 299], [0, 299]], np.float32)
    M = cv2.getPerspectiveTransform(temp_rect.astype(np.float32), dst)
    warp = cv2.warpPerspective(image, M, (200, 300))
    if len(warp.shape) == 3:
        warp = cv2.cvtColor(warp, cv2.COLOR_BGR2GRAY)
    return warp


def _preprocess_card(contour, image):
    import cv2
    import numpy as np

    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.01 * peri, True)
    pts = np.float32(approx)
    x, y, w, h = cv2.boundingRect(contour)
    w, h = float(w), float(h)

    warp = _flattener(image, pts, w, h)
    Qcorner = warp[0:CORNER_HEIGHT, 0:CORNER_WIDTH]
    Qcorner_zoom = cv2.resize(Qcorner, (0, 0), fx=4, fy=4)

    white_level = Qcorner_zoom[15, int((CORNER_WIDTH * 4) / 2)]
    thresh_level = max(1, white_level - CARD_THRESH)
    _, query_thresh = cv2.threshold(Qcorner_zoom, thresh_level, 255, cv2.THRESH_BINARY_INV)

    Qrank = query_thresh[20:185, 0:128]
    Qsuit = query_thresh[186:336, 0:128]

    rank_img = None
    suit_img = None

    r = cv2.findContours(Qrank, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = r[0] if len(r) == 2 else r[1]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    if cnts:
        x1, y1, w1, h1 = cv2.boundingRect(cnts[0])
        roi = Qrank[y1:y1 + h1, x1:x1 + w1]
        rank_img = cv2.resize(roi, (RANK_WIDTH, RANK_HEIGHT), 0, 0)

    s = cv2.findContours(Qsuit, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = s[0] if len(s) == 2 else s[1]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    if cnts:
        x2, y2, w2, h2 = cv2.boundingRect(cnts[0])
        roi = Qsuit[y2:y2 + h2, x2:x2 + w2]
        suit_img = cv2.resize(roi, (SUIT_WIDTH, SUIT_HEIGHT), 0, 0)

    if rank_img is None or suit_img is None:
        return None
    return {'rank_img': rank_img, 'suit_img': suit_img}


def _match_card(qcard, train_ranks, train_suits):
    import cv2
    import numpy as np

    best_rank, best_suit = 'Unknown', 'Unknown'
    best_rank_diff, best_suit_diff = 10000, 10000

    for t in train_ranks:
        diff = int(np.sum(cv2.absdiff(qcard['rank_img'], t['img'])) / 255)
        if diff < best_rank_diff:
            best_rank_diff = diff
            best_rank = t['name']
    for t in train_suits:
        diff = int(np.sum(cv2.absdiff(qcard['suit_img'], t['img'])) / 255)
        if diff < best_suit_diff:
            best_suit_diff = diff
            best_suit = t['name']

    if best_rank_diff >= RANK_DIFF_MAX:
        best_rank = 'Unknown'
    if best_suit_diff >= SUIT_DIFF_MAX:
        best_suit = 'Unknown'
    return best_rank, best_suit
