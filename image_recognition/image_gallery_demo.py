from pathlib import Path
import csv
import streamlit as st


ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "dataset" / "raw"
TRACKER_CSV = ROOT / "dataset_progress_tracker.csv"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

ACTOR_DISPLAY_NAMES = {
    "Brad_Pitt": "Brad Pitt",
    "Denzel_Washington": "Denzel Washington",
    "Johnny_Depp": "Johnny Depp",
    "Keanu_Reeves": "Keanu Reeves",
    "Leonardo_DiCaprio": "Leonardo DiCaprio",
    "Morgan_Freeman": "Morgan Freeman",
    "Robert_Downey_Jr": "Robert Downey Jr.",
    "Samuel_L_Jackson": "Samuel L. Jackson",
    "Tom_Hanks": "Tom Hanks",
    "Will_Smith": "Will Smith",
}


st.set_page_config(
    page_title="CloudSync Image Recognition Dataset Gallery",
    layout="wide",
)

st.title("CloudSync Insight - Image Recognition Dataset Gallery")
st.caption("Image Recognition Part 2 - Dataset Preparation Checkpoint")

st.write(
    "This live gallery shows the current actor image dataset for the CloudSync Insight image-recognition checkpoint. "
    "Each image is displayed under the correct actor name. This page is for dataset proof only; prediction, "
    "bounding boxes, annotation, training, and evaluation are later steps."
)


def get_actor_images(folder_path):
    if not folder_path.exists():
        return []

    images = []

    for image_path in sorted(folder_path.rglob("*")):
        if image_path.is_file() and image_path.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(image_path)

    return images


def load_tracker_rows():
    rows = {}

    if not TRACKER_CSV.exists():
        return rows

    with TRACKER_CSV.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            actor_name = row.get("actor_name", "").strip()
            if actor_name:
                rows[actor_name] = row

    return rows


tracker_rows = load_tracker_rows()

summary_rows = []
total_images = 0

for folder_name, actor_name in ACTOR_DISPLAY_NAMES.items():
    folder_path = RAW_DIR / folder_name
    images = get_actor_images(folder_path)
    image_count = len(images)
    total_images += image_count

    tracker_row = tracker_rows.get(actor_name, {})

    summary_rows.append(
        {
            "Correct Actor Name": actor_name,
            "Dataset Folder": folder_name,
            "Current Images": image_count,
            "Metadata Rows": tracker_row.get("metadata_rows", image_count),
            "Target Images": tracker_row.get("target_images", 100),
            "Status": tracker_row.get("status", "In progress"),
        }
    )


st.subheader("Dataset Summary")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Actor Classes", len(ACTOR_DISPLAY_NAMES))

with col2:
    st.metric("Current Local Images", total_images)

with col3:
    st.metric("Target Images", len(ACTOR_DISPLAY_NAMES) * 100)

st.dataframe(summary_rows, width="stretch")


st.subheader("All 10 Actor Names With Their Actual Images")

for folder_name, actor_name in ACTOR_DISPLAY_NAMES.items():
    folder_path = RAW_DIR / folder_name
    images = get_actor_images(folder_path)

    st.markdown("---")
    st.header(actor_name)
    st.write(f"**Correct label:** {actor_name}")
    st.caption(f"Dataset folder: image_recognition/dataset/raw/{folder_name}")

    if not images:
        st.warning(f"No images are currently saved for {actor_name}.")
        continue

    columns = st.columns(4)

    for index, image_path in enumerate(images):
        with columns[index % 4]:
            st.image(
                str(image_path),
                caption=f"{actor_name}",
                width="stretch",
            )
            st.caption(f"File: {image_path.name}")


st.markdown("---")
st.subheader("Checkpoint Explanation")
st.success(
    "This live gallery confirms that the dataset has 10 actor classes and that each saved image is displayed under the correct actor name."
)

st.info(
    "This is not the final trained image-recognition model yet. The next steps are to replace placeholder metadata, "
    "collect more verified public/licensed images, annotate bounding boxes, split the dataset into train/validation/test, "
    "train the model, and evaluate it with mAP, confusion matrix, and class accuracy."
)
