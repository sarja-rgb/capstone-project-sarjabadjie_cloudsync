import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)


def load_predictions(predictions_path: Path) -> pd.DataFrame:
    if not predictions_path.exists():
        raise FileNotFoundError(
            f"Prediction file not found: {predictions_path}\n"
            "Create a CSV file with these columns: image_path,true_label,predicted_label,confidence"
        )

    df = pd.read_csv(predictions_path)

    required_columns = {"image_path", "true_label", "predicted_label"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}\n"
            "Required columns: image_path,true_label,predicted_label,confidence"
        )

    df["true_label"] = df["true_label"].astype(str)
    df["predicted_label"] = df["predicted_label"].astype(str)

    return df


def save_confusion_matrix(cm, labels, output_path: Path):
    plt.figure(figsize=(12, 10))
    plt.imshow(cm, interpolation="nearest")
    plt.title("Vision Model Confusion Matrix")
    plt.colorbar()

    tick_marks = range(len(labels))
    plt.xticks(tick_marks, labels, rotation=45, ha="right")
    plt.yticks(tick_marks, labels)

    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def evaluate_model(predictions_path: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_predictions(predictions_path)

    y_true = df["true_label"]
    y_pred = df["predicted_label"]

    labels = sorted(list(set(y_true) | set(y_pred)))

    accuracy = accuracy_score(y_true, y_pred)

    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=labels,
        average="macro",
        zero_division=0,
    )

    weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=labels,
        average="weighted",
        zero_division=0,
    )

    report_dict = classification_report(
        y_true,
        y_pred,
        labels=labels,
        output_dict=True,
        zero_division=0,
    )

    report_text = classification_report(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0,
    )

    cm = confusion_matrix(y_true, y_pred, labels=labels)

    summary = {
        "total_test_images": int(len(df)),
        "accuracy": float(accuracy),
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "macro_f1_score": float(macro_f1),
        "weighted_precision": float(weighted_precision),
        "weighted_recall": float(weighted_recall),
        "weighted_f1_score": float(weighted_f1),
        "labels": labels,
    }

    summary_path = output_dir / "evaluation_summary.json"
    report_txt_path = output_dir / "classification_report.txt"
    report_csv_path = output_dir / "classification_report.csv"
    confusion_csv_path = output_dir / "confusion_matrix.csv"
    confusion_png_path = output_dir / "confusion_matrix.png"

    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)

    with report_txt_path.open("w", encoding="utf-8") as file:
        file.write(report_text)

    pd.DataFrame(report_dict).transpose().to_csv(report_csv_path)

    pd.DataFrame(cm, index=labels, columns=labels).to_csv(confusion_csv_path)

    save_confusion_matrix(cm, labels, confusion_png_path)

    print("=" * 70)
    print("CloudSync Insight - Vision Model Evaluation Results")
    print("=" * 70)
    print(f"Prediction file: {predictions_path}")
    print(f"Total test images: {len(df)}")
    print()
    print(f"Accuracy:           {accuracy:.4f}")
    print(f"Macro Precision:    {macro_precision:.4f}")
    print(f"Macro Recall:       {macro_recall:.4f}")
    print(f"Macro F1 Score:     {macro_f1:.4f}")
    print(f"Weighted Precision: {weighted_precision:.4f}")
    print(f"Weighted Recall:    {weighted_recall:.4f}")
    print(f"Weighted F1 Score:  {weighted_f1:.4f}")
    print()
    print("Saved files:")
    print(f"- {summary_path}")
    print(f"- {report_txt_path}")
    print(f"- {report_csv_path}")
    print(f"- {confusion_csv_path}")
    print(f"- {confusion_png_path}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate a trained CloudSync Insight vision model using accuracy, precision, recall, F1 score, and confusion matrix."
    )

    parser.add_argument(
        "--predictions",
        default="image_recognition/results/vision_predictions.csv",
        help="Path to CSV file with columns: image_path,true_label,predicted_label,confidence",
    )

    parser.add_argument(
        "--output-dir",
        default="image_recognition/results/evaluation",
        help="Folder where evaluation results will be saved.",
    )

    args = parser.parse_args()

    evaluate_model(
        predictions_path=Path(args.predictions),
        output_dir=Path(args.output_dir),
    )


if __name__ == "__main__":
    main()
