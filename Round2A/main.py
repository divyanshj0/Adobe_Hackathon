# main.py
import json
from processor import process_documents

if __name__ == "__main__":
    # Load input JSON with document list, persona, and task
    with open("sample_input.json", "r") as f:
        input_payload = json.load(f)

    # Run document analysis
    output = process_documents(input_payload)

    # Write output to file
    with open("outputs/output.json", "w") as f:
        json.dump(output, f, indent=4)

    print("✅ Output saved to outputs/output.json")
