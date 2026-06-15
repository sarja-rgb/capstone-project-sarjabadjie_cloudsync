import argparse
import csv
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests


ROOT = Path(__file__).resolve().parent
ACTORS_CSV = ROOT / "actors.csv"
RAW_DIR = ROOT / "dataset" / "raw"
METADATA_CSV = ROOT / "dataset_metadata.csv"

COMMONS_API = "https://commons.wikimedia.org/w/api.php"

HEADERS = {
    "User-Agent": "CloudSyncImageRecognitionDemo/1.0 educational capstone dataset collection"
}


def safe_folder_name(name: str) -> str:
    return re.sub(r"[^\w\-]+", "_", name).strip("_")


def safe_file_name(name: str) -> str:
    return re.sub(r"[^\w\-.]+", "_", name).strip("_")


def get_extension_from_url(url: str) -> str:
    path = urlparse(url).path.lower()
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        if path.endswith(ext):
            return ext
    return ".jpg"


def read_actors():
    with ACTORS_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [row["actor_name"].strip() for row in reader if row.get("actor_name", "").strip()]


def search_commons_images(actor_name: str, limit: int):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f'{actor_name} portrait OR {actor_name} actor',
        "gsrnamespace": "6",
        "gsrlimit": str(limit * 3),
        "prop": "imageinfo",
        "iiprop": "url|mime|extmetadata",
    }

    response = requests.get(COMMONS_API, params=params, headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()

    pages = data.get("query", {}).get("pages", {})
    results = []

    for page in pages.values():
        imageinfo = page.get("imageinfo", [])
        if not imageinfo:
            continue

        info = imageinfo[0]
        url = info.get("url", "")
        mime = info.get("mime", "")

        if not url:
            continue

        if not mime.startswith("image/"):
            continue

        if any(skip in url.lower() for skip in [".svg", ".gif", ".tif", ".tiff"]):
            continue

        metadata = info.get("extmetadata", {})
        license_name = metadata.get("LicenseShortName", {}).get("value", "Unknown")
        author = metadata.get("Artist", {}).get("value", "Unknown")

        results.append({
            "url": url,
            "license": re.sub(r"<.*?>", "", license_name),
            "author": re.sub(r"<.*?>", "", author),
        })

        if len(results) >= limit:
            break

    return results


def download_file(url: str, output_path: Path):
    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    output_path.write_bytes(response.content)


def append_metadata(row):
    file_exists = METADATA_CSV.exists()

    with METADATA_CSV.open("a", encoding="utf-8", newline="") as f:
        fieldnames = ["actor_name", "image_filename", "source_url", "license", "author", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists or METADATA_CSV.stat().st_size == 0:
            writer.writeheader()

        writer.writerow(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5, help="Number of images to download per actor")
    args = parser.parse_args()

    actors = read_actors()

    print(f"Loaded {len(actors)} actors.")
    print(f"Downloading up to {args.limit} candidate images per actor.")
    print("Important: manually review images after download.")

    for actor in actors:
        folder = RAW_DIR / safe_folder_name(actor)
        folder.mkdir(parents=True, exist_ok=True)

        print(f"\nSearching images for: {actor}")
        images = search_commons_images(actor, args.limit)

        if not images:
            print(f"  No images found for {actor}.")
            continue

        for index, image in enumerate(images, start=1):
            ext = get_extension_from_url(image["url"])
            filename = safe_file_name(f"{safe_folder_name(actor)}_{index:03d}{ext}")
            output_path = folder / filename

            if output_path.exists():
                print(f"  Skipping existing file: {filename}")
                continue

            try:
                download_file(image["url"], output_path)

                append_metadata({
                    "actor_name": actor,
                    "image_filename": str(output_path.relative_to(ROOT)).replace("\\", "/"),
                    "source_url": image["url"],
                    "license": image["license"],
                    "author": image["author"],
                    "notes": "Wikimedia Commons candidate image; manually verify before annotation.",
                })

                print(f"  Downloaded: {filename}")
                time.sleep(0.5)

            except Exception as error:
                print(f"  Failed: {image['url']} | {error}")

    print("\nDone. Review downloaded images before using them for training.")


if __name__ == "__main__":
    main()
