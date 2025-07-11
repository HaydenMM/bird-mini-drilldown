import json

def has_inconsistent_path(path):
    """Returns True if correctness values are inconsistent within a path."""
    correctness = [entry.get("correct") for entry in path]
    # Remove None for basic inconsistency check, but still count change to/from None as inconsistent
    return len(set(correctness)) > 1

def filter_inconsistent_paths(data):
    """Filters the dataset to only include entries with inconsistent correctness in their path."""
    return [entry for entry in data if has_inconsistent_path(entry["path"])]

# Load your original file
with open("/Users/hmmoore/Desktop/mini_dev/evaluation/path_eval_log.json", "r") as f:
    original_data = json.load(f)

# Filter inconsistent paths
inconsistent_entries = filter_inconsistent_paths(original_data)

# Save to new JSON
with open("inconsistent_paths_only.json", "w") as f:
    json.dump(inconsistent_entries, f, indent=2)
