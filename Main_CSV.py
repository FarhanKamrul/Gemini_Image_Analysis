import os
import google.generativeai as genai
from google.generativeai.types import safety_types
from dotenv import load_dotenv
import csv
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

# Prompt
prompt = (
    "Analyze the given image files. Extract any relevant Twitter interaction details for each complete Tweet, Reply, or Quote, ignoring incomplete ones. "
    "The first image shows a sample difference between complete and incomplete tweet; and identifies objects within complete tweet.\n\n"
    "Only Analyze the second image. Provide the details in the following CSV format: \n\n"
    "Ensure all string values are properly escaped for CSV format. Use double quotes for text fields and escape any internal double quotes by doubling them.\n\n"
    'completeness,content_type,text_body,username,image_text_description,likes,replies,retweets,views,time_of_post,promotional_or_irrelevant,pro_trump,hostile_to_trump,sarcastic_about_trump,ambivalent_about_trump,nationalist_pro_trump,anti_elite_pro_trump,fearful_pro_trump,optimistic_about_trump,skeptical_of_trump,disengaged_from_trump\n'
    '1,"tweet","Tweet text here","username","Image description here",0,0,0,0,"time",false,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0\n'
    "\n"
    "Note: Ensure values are properly escaped for CSV format. Use double quotes for text fields and escape any internal double quotes by doubling them. Explanations for fields:\n"
    "completeness: 1 (complete), 0 (incomplete)\n"
    'content_type: "tweet" for original tweet (only Donald J. Trump\'s Tweets), "reply" for all other Tweets\n'
    "username: Username of the tweet. Be very careful, as there can be multiple visible usernames on the screenshot but only take the one attached to the tweet. Leave empty if none is found.\n"
    "image_text_description: Describe the image from the perspective of the creator of the image. Convey the associated emotions.\n"
    "promotional_or_irrelevant: true if the tweet is promotional or irrelevant to the campaign, false otherwise\n"
    "pro_trump: -1: strongly anti-Trump, 0: neutral, 1: strongly pro-Trump\n"
    "hostile_to_trump: -1: friendly to Trump, 0: neutral, 1: extremely hostile to Trump\n"
    "sarcastic_about_trump: -1: no sarcasm about Trump, 1: highly sarcastic about Trump\n"
    "ambivalent_about_trump: -1: clear stance on Trump, 1: extremely ambivalent about Trump\n"
    "nationalist_pro_trump: -1: anti-nationalist/anti-Trump, 1: highly nationalist in support of Trump\n"
    "anti_elite_pro_trump: -1: pro-elite/anti-Trump, 1: highly anti-elite in support of Trump\n"
    "fearful_pro_trump: -1: no fear, pro-Trump, 1: extreme fear, anti-Trump\n"
    "optimistic_about_trump: -1: pessimistic about Trump, 1: highly optimistic about Trump\n"
    "skeptical_of_trump: -1: trusting of Trump, 1: highly skeptical of Trump\n"
    "disengaged_from_trump: -1: highly engaged with Trump, 1: extremely disengaged from Trump"
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

# Function to parse and validate CSV output
def parse_and_validate_csv(csv_text):
    valid_lines = []
    csv_lines = csv_text.strip().split('\n')
    expected_fields = 21  # Number of fields we expect in each valid CSV row

    for line in csv_lines:
        fields = line.split(',')
        if len(fields) == expected_fields:
            try:
                # Validate some fields to ensure they're in the expected format
                int(fields[0])  # completeness should be an integer
                float(fields[11])  # pro_trump should be a float
                # Add more validations as needed
                valid_lines.append(line)
            except ValueError:
                print(f"Skipping invalid line: {line}")
        else:
            print(f"Skipping line with incorrect number of fields: {line}")

    return valid_lines

# Change the output file extension
output_file = "twitter_analysis_results.csv"

# Initialize the CSV file with headers
csv_headers = [
    "tweet_id", "file_name", "completeness", "content_type", "text_body", "username",
    "image_text_description", "likes", "replies", "retweets", "views", "time_of_post",
    "promotional_or_irrelevant", "pro_trump", "hostile_to_trump", "sarcastic_about_trump",
    "ambivalent_about_trump", "nationalist_pro_trump", "anti_elite_pro_trump",
    "fearful_pro_trump", "optimistic_about_trump", "skeptical_of_trump", "disengaged_from_trump"
]

with open(output_file, "w", newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(csv_headers)

for folder_name in os.listdir(screenshots_root_folder):
    folder_path = os.path.join(screenshots_root_folder, folder_name)
    if os.path.isdir(folder_path):
        tweet_id = folder_name
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".png"):
                file_path = os.path.join(folder_path, file_name)
                retries = 0
                max_retries = len(api_keys)
                while retries < max_retries:
                    try:
                        completeness_reference = genai.upload_file(completeness_path)
                        file_reference = genai.upload_file(file_path)
                        print(f"Uploaded screenshot: {file_name} from folder: {tweet_id}")
                        
                        response = model.generate_content(
                            [prompt, completeness_reference, file_reference]
                        )
                        
                        # Parse and validate the CSV response
                        valid_csv_lines = parse_and_validate_csv(response.text)
                        
                        for line in valid_csv_lines:
                            csv_data = line.split(',')
                            
                            # Prepare the row data
                            row_data = [tweet_id, file_name] + csv_data
                            
                            # Append the result to the CSV file
                            with open(output_file, "a", newline='', encoding='utf-8') as csv_file:
                                writer = csv.writer(csv_file)
                                writer.writerow(row_data)
                            
                            print(f"Valid result appended to {output_file} for {file_name}")
                        
                        break  # Break the retry loop if successful
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

print(f"All processing complete. Results saved to {output_file}")