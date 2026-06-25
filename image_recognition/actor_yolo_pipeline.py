import argparse
import csv
import json
import random
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image, ImageOps
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def actor_display_name(folder_name: str) -> str:
    return folder_name.replace("_", " ")


def safe_name(text: str) -> str:
    return (
        text.replace(" ", "_")
        .replace(".", "")
        .replace(",", "")
        .replace("-", "_")
        .replace("__", "_")
    )


def collect_actor_images(raw_dir: Path):
    actor_folders = sorted([p for p in raw_dir.iterdir() if p.is_dir()])
    dataset = {}

    for folder in actor_folders:
        images = [
            p for p in sorted(folder.iterdir())
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        ]
        if images:
            dataset[folder.name] = images

    if not dataset:
        raise RuntimeError(
            f"No actor images found in {raw_dir}. "
            "Put images inside image_recognition/dataset/raw/<Actor_Folder>/"
        )

    return dataset


def split_files(files, train_ratio=0.70, val_ratio=0.15, seed=42):
    files = list(files)
    random.Random(seed).shuffle(files)

    n = len(files)

    if n == 1:
        return files, [], []

    if n == 2:
        return files[:1], [], files[1:]

    train_count = max(1, int(round(n * train_ratio)))
    val_count = max(1, int(round(n * val_ratio)))

    if train_count + val_count >= n:
        train_count = max(1, n - 2)
        val_count = 1

    test_count = n - train_count - val_count

    train_files = files[:train_count]
    val_files = files[train_count:train_count + val_count]
    test_files = files[train_count + val_count:]

    return train_files, val_files, test_files


def pad_resize_image(src_path: Path, dst_path: Path, width: int, height: int):
    """
    Resize image to fit inside width x height while preserving aspect ratio.
    Add padding around the image to make the final output exactly width x height.

    Example advisor requirement:
    1920 x 1000 image -> 1920 x 1080 by adding 80px vertically,
    usually 40px top and 40px bottom.
    """
    img = Image.open(src_path)
    img = ImageOps.exif_transpose(img).convert("RGB")

    original_w, original_h = img.size
    scale = min(width / original_w, height / original_h)

    new_w = int(round(original_w * scale))
    new_h = int(round(original_h * scale))

    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (width, height), (0, 0, 0))

    x_offset = (width - new_w) // 2
    y_offset = (height - new_h) // 2

    canvas.paste(img, (x_offset, y_offset))
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dst_path, quality=95)

    # YOLO normalized bounding box around the visible original image area,
    # not the black padding.
    x_center = (x_offset + new_w / 2) / width
    y_center = (y_offset + new_h / 2) / height
    box_w = new_w / width
    box_h = new_h / height

    return x_center, y_center, box_w, box_h


def write_yolo_label(label_path: Path, class_id: int, bbox):
    label_path.parent.mkdir(parents=True, exist_ok=True)
    x_center, y_center, box_w, box_h = bbox

    with label_path.open("w", encoding="utf-8") as f:
        f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {box_w:.6f} {box_h:.6f}\n")


def write_data_yaml(out_dir: Path, actor_names):
    yaml_path = out_dir / "data.yaml"
    out_path = out_dir.resolve().as_posix()

    names_text = "\n".join([f"  {i}: {name}" for i, name in enumerate(actor_names)])

    yaml_text = f"""path: {out_path}
train: images/train
val: images/val
test: images/test

nc: {len(actor_names)}
names:
{names_text}
"""

    yaml_path.write_text(yaml_text, encoding="utf-8")
    return yaml_path


def prepare_dataset(args):
    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.out_dir)

    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw image folder not found: {raw_dir}")

    dataset = collect_actor_images(raw_dir)

    actor_folders = list(dataset.keys())
    actor_names = [actor_display_name(name) for name in actor_folders]
    actor_to_id = {actor: idx for idx, actor in enumerate(actor_folders)}

    summary_rows = []

    for actor_folder in actor_folders:
        class_id = actor_to_id[actor_folder]
        files = dataset[actor_folder]

        train_files, val_files, test_files = split_files(
            files,
            train_ratio=args.train_ratio,
            val_ratio=args.val_ratio,
            seed=args.seed,
        )

        split_map = {
            "train": train_files,
            "val": val_files,
            "test": test_files,
        }

        for split_name, split_files_list in split_map.items():
            for idx, src_path in enumerate(split_files_list, start=1):
                output_stem = f"{safe_name(actor_folder)}_{idx:04d}"
                dst_img = out_dir / "images" / split_name / f"{output_stem}.jpg"
                dst_label = out_dir / "labels" / split_name / f"{output_stem}.txt"

                bbox = pad_resize_image(
                    src_path=src_path,
                    dst_path=dst_img,
                    width=args.width,
                    height=args.height,
                )

                # This creates an automatic starter box around the image content.
                # For final training, replace these with true face/actor bounding boxes if available.
                write_yolo_label(dst_label, class_id, bbox)

                summary_rows.append(
                    {
                        "actor_folder": actor_folder,
                        "actor_name": actor_display_name(actor_folder),
                        "class_id": class_id,
                        "split": split_name,
                        "source_image": str(src_path),
                        "output_image": str(dst_img),
                        "output_label": str(dst_label),
                    }
                )

    yaml_path = write_data_yaml(out_dir, actor_names)

    summary_path = out_dir / "split_summary.csv"
    pd.DataFrame(summary_rows).to_csv(summary_path, index=False)

    print("=" * 72)
    print("CloudSync Insight - YOLO Actor Dataset Preparation")
    print("=" * 72)
    print(f"Raw folder:       {raw_dir}")
    print(f"Output folder:    {out_dir}")
    print(f"Image size:       {args.width} x {args.height}")
    print(f"Actor classes:    {len(actor_names)}")
    print(f"Total images:     {len(summary_rows)}")
    print(f"Data YAML:        {yaml_path}")
    print(f"Split summary:    {summary_path}")
    print()
    print("Class list:")
    for i, name in enumerate(actor_names):
        print(f"  {i}: {name}")

    print()
    print("Important note:")
    print("This script creates starter YOLO labels around the visible image area.")
    print("For final advisor-grade training, replace starter boxes with real face/actor annotations when available.")
    print("=" * 72)


def train_model(args):
    if YOLO is None:
        raise RuntimeError("Ultralytics is not installed. Run: python -m pip install ultralytics")

    data_yaml = Path(args.data)

    if not data_yaml.exists():
        raise FileNotFoundError(f"data.yaml not found: {data_yaml}")

    model = YOLO(args.model)

    results = model.train(
        data=str(data_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=args.project,
        name=args.name,
        exist_ok=True,
    )

    print("=" * 72)
    print("Training complete.")
    print("Best model is usually saved under:")
    print(f"{args.project}/{args.name}/weights/best.pt")
    print("=" * 72)

    return results


def read_class_names_from_yaml(data_yaml: Path):
    lines = data_yaml.read_text(encoding="utf-8").splitlines()
    names = {}

    inside_names = False
    for line in lines:
        if line.strip() == "names:":
            inside_names = True
            continue

        if inside_names:
            if not line.startswith("  "):
                break

            if ":" in line:
                left, right = line.strip().split(":", 1)
                try:
                    idx = int(left.strip())
                    names[idx] = right.strip()
                except ValueError:
                    pass

    return names


def get_true_class_from_label(label_path: Path):
    if not label_path.exists():
        return None

    text = label_path.read_text(encoding="utf-8").strip()
    if not text:
        return None

    first_line = text.splitlines()[0]
    return int(first_line.split()[0])


def evaluate_model(args):
    if YOLO is None:
        raise RuntimeError("Ultralytics is not installed. Run: python -m pip install ultralytics")

    weights_path = Path(args.weights)
    data_yaml = Path(args.data)

    if not weights_path.exists():
        raise FileNotFoundError(f"Model weights not found: {weights_path}")

    if not data_yaml.exists():
        raise FileNotFoundError(f"data.yaml not found: {data_yaml}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(str(weights_path))

    print("=" * 72)
    print("Running Ultralytics validation for mAP, precision, and recall...")
    print("=" * 72)

    val_results = model.val(
        data=str(data_yaml),
        split=args.split,
        imgsz=args.imgsz,
        project=str(output_dir),
        name="ultralytics_val",
        exist_ok=True,
    )

    box_metrics = {}
    try:
        box_metrics = {
            "precision_mean": float(val_results.box.mp),
            "recall_mean": float(val_results.box.mr),
            "map50": float(val_results.box.map50),
            "map50_95": float(val_results.box.map),
        }
    except Exception:
        box_metrics = {
            "precision_mean": None,
            "recall_mean": None,
            "map50": None,
            "map50_95": None,
        }

    names = read_class_names_from_yaml(data_yaml)
    dataset_path = None

    for line in data_yaml.read_text(encoding="utf-8").splitlines():
        if line.startswith("path:"):
            dataset_path = Path(line.split(":", 1)[1].strip())

    if dataset_path is None:
        raise RuntimeError("Could not read dataset path from data.yaml")

    test_images_dir = dataset_path / "images" / args.split
    test_labels_dir = dataset_path / "labels" / args.split

    y_true = []
    y_pred = []
    rows = []

    if test_images_dir.exists():
        image_files = [
            p for p in sorted(test_images_dir.iterdir())
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        ]

        for img_path in image_files:
            label_path = test_labels_dir / f"{img_path.stem}.txt"
            true_class = get_true_class_from_label(label_path)

            pred_class = -1
            pred_conf = 0.0

            predictions = model.predict(
                source=str(img_path),
                imgsz=args.imgsz,
                conf=args.conf,
                verbose=False,
            )

            if predictions and predictions[0].boxes is not None and len(predictions[0].boxes) > 0:
                boxes = predictions[0].boxes
                best_idx = int(boxes.conf.argmax().item())
                pred_class = int(boxes.cls[best_idx].item())
                pred_conf = float(boxes.conf[best_idx].item())

            if true_class is not None:
                y_true.append(true_class)
                y_pred.append(pred_class)

            rows.append(
                {
                    "image_path": str(img_path),
                    "true_class_id": true_class,
                    "true_label": names.get(true_class, "Unknown"),
                    "predicted_class_id": pred_class,
                    "predicted_label": names.get(pred_class, "No Detection"),
                    "confidence": pred_conf,
                    "correct": true_class == pred_class,
                }
            )

    predictions_csv = output_dir / "test_predictions.csv"
    pd.DataFrame(rows).to_csv(predictions_csv, index=False)

    class_labels = sorted(list(names.keys()))
    report_labels = class_labels + [-1]
    report_names = [names[i] for i in class_labels] + ["No Detection"]

    if y_true:
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true,
            y_pred,
            labels=report_labels,
            average="weighted",
            zero_division=0,
        )

        report_text = classification_report(
            y_true,
            y_pred,
            labels=report_labels,
            target_names=report_names,
            zero_division=0,
        )

        cm = confusion_matrix(y_true, y_pred, labels=report_labels)

        report_path = output_dir / "classification_report.txt"
        report_path.write_text(report_text, encoding="utf-8")

        cm_csv = output_dir / "confusion_matrix.csv"
        pd.DataFrame(cm, index=report_names, columns=report_names).to_csv(cm_csv)

        cm_png = output_dir / "confusion_matrix.png"
        plt.figure(figsize=(12, 10))
        plt.imshow(cm, interpolation="nearest")
        plt.title("Actor Detection Confusion Matrix")
        plt.colorbar()
        ticks = range(len(report_names))
        plt.xticks(ticks, report_names, rotation=45, ha="right")
        plt.yticks(ticks, report_names)
        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.tight_layout()
        plt.savefig(cm_png, dpi=300)
        plt.close()
    else:
        accuracy = None
        precision = None
        recall = None
        f1 = None
        report_path = None
        cm_csv = None
        cm_png = None

    summary = {
        "weights": str(weights_path),
        "data_yaml": str(data_yaml),
        "split": args.split,
        "image_level_accuracy": accuracy,
        "image_level_weighted_precision": precision,
        "image_level_weighted_recall": recall,
        "image_level_weighted_f1": f1,
        "ultralytics_detection_metrics": box_metrics,
        "prediction_csv": str(predictions_csv),
        "classification_report": str(report_path) if report_path else None,
        "confusion_matrix_csv": str(cm_csv) if cm_csv else None,
        "confusion_matrix_png": str(cm_png) if cm_png else None,
    }

    summary_path = output_dir / "evaluation_summary.json"
    summary_path.write_text(json.dumps(summary, indent=4), encoding="utf-8")

    print("=" * 72)
    print("CloudSync Insight - YOLO Actor Model Evaluation")
    print("=" * 72)
    print(f"mAP50:       {box_metrics.get('map50')}")
    print(f"mAP50-95:    {box_metrics.get('map50_95')}")
    print(f"Precision:   {box_metrics.get('precision_mean')}")
    print(f"Recall:      {box_metrics.get('recall_mean')}")
    print(f"Accuracy:    {accuracy}")
    print(f"F1 Score:    {f1}")
    print()
    print("Saved files:")
    print(f"- {summary_path}")
    print(f"- {predictions_csv}")
    if report_path:
        print(f"- {report_path}")
    if cm_csv:
        print(f"- {cm_csv}")
    if cm_png:
        print(f"- {cm_png}")
    print("=" * 72)


def main():
    parser = argparse.ArgumentParser(
        description="CloudSync Insight YOLO actor dataset preparation, training, and evaluation pipeline."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--raw-dir", default="image_recognition/dataset/raw")
    prepare_parser.add_argument("--out-dir", default="image_recognition/yolo_actor_dataset")
    prepare_parser.add_argument("--width", type=int, default=1920)
    prepare_parser.add_argument("--height", type=int, default=1080)
    prepare_parser.add_argument("--train-ratio", type=float, default=0.70)
    prepare_parser.add_argument("--val-ratio", type=float, default=0.15)
    prepare_parser.add_argument("--seed", type=int, default=42)

    train_parser = subparsers.add_parser("train")
    train_parser.add_argument("--data", default="image_recognition/yolo_actor_dataset/data.yaml")
    train_parser.add_argument("--model", default="yolov8n.pt")
    train_parser.add_argument("--epochs", type=int, default=3)
    train_parser.add_argument("--imgsz", type=int, default=640)
    train_parser.add_argument("--batch", type=int, default=2)
    train_parser.add_argument("--project", default="image_recognition/runs")
    train_parser.add_argument("--name", default="actor_yolo_detector")

    eval_parser = subparsers.add_parser("evaluate")
    eval_parser.add_argument("--weights", default="image_recognition/runs/actor_yolo_detector/weights/best.pt")
    eval_parser.add_argument("--data", default="image_recognition/yolo_actor_dataset/data.yaml")
    eval_parser.add_argument("--split", default="test")
    eval_parser.add_argument("--imgsz", type=int, default=640)
    eval_parser.add_argument("--conf", type=float, default=0.25)
    eval_parser.add_argument("--output-dir", default="image_recognition/results/yolo_evaluation")

    args = parser.parse_args()

    if args.command == "prepare":
        prepare_dataset(args)
    elif args.command == "train":
        train_model(args)
    elif args.command == "evaluate":
        evaluate_model(args)


if __name__ == "__main__":
    main()
