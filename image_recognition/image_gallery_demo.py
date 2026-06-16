from pathlib import Path
import streamlit as st


ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "dataset" / "raw"

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

st.write(
    "This live demo shows the current Image Recognition Part 2 dataset. "
    "Each actor folder is displayed with its correct actor name and the images currently collected for that actor. "
    "This is dataset preparation evidence only. Model prediction and bounding-box detection are later steps."
)


def get_actor_images(folder_path):
    if not folder_path.exists():
        return []

    images = []

    for image_path in sorted(folder_path.rglob("*")):
        if image_path.is_file() and image_path.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(image_path)

    return images


total_images = 0

st.subheader("Dataset Summary")

summary_rows = []

for folder_name, actor_name in ACTOR_DISPLAY_NAMES.items():
    folder_path = RAW_DIR / folder_name
    images = get_actor_images(folder_path)
    total_images += len(images)

    summary_rows.append(
        {
            "Actor Name": actor_name,
            "Folder Name": folder_name,
            "Current Images": len(images),
            "Target Images": 100,
        }
    )

st.write(f"Total actor classes: **{len(ACTOR_DISPLAY_NAMES)}**")
st.write(f"Total local images currently collected: **{total_images}**")
st.dataframe(summary_rows, use_container_width=True)


st.subheader("All Actor Images With Correct Names")

for folder_name, actor_name in ACTOR_DISPLAY_NAMES.items():
    folder_path = RAW_DIR / folder_name
    images = get_actor_images(folder_path)

    st.markdown("---")
    st.header(actor_name)
    st.caption(f"Dataset folder: {folder_name}")

    if not images:
        st.warning(f"No images are currently saved for {actor_name}.")
        continue

    columns = st.columns(4)

    for index, image_path in enumerate(images):
        with columns[index % 4]:
            st.image(
                str(image_path),
                caption=f"{actor_name}\n{image_path.name}",
                use_container_width=True,
            )

st.markdown("---")
st.subheader("Demo Note")
st.write(
    "This page proves that the dataset folders contain images and that each image is displayed under the correct actor label. "
    "The next project step is to replace placeholder metadata, collect more verified images, annotate faces/actors with bounding boxes, "
    "split the dataset into train/validation/test folders, and then train the image-recognition model."
)
