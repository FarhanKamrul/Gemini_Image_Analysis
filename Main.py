import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import time

# Load environment variables
load_dotenv()

# Set up API keys
api_keys = [
    os.getenv("GEMINI_API_KEY1"),
    os.getenv("GEMINI_API_KEY2"),
    os.getenv("GEMINI_API_KEY3"),
    os.getenv("GEMINI_API_KEY4")
]

# Remove any None values if some keys are not set
api_keys = [key for key in api_keys if key]

if not api_keys:
    print("Error: No valid API keys found in environment variables.")
    exit()

# Initialize the current key index
current_key_index = 0

# Function to configure API with current key
def configure_api():
    global current_key_index
    genai.configure(api_key=api_keys[current_key_index])
    print(f"Configured with API key: GEMINI_API_KEY{current_key_index + 1}")

# Initial API configuration
configure_api()

# Load the original JSON file
input_file = "twitter_analysis_results.json"
output_file = "twitter_analysis_results_1.json"

try:
    with open(input_file, "r") as file:
        data = json.load(file)
except Exception as e:
    print(f"Error loading input JSON file: {e}")
    exit()

# Function to generate prompt for each entry
def generate_prompt(entry):
    tweet_id = entry.get("tweet_id", "")
    file_name = entry.get("file_name", "")
    original_response = entry.get("response", "")

    prompt = (
        f"The response received is not in valid JSON format. Please convert the following response into a valid JSON object. "
        f"Follow this format strictly:\n\n"
        "{\n"
        "  \"tweet_id\": \"<tweet_id>\",\n"
        "  \"file_name\": \"<file_name>\",\n"
        "  \"response\": {\n"
        "    \"tweets\": [\n"
        "      {\n"
        "        \"completeness\": \"<1 or 0>\",\n"
        "        \"content_type\": \"<tweet or reply>\",\n"
        "        \"text_body\": \"<text content>\",\n"
        "        \"username\": \"<username>\",\n"
        "        \"image_text_description\": \"<description>\",\n"
        "        \"likes\": <integer>,\n"
        "        \"replies\": <integer>,\n"
        "        \"retweets\": <integer>,\n"
        "        \"views\": <integer>,\n"
        "        \"time_of_post\": \"<date and time>\",\n"
        "        \"promotional_or_irrelevant\": <true or false>,\n"
        "        \"pro_trump\": <float>,\n"
        "        \"hostile_to_trump\": <float>,\n"
        "        \"sarcastic_about_trump\": <float>,\n"
        "        \"ambivalent_about_trump\": <float>,\n"
        "        \"nationalist_pro_trump\": <float>,\n"
        "        \"anti_elite_pro_trump\": <float>,\n"
        "        \"fearful_pro_trump\": <float>,\n"
        "        \"optimistic_about_trump\": <float>,\n"
        "        \"skeptical_of_trump\": <float>,\n"
        "        \"disengaged_from_trump\": <float>\n"
        "      }\n"
        "    ]\n"
        "  }\n"
        "}\n\n"
        f"Convert the following response:\n{original_response}"
    )
    return prompt

# Function to send each entry to the model, validate, and store the corrected JSON
results = []
for entry in data:
    retries = 0
    max_retries = len(api_keys)

    while retries < max_retries:
        try:
            # Generate prompt from the entry
            prompt = generate_prompt(entry)
            response = genai.generate_content(prompt=prompt)
        except Exception as e:
            print(f"Error generating content for tweet_id: {entry.get('tweet_id', '')}: {e}")
            retries += 1
            continue

            # Parse and validate response
            try:
                response_data = json.loads(response["candidates"][0]["content"])
                response_data["tweet_id"] = entry.get("tweet_id", "")
                response_data["file_name"] = entry.get("file_name", "")
                results.append(response_data)
                print(f"Valid JSON received and processed for tweet_id: {entry.get('tweet_id', '')}")
                break

            except json.JSONDecodeError:
                print(f"Invalid JSON response received for tweet_id: {entry.get('tweet_id', '')}. Retrying with correction prompt.")

                # Retry logic with next API key
                current_key_index = (current_key_index + 1) % len(api_keys)
                configure_api()

                # If we've cycled through all keys, wait and retry
                if current_key_index == 0:
                    print("All API keys exhausted. Waiting for 30 seconds before retrying...")
                    time.sleep(30)

            retries += 1

# Save valid JSON entries to a new file
try:
    with open(output_file, "w") as file:
        json.dump(results, file, indent=4)
    print(f"Final results saved to {output_file}")
except Exception as e:
    print(f"Error saving final results to JSON file: {e}")
