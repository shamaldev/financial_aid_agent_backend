import json


def load_json(file_path):
    try:
        with open(file_path) as f:
            policy_details = json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return {}

    policy_details = {k: v["summary"] for k, v in policy_details.items()}
    
    return policy_details