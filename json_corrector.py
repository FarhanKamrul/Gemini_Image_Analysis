'''
import json

# Load the JSON file
with open("twitter_analysis_results.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Function to parse embedded JSON in "response" field
def parse_embedded_json(item):
    try:
        # Parse the "response" field as JSON if it is a string containing JSON data
        if "response" in item and isinstance(item["response"], str):
            # Remove backticks or additional JSON code wrappers
            raw_json_str = item["response"].replace("```json", "").replace("```", "")
            # Parse the JSON string and replace the "response" field with parsed data
            item["response"] = json.loads(raw_json_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing embedded JSON: {e}")

# Iterate over each item and fix the "response" field formatting
for item in data:
    parse_embedded_json(item)

# Save the corrected JSON back to a file
with open("twitter_analysis_results_corrected.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4)
'''

import json
import re

# Load the JSON file
input_file = "twitter_analysis_results_corrected.json"
output_file = "twitter_analysis_results_fixed.json"

with open(input_file, "r", encoding="utf-8") as file:
    data = json.load(file)

# Function to clean and parse embedded JSON strings
def parse_embedded_json(item):
    if "response" in item and isinstance(item["response"], str):
        # Remove any backticks and extract the JSON-like part
        raw_json_str = re.sub(r"```json|```", "", item["response"])
        
        try:
            # Parse the cleaned string as JSON and replace "response" field
            item["response"] = json.loads(raw_json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing embedded JSON: {e}")

# Iterate through each item in the data and fix the "response" field
for item in data:
    parse_embedded_json(item)

# Save the fixed JSON to a new file
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4)

print(f"Fixed JSON file saved as {output_file}")
