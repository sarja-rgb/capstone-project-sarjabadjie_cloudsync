# -*- coding: utf-8 -*-

import csv
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "dataset" / "raw"
METADATA_CSV = ROOT / "dataset_metadata.csv"
TRACKER_CSV = ROOT / "dataset_progress_tracker.csv"
REPORT_MD = ROOT / "IMAGE_RECOGNITION_DEMO_REPORT.md"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def normalize_name(name):
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def count_images(actor_folder):
    count = 0
    for file_path in actor_folder.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            count += 1
    return count


def read_metadata_counts():
    counts = {}
    placeholders = []

    if not METADATA_CSV.exists():
        return counts, placeholders

    with METADATA_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            actor = row.get("actor_name", "").strip()
            source = row.get("source_url", "").strip()
            license_name = row.get("license", "").strip()
            author = row.get("author", "").strip()
            image_file = row.get("image_filename", "").strip()

            if actor:
                key = normalize_name(actor)
                counts[key] = counts.get(key, 0) + 1

            if "NEEDED" in source.upper() or "NEEDED" in license_name.upper() or "NEEDED" in author.upper():
                placeholders.append((actor, image_file))

    return counts, placeholders


def read_tracker():
    rows = []

    if not TRACKER_CSV.exists():
        return rows

    with TRACKER_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    return rows


def main():
    print("=" * 70)
    print("CloudSync Insight - Image Recognition Part 2 Demo")
    print("=" * 70)
    print(f"Demo time: {datetime.now()}")
    print(f"Project folder: {ROOT}")
    print()

    actor_folders = sorted([folder for folder in RAW_DIR.iterdir() if folder.is_dir()])
    metadata_counts, placeholders = read_metadata_counts()
    tracker_rows = read_tracker()

    print("Actor Dataset Folder Check")
    print("-" * 70)

    total_images = 0
    demo_rows = []

    for folder in actor_folders:
        image_count = count_images(folder)
        total_images += image_count

        actor_display = folder.name.replace("_", " ")
        metadata_key = normalize_name(actor_display)
        metadata_count = metadata_counts.get(metadata_key, 0)

        demo_rows.append((folder.name, image_count, metadata_count))

        print(f"{folder.name:25} Images: {image_count:3} | Metadata rows: {metadata_count:3}")

    print("-" * 70)
    print(f"Total actor folders: {len(actor_folders)}")
    print(f"Total local test images: {total_images}")
    print()

    print("Tracker File Check")
    print("-" * 70)

    if tracker_rows:
        for row in tracker_rows:
            print(
                f"{row.get('actor_name', ''):22} "
                f"Target: {row.get('target_images', ''):3} | "
                f"Images: {row.get('current_images', ''):3} | "
                f"Metadata: {row.get('metadata_rows', ''):3} | "
                f"Status: {row.get('status', '')}"
            )
    else:
        print("Tracker file not found or empty.")

    print()
    print("Metadata Placeholder Check")
    print("-" * 70)

    if placeholders:
        print("Some manual metadata rows still need real source details:")
        for actor, image_file in placeholders:
            print(f"- {actor} | {image_file}")
    else:
        print("No placeholder metadata values found.")

    print()
    print("Demo Summary")
    print("-" * 70)
    print("Image recognition setup is ready for advisor checkpoint review.")
    print("Dataset folders, metadata tracking, progress tracker, and demo evidence are in place.")
    print("Next work: replace placeholder metadata, collect more images, annotate, split, train, and evaluate.")
    print("=" * 70)

    with REPORT_MD.open("w", encoding="utf-8") as report:
        report.write("# CloudSync Insight - Image Recognition Part 2 Demo Report\n\n")
        report.write(f"Generated: {datetime.now()}\n\n")

        report.write("## Demo Summary\n\n")
        report.write("This demo verifies the current Image Recognition Part 2 setup for the CloudSync Insight project. ")
        report.write("It checks actor folders, local test image counts, metadata rows, tracker status, and placeholder metadata values.\n\n")

        report.write("## Actor Folder Counts\n\n")
        report.write("| Actor Folder | Local Images | Metadata Rows |\n")
        report.write("|---|---:|---:|\n")

        for folder_name, image_count, metadata_count in demo_rows:
            report.write(f"| {folder_name} | {image_count} | {metadata_count} |\n")

        report.write(f"\n**Total actor folders:** {len(actor_folders)}\n\n")
        report.write(f"**Total local test images:** {total_images}\n\n")

        report.write("## Metadata Placeholder Items\n\n")

        if placeholders:
            for actor, image_file in placeholders:
                report.write(f"- {actor} - {image_file}\n")
        else:
            report.write("- No placeholder metadata values found.\n")

        report.write("\n## Next Steps\n\n")
        report.write("1. Replace placeholder metadata values with real source URL, license, and author details.\n")
        report.write("2. Continue collecting public or licensed actor images in small batches.\n")
        report.write("3. Manually verify image quality and actor correctness.\n")
        report.write("4. Annotate images with bounding boxes.\n")
        report.write("5. Split dataset into train, validation, and test folders.\n")
        report.write("6. Train and evaluate the image recognition model.\n")

    print()
    print(f"Demo report created: {REPORT_MD}")


if __name__ == "__main__":
    main()
