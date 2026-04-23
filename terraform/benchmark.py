#!/usr/bin/env python3
import json
import time
from pathlib import Path

import lightgbm as lgb
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split


DATA_FILE = Path("creditcard.csv")
OUTPUT_FILE = Path("benchmark_result.json")
RANDOM_STATE = 42


def main() -> None:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Missing dataset: {DATA_FILE}. Download Kaggle dataset mlg-ulb/creditcardfraud first."
        )

    overall_start = time.perf_counter()

    load_start = time.perf_counter()
    df = pd.read_csv(DATA_FILE)
    load_time = time.perf_counter() - load_start

    if "Class" not in df.columns:
        raise ValueError("Dataset must contain a 'Class' target column.")

    x = df.drop(columns=["Class"])
    y = df["Class"]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    model = lgb.LGBMClassifier(
        objective="binary",
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    train_start = time.perf_counter()
    model.fit(
        x_train,
        y_train,
        eval_set=[(x_test, y_test)],
        eval_metric="auc",
        callbacks=[lgb.early_stopping(30, verbose=False)],
    )
    training_time = time.perf_counter() - train_start

    prob_start = time.perf_counter()
    y_prob = model.predict_proba(x_test)[:, 1]
    prediction_time = time.perf_counter() - prob_start
    y_pred = (y_prob >= 0.5).astype(int)

    one_row_start = time.perf_counter()
    _ = model.predict_proba(x_test.iloc[[0]])
    one_row_latency_ms = (time.perf_counter() - one_row_start) * 1000

    sample_size = min(1000, len(x_test))
    throughput_start = time.perf_counter()
    _ = model.predict_proba(x_test.iloc[:sample_size])
    throughput_elapsed = time.perf_counter() - throughput_start
    throughput_rows_per_sec = sample_size / throughput_elapsed if throughput_elapsed > 0 else float("inf")

    result = {
        "dataset": str(DATA_FILE),
        "rows": int(len(df)),
        "features": int(x.shape[1]),
        "class_distribution": {
            "negative": int((y == 0).sum()),
            "positive": int((y == 1).sum()),
        },
        "load_time_seconds": round(load_time, 4),
        "training_time_seconds": round(training_time, 4),
        "prediction_time_seconds": round(prediction_time, 4),
        "best_iteration": int(getattr(model, "best_iteration_", model.n_estimators)),
        "auc_roc": round(float(roc_auc_score(y_test, y_prob)), 6),
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 6),
        "f1_score": round(float(f1_score(y_test, y_pred, zero_division=0)), 6),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 6),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 6),
        "inference_latency_1_row_ms": round(one_row_latency_ms, 4),
        "inference_throughput_1000_rows_per_sec": round(float(throughput_rows_per_sec), 2),
        "total_runtime_seconds": round(time.perf_counter() - overall_start, 4),
    }

    OUTPUT_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("Benchmark completed.")
    print(json.dumps(result, indent=2))
    print(f"Saved metrics to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
