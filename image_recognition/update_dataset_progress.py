import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ACTORS_CSV = ROOT / "actors.csv"
RAW_DIR = ROOT / "dataset" / "raw"
METADATA_CSV = ROOT / "dataset_metadata.csv"
TRACKER_CSV = ROOT / "dataset_progress_tracker.csv"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def safe_name(name):
    return re.sub(r"[^\w\-]+", "_", name).strip("_")


def read_actors():
    with ACTORS_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [row["actor_name"].strip() for row in reader if row.get("actor_name", "").strip()]


def count_images(actor_name):
    folder = RAW_DIR / safe_name(actor_name)

    if not folder.exists():
        return 0

    return sum(
        1 for path in folder.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def count_metadata_rows():
    counts = {}

    if not METADATA_CSV.exists():
        return counts

    with METADATA_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            actor_name = row.get("actor_name", "").strip()
            if actor_name:
                counts[actor_name] = counts.get(actor_name, 0) + 1

    return counts


def main():
    actors = read_actors()
    metadata_counts = count_metadata_rows()

    rows = []

    for actor in actors:
        current_images = count_images(actor)
        metadata_rows = metadata_counts.get(actor, 0)

        if current_images >= 100:
            status = "Target reached"
        elif current_images > 0:
            status = "In progress"
        else:
            status = "Not started"

        rows.append({
            "actor_name": actor,
            "target_images": 100,
            "current_images": current_images,
            "metadata_rows": metadata_rows,
            "status": status,
            "notes": "Review images manually before annotation."
        })

    with TRACKER_CSV.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["actor_name", "target_images", "current_images", "metadata_rows", "status", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated tracker: {TRACKER_CSV}")


if __name__ == "__main__":
    main()
