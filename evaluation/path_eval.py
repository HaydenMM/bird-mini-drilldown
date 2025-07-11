import json
import argparse
import sqlite3
from pathlib import Path
from evaluation_utils import execute_sql, calculate_ex  # assuming you have these
from func_timeout import func_timeout, FunctionTimedOut

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def log_result(entry, pred_sql, pred_result, gt_result, diff, error=None):
    return {
        "question_id": entry["question_id"],
        "db_id": entry["db_id"],
        "gt_query": entry.get("SQL", ""),
        "predicted_query": pred_sql,
        "correct": pred_result,
        "error": error,
        "difficulty": diff
    }

def execute_safe(predicted_sql, ground_truth, db_path, sql_dialect, calculate_func, timeout=10.0):
    try:
        print("\n[Executing SQL]")
        print(f"  predicted_sql: {predicted_sql}")
        print(f"  ground_truth:  {ground_truth}")
        print(f"  db_path:       {db_path}")
        print(f"  dialect:       {sql_dialect}")
        print(f"  calculate_fn:  {calculate_func.__name__}")

        result = func_timeout(timeout, execute_sql, args=(predicted_sql, ground_truth, db_path, sql_dialect, calculate_func))
        print(f"  → Execution Result: {result}")
        return result, None
    except FunctionTimedOut:
        print("  → [Timeout Error]")
        return None, "timeout"
    except Exception as e:
        print(f"  → [Execution Error]: {e}")
        return None, str(e)

def evaluate_trace(pred_path, gt_path, db_dir, sql_dialect, calculate_func):
    predictions = load_json(pred_path)
    ground_truths = load_json(gt_path)

    logs = []
    current_path = []

    for i, gt_entry in enumerate(ground_truths):
        pred_sql = predictions[str(i)]  # assuming keys are "0", "1", ...
        db_path = Path(db_dir) / gt_entry["db_id"] / f"{gt_entry['db_id']}.sqlite"

        # Pass the sql_dialect and calculate_func to execute_safe
        pred_res, pred_err = execute_safe(pred_sql, gt_entry["SQL"], db_path, sql_dialect, calculate_func)
        gt_res, gt_err = execute_safe(gt_entry["SQL"], gt_entry["SQL"], db_path, sql_dialect, calculate_func)

        diff = gt_entry["difficulty"]

        entry_log = log_result(gt_entry, pred_sql, pred_res, gt_res, diff, error=pred_err)
        current_qid = current_path.append(entry_log)

        print(gt_entry)
        
        # Reset path when original query is encountered
        if gt_entry.get("is_original", False):
            if current_path:
                logs.append({"question_id": current_qid, "path": current_path})
            current_path = []
            
            current_qid = gt_entry["question_id"]

    if current_path:
        logs.append({"question_id": current_qid, "path": current_path})
        

    return logs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--predicted_sql_path", required=True)
    parser.add_argument("--ground_truth_path", required=True)
    parser.add_argument("--db_root_path", required=True)
    parser.add_argument("--output_log_path", default="path_eval_log.json")
    parser.add_argument("--sql_dialect", required=True, help="The SQL dialect (e.g., 'sqlite')")
    args = parser.parse_args()

    logs = evaluate_trace(
        args.predicted_sql_path,
        args.ground_truth_path,
        args.db_root_path,
        args.sql_dialect,
        calculate_ex  # from evaluation_utils
    )

    with open(args.output_log_path, "w") as f:
        json.dump(logs, f, indent=2)
    print(f"\n✅ Evaluation complete. Logs written to: {args.output_log_path}")

if __name__ == "__main__":
    main()
