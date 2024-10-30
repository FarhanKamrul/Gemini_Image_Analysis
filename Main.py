import os
import google.generativeai as genai
from google.generativeai.types import safety_types
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

# Path to completeness reference image and screenshots root folder
completeness_path = "Completeness.jpg"
screenshots_root_folder = "Screenshots/trump/replies"

# Updated prompt to improve sentiment analysis
prompt = (
    "Analyze the given image files. Extract any relevant Twitter interaction details for each complete Tweet, Reply, or Quote, ignoring incomplete ones. "
    "The first image shows a sample difference between complete and incomplete tweet.\n\n"
    "Only Analyze the second image. Provide the details in the following JSON format: \n\n"
    "{\n"
    "  \"tweets\": [\n"
    "    {\n"
    "      \"completeness\": \"\",  # Possible values: 1 (complete), 0 (incomplete)\n"
    "      \"content_type\": \"tweet\",  # Possible values: original tweet (only Donald J. Trump's Tweets), reply (All other Tweets)\n"
    "      \"text_body\": \"\",  # Extracted text content from the tweet/reply/quote\n"
    "      \"username\": \"\",  # Username of the tweet\n"
    "      \"image_text_description\": \"\", # Description of the image (with emotional traits) associated with the tweet. If no image, leave empty. \n"
    "      \"likes\": 0,\n"
    "      \"replies\": 0,\n"
    "      \"retweets\": 0,\n"
    "      \"views\": 0,\n"
    "      \"time_of_post\": \"\",  # Time when the content was posted\n"
    "      \"sentiment_scores\": {  # Scored between -1 to 1, accounting for both text and image. 0 indicates not present, -1 indicates extreme opposite and 1 indicates extreme value for said sentiment\n"
    "        \"supportive\": 0.0,    # -1: strongly against, 0: neutral, 1: strongly supportive\n"
    "        \"hostile\": 0.0,       # -1: extremely friendly, 0: neutral, 1: extremely hostile\n"
    "        \"sarcastic\": 0.0,     # -1: no sarcasm, 1: highly sarcastic\n"
    "        \"ambivalent\": 0.0,    # -1: no mixed feelings, 1: extremely ambivalent\n"
    "        \"nationalist\": 0.0,   # -1: anti-nationalist, 1: highly nationalist\n"
    "        \"anti_elite\": 0.0,    # -1: pro-elite, 1: highly anti-elite\n"
    "        \"fearful\": 0.0,       # -1: no fear, 1: extreme fear present\n"
    "        \"optimistic\": 0.0,    # -1: extremely pessimistic, 1: highly optimistic\n"
    "        \"skeptical\": 0.0,     # -1: not skeptical, 1: highly skeptical\n"
    "        \"disengaged\": 0.0     # -1: highly engaged, 1: extremely disengaged\n"
    "      }\n"
    "    }\n"
    "  ]\n"
    "}"
)
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

# Loop through each folder in the screenshots root folder and process the PNG files
results = []
output_file = "twitter_analysis_results.json"

for folder_name in os.listdir(screenshots_root_folder):
    folder_path = os.path.join(screenshots_root_folder, folder_name)

    # Check if it's a directory and treat it as a tweet ID folder
    if os.path.isdir(folder_path):
        tweet_id = folder_name

        for file_name in os.listdir(folder_path):
            if file_name.endswith(".png"):
                file_path = os.path.join(folder_path, file_name)

                retries = 0
                max_retries = len(api_keys)

                while retries < max_retries:
                    try:
                        # Upload the completeness reference image again after switching keys
                        completeness_reference = genai.upload_file(completeness_path)
                        # Upload the screenshot
                        file_reference = genai.upload_file(file_path)
                        print(f"Uploaded screenshot: {file_name} from folder: {tweet_id}")

                        # Send request to the model with text prompt and the two images
                        response = model.generate_content(
                            [prompt, completeness_reference, file_reference]
                        )

                        # Store response JSON with the tweet ID
                        response_data = {
                            "tweet_id": tweet_id,
                            "file_name": file_name,
                            "response": response.text
                        }
                        results.append(response_data)

                        # Save results to a JSON file after processing each image
                        try:
                            with open(output_file, "w") as json_file:
                                json.dump(results, json_file, indent=4)
                            print(f"Results saved to {output_file} after processing {file_name}")
                        except Exception as e:
                            print(f"Error saving results to JSON file after processing {file_name}: {e}")

                        break

                    except Exception as e:
                        print(f"Error processing {file_name} in folder {tweet_id} with API key {current_key_index + 1}: {e}")

                        # Cycle to the next API key regardless of error type
                        current_key_index = (current_key_index + 1) % len(api_keys)
                        if current_key_index == 0:
                            print("All API keys exhausted. Waiting for 30 seconds before retrying...")
                            time.sleep(30)
                        configure_api()
                        model = create_model()

                    retries += 1

# Save any remaining results to a JSON file after processing all images
try:
    with open(output_file, "w") as json_file:
        json.dump(results, json_file, indent=4)
    print(f"Final results saved to {output_file}")
except Exception as e:
    print(f"Error saving final results to JSON file: {e}")


