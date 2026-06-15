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
    "User-Agent": "CloudSyncImageRecognitionDemo/1.0 (educational capstone; local dataset collection)"
}


def safe_name(name):
    return re.sub(r"[^\w\-]+", "_", name).strip("_")


def clean_html(value):
    if not value:
        return "Unknown"
    return re.sub(r"<.*?>", "", str(value)).replace(",", " ").strip()


def get_extension(url):
    path = urlparse(url).path.lower()
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        if ext in path:
            return ext
    return ".jpg"


def read_actors():
    with ACTORS_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [row["actor_name"].strip() for row in reader if row.get("actor_name", "").strip()]


def existing_metadata_rows():
    rows = set()
    if not METADATA_CSV.exists():
        return rows

    with METADATA_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.add((row.get("actor_name", ""), row.get("source_url", "")))
    return rows


def search_commons(actor_name, limit):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f'"{actor_name}" actor portrait',
        "gsrnamespace": "6",
        "gsrlimit": str(limit * 8),
        "prop": "imageinfo",
        "iiprop": "url|mime|extmetadata",
        "iiurlwidth": "640",
    }

    response = requests.get(COMMONS_API, params=params, headers=HEADERS, timeout=40)
    response.raise_for_status()
    data = response.json()

    pages = data.get("query", {}).get("pages", {})
    results = []

    for page in pages.values():
        info_list = page.get("imageinfo", [])
        if not info_list:
            continue

        info = info_list[0]
        full_url = info.get("url", "")
        thumb_url = info.get("thumburl", "")
        mime = info.get("mime", "")

        download_url = thumb_url or full_url

        if not download_url or not mime.startswith("image/"):
            continue

        lowered = download_url.lower()
        if any(bad in lowered for bad in [".svg", ".gif", ".tif", ".tiff"]):
            continue

        metadata = info.get("extmetadata", {})
        license_name = metadata.get("LicenseShortName", {}).get("value", "Unknown")
        author = metadata.get("Artist", {}).get("value", "Unknown")

        results.append({
            "download_url": download_url,
            "source_url": full_url,
            "license": clean_html(license_name),
            "author": clean_html(author),
        })

        if len(results) >= limit:
            break

    return results


def download_file(url, output_path):
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
    parser.add_argument("--limit", type=int, default=3, help="Images to download per actor")
    parser.add_argument("--delay", type=float, default=8.0, help="Delay between downloads")
    args = parser.parse_args()

    actors = read_actors()
    seen = existing_metadata_rows()

    print(f"Loaded {len(actors)} actors.")
    print(f"Downloading up to {args.limit} thumbnail images per actor.")
    print(f"Delay between downloads: {args.delay} seconds.")
    print("Manually review images after download.")

    for actor in actors:
        actor_folder = RAW_DIR / safe_name(actor)
        actor_folder.mkdir(parents=True, exist_ok=True)

        print(f"\nSearching Wikimedia Commons for: {actor}")
        images = search_commons(actor, args.limit)

        if not images:
            print(f"  No image candidates found for {actor}.")
            continue

        downloaded_count = 0

        for index, image in enumerate(images, start=1):
            if (actor, image["source_url"]) in seen:
                print("  Skipping duplicate metadata source.")
                continue

            ext = get_extension(image["download_url"])
            filename = f"{safe_name(actor)}_{int(time.time())}_{index:03d}{ext}"
            output_path = actor_folder / filename

            try:
                download_file(image["download_url"], output_path)

                append_metadata({
                    "actor_name": actor,
                    "image_filename": str(output_path.relative_to(ROOT)).replace("\\", "/"),
                    "source_url": image["source_url"],
                    "license": image["license"],
                    "author": image["author"],
                    "notes": "Wikimedia Commons thumbnail candidate image; manually verify before annotation.",
                })

                seen.add((actor, image["source_url"]))
                downloaded_count += 1
                print(f"  Downloaded: {filename}")

                time.sleep(args.delay)

            except Exception as error:
                print(f"  Failed: {image['download_url']} | {error}")
                time.sleep(args.delay)

        print(f"  Finished {actor}: downloaded {downloaded_count} new images.")

    print("\nDone. Review images before annotation or training.")


if __name__ == "__main__":
    main()
