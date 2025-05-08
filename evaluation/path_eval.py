import json
import argparse
import sqlite3
from pathlib import Path
from evaluation_utils import execute_sql, calculate_ex  # assuming you have these
from func_timeout import func_timeout, FunctionTimedOut

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def log_result(entry, pred_result, gt_result, error=None):
    return {
        "question_id": entry["question_id"],
        "db_id": entry["db_id"],
        "query": entry.get("SQL", ""),
        "predicted_result": pred_result,
        "gt_result": gt_result,
        "correct": pred_result == gt_result,
        "error": error
    }

def execute_safe(predicted_sql, ground_truth, db_path, sql_dialect, calculate_func, timeout=10.0):
    try:
        # Print all arguments to check their values
        # print(f"Executing SQL with the following arguments:")
        # print(f"predicted_sql: {predicted_sql}")
        # print(f"ground_truth: {ground_truth}")
        # print(f"db_path: {db_path}")
        # print(f"sql_dialect: {sql_dialect}")
        # print(f"calculate_func: {calculate_func}")
        
        # Execute the SQL with the given arguments, including the timeout
        result = func_timeout(timeout, execute_sql, args=(predicted_sql, ground_truth, db_path, sql_dialect, calculate_func))
        print(f"SQL execution result: {result}")
        return result, None
    except FunctionTimedOut:
        return None, "timeout"
    except Exception as e:
        return None, str(e)



def evaluate_trace(pred_path, gt_path, db_dir, sql_dialect, calculate_func):
    predictions = load_json(pred_path)
    ground_truths = load_json(gt_path)

    logs = []
    current_path = []
    current_qid = None

    for i, gt_entry in enumerate(ground_truths):
        pred_sql = predictions[str(i)]  # assuming keys are "0", "1", ...
        db_path = Path(db_dir) / gt_entry["db_id"] / f"{gt_entry['db_id']}.sqlite"

        qid = gt_entry["question_id"]

        # When question_id changes, finalize previous path
        if current_qid is not None and qid != current_qid:
            logs.append({"question_id": current_qid, "path": current_path})
            current_path = []

        # Update current_qid for new group
        current_qid = qid

        # Execute SQL prediction and ground truth
        pred_res, pred_err = execute_safe(pred_sql, gt_entry["SQL"], db_path, sql_dialect, calculate_func)
        gt_res, gt_err = execute_safe(gt_entry["SQL"], gt_entry["SQL"], db_path, sql_dialect, calculate_func)

        # Log the result
        entry_log = log_result(gt_entry, pred_res, gt_res, error=pred_err or gt_err)
        current_path.append(entry_log)

    # Final path
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

    # Pass sql_dialect and calculate_func (imported from evaluation_utils) to evaluate_trace
    logs = evaluate_trace(
        args.predicted_sql_path,
        args.ground_truth_path,
        args.db_root_path,
        args.sql_dialect,
        calculate_ex  # assuming calculate_ex is defined in evaluation_utils
    )

    with open(args.output_log_path, "w") as f:
        json.dump(logs, f, indent=2)
    print(f"Results written to {args.output_log_path}")


if __name__ == "__main__":
    main()
