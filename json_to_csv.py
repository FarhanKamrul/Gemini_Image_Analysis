import os
import google.generativeai as genai
from google.generativeai.types import safety_types
from dotenv import load_dotenv
import csv
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

# Initial configuration
configure_api()

# Define the model configuration
generation_config = {
    "temperature": 0.3,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

# Define safety settings
safety_settings = [
    {
        "category": safety_types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        "threshold": safety_types.HarmBlockThreshold.BLOCK_NONE
    },
    {
        "category": safety_types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        "threshold": safety_types.HarmBlockThreshold.BLOCK_NONE
    },
    {
        "category": safety_types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        "threshold": safety_types.HarmBlockThreshold.BLOCK_NONE
    },
    {
        "category": safety_types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        "threshold": safety_types.HarmBlockThreshold.BLOCK_NONE
    }
]

# Create the model instance using gemini-1.5-flash-8b
def create_model():
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-8b",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        print("Model created successfully.")
        return model
    except Exception as e:
        print(f"Error creating model: {e}")
        exit(1)

model = create_model()

# Load the original JSON file
input_file = "twitter_analysis_results.json"
output_file = "twitter_analysis_results_converted.csv"

try:
    with open(input_file, "r") as file:
        data = json.load(file)
except Exception as e:
    print(f"Error loading input JSON file: {e}")
    exit()

# Define headers based on the expected CSV format
csv_headers = [
    "tweet_id", "file_name", "completeness", "content_type", "text_body", "username",
    "image_text_description", "likes", "replies", "retweets", "views", "time_of_post",
    "promotional_or_irrelevant", "pro_trump", "hostile_to_trump", "sarcastic_about_trump",
    "ambivalent_about_trump", "nationalist_pro_trump", "anti_elite_pro_trump",
    "fearful_pro_trump", "optimistic_about_trump", "skeptical_of_trump", "disengaged_from_trump"
]

# Open CSV file for writing
with open(output_file, mode="w", newline="") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
    writer.writeheader()  # Write headers to CSV

    for entry in data:
        retries = 0
        max_retries = len(api_keys)
        prior_response_text = None  # To store previous response text for the retry prompt

        while retries < max_retries:
            try:
                # Create prompt to ask for CSV conversion with correct format example
                prompt = (
                    "Convert the following JSON entry to CSV format:\n\n"
                    f"{entry}\n\n"
                    "Ensure each JSON key has its own column in the CSV. If the entry is nested, please flatten it appropriately.\n"
                    "Format the output exactly as shown in this example:\n\n"
                    "tweet_id,file_name,completeness,content_type,text_body,username,image_text_description,likes,replies,retweets,views,time_of_post,promotional_or_irrelevant,pro_trump,hostile_to_trump,sarcastic_about_trump,ambivalent_about_trump,nationalist_pro_trump,anti_elite_pro_trump,fearful_pro_trump,optimistic_about_trump,skeptical_of_trump,disengaged_from_trump\n"
                    "1234567890,screenshot.png,1,tweet,\"Sample tweet text\",\"username123\",\"Description of the image\",100,20,50,200,\"2023-01-01 12:34:56\",false,0.5,0.2,0.0,0.0,0.1,-0.3,0.0,0.2,-0.1,0.3\n"
                )
                response = model.generate_content(prompt)

                # Parse the CSV response
                try:
                    # Extract CSV content from response text
                    csv_content = response.text.strip()
                    csv_lines = csv_content.splitlines()
                    csv_reader = csv.DictReader(csv_lines)

                    for row in csv_reader:
                        # Ensure all fields are accounted for before writing to CSV
                        csv_row = {field: row.get(field, "") for field in csv_headers}
                        writer.writerow(csv_row)

                    print(f"CSV data received and processed for tweet_id: {entry.get('tweet_id', '')}")
                    break

                except Exception as e:
                    print(f"Failed to parse CSV for tweet_id: {entry.get('tweet_id', '')}. Retrying with correction prompt.")

                    # Update prior response text for retry
                    correction_prompt = (
                        f"The following response was invalid CSV. Please correct it to ensure all keys are "
                        f"flattened into individual CSV columns following this structure:\n\n"
                        "tweet_id,file_name,completeness,content_type,text_body,username,image_text_description,likes,replies,retweets,views,time_of_post,promotional_or_irrelevant,pro_trump,hostile_to_trump,sarcastic_about_trump,ambivalent_about_trump,nationalist_pro_trump,anti_elite_pro_trump,fearful_pro_trump,optimistic_about_trump,skeptical_of_trump,disengaged_from_trump\n\n"
                        "Response:\n{prior_response_text or response.text}"
                    )
                    prior_response_text = response.text
                    response = model.generate_content(correction_prompt)

                retries += 1
                # Cycle API keys if necessary
                current_key_index = (current_key_index + 1) % len(api_keys)
                if current_key_index == 0:
                    print("All API keys exhausted. Waiting for 30 seconds before retrying...")
                    time.sleep(30)
                configure_api()

            except Exception as e:
                print(f"Error processing tweet_id {entry.get('tweet_id', '')} with API key {current_key_index + 1}: {e}")
                retries += 1

print(f"CSV file saved to {output_file}")
