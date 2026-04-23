import pandas as pd
import os
import config
from validation.backtesting import run_full_backtest
from baselines.models import run_all_baselines

def main():
    print("Loading data...")
    losses_df = pd.read_csv(os.path.join(config.DATA_DIR, "negative_log_returns.csv"), index_col=0, parse_dates=True)
    labels_df = pd.read_csv(os.path.join(config.DATA_DIR, "rolling_cluster_labels.csv"), index_col=0, parse_dates=True)

    print("\n" + "─" * 60)
    print("  STAGE 6 / 9 — OUT-OF-SAMPLE BACKTESTING (FAST RUN)")
    print("─" * 60)
    
    print(f"\n  Train period:      up to {config.TRAIN_END}")
    print(f"  Test  period:      {config.TEST_START} onward")
    print(f"  Backtest horizon:  {config.BACKTEST_HORIZON} trading days")
    backtest_results = run_full_backtest(labels_df, horizon=config.BACKTEST_HORIZON,
                                         test_start=config.TEST_START)
    print("\n  Signal-Quality Metrics (EVT-Clustering, TEST SET ONLY):")
    print(backtest_results.to_string())

    print("\n" + "─" * 60)
    print("  STAGE 7 / 9 — BASELINE MODEL COMPARISONS (FAST RUN)")
    print("─" * 60)
    
    baseline_labels_all = run_all_baselines(losses_df)
    baseline_backtest_records = []

    for method, bl_labels in baseline_labels_all.items():
        bl_backtest = run_full_backtest(bl_labels, horizon=config.BACKTEST_HORIZON,
                                         test_start=config.TEST_START)
        agg = bl_backtest.loc["AGGREGATE"]
        baseline_backtest_records.append({
            "Method":        method,
            "TP":            agg["TP"],
            "FP":            agg["FP"],
            "FN":            agg["FN"],
            "Precision":     agg["Precision"],
            "Recall":        agg["Recall"],
            "F1":            agg["F1"],
            "mean_lead_time": agg["mean_lead_time"],
        })

    our_agg = backtest_results.loc["AGGREGATE"]
    baseline_backtest_records.insert(0, {
        "Method":        "EVT-Clustering (Ours)",
        "TP":            our_agg["TP"],
        "FP":            our_agg["FP"],
        "FN":            our_agg["FN"],
        "Precision":     our_agg["Precision"],
        "Recall":        our_agg["Recall"],
        "F1":            our_agg["F1"],
        "mean_lead_time": our_agg["mean_lead_time"],
    })

    comparison_df = pd.DataFrame(baseline_backtest_records).set_index("Method")
    print("\n  ╔══ Baseline Comparison Summary ══╗")
    print(comparison_df.to_string())

if __name__ == "__main__":
    main()
