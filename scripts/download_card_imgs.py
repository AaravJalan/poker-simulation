#!/usr/bin/env python3
"""Download Card_Imgs from EdjeElectronics/OpenCV-Playing-Card-Detector for card detection."""
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/EdjeElectronics/OpenCV-Playing-Card-Detector/master/Card_Imgs"
FILES = [
    "Ace.jpg", "Two.jpg", "Three.jpg", "Four.jpg", "Five.jpg", "Six.jpg", "Seven.jpg",
    "Eight.jpg", "Nine.jpg", "Ten.jpg", "Jack.jpg", "Queen.jpg", "King.jpg",
    "Clubs.jpg", "Diamonds.jpg", "Hearts.jpg", "Spades.jpg",
]

def main():
    dest = Path(__file__).resolve().parent.parent / "python" / "poker_sim" / "card_imgs"
    dest.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        url = f"{BASE}/{f}"
        out = dest / f
        print(f"Downloading {f}...")
        urllib.request.urlretrieve(url, out)
    print(f"Done. Templates saved to {dest}")

if __name__ == "__main__":
    main()
