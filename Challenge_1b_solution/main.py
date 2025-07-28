# main.py
import json
import os
from processor import process_documents

if __name__ == "__main__":
    input_path = os.path.join("input", "sample_input.json")
    output_path = os.path.join("output", "output.json")

    with open(input_path, "r") as f:
        input_payload = json.load(f)

    output = process_documents(input_payload)

    with open(output_path, "w") as f:
        json.dump(output, f, indent=4)

    print("✅ Output saved to", output_path)
