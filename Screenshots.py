import csv
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
from PIL import Image
from io import BytesIO
import psutil
import threading
import keyboard

# Ensure all Edge processes are closed before starting a new session
def kill_edge_processes():
    try:
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] in ('msedge.exe', 'msedgedriver.exe'):
                psutil.Process(process.info['pid']).terminate()
        print("Successfully closed all running Edge and EdgeDriver processes.")
    except Exception as e:
        print(f"Error while closing Edge processes: {e}")

kill_edge_processes()

# Set the path to Edge WebDriver
edge_driver_path = '/edgedriver_win64/msedgedriver.exe'
service = Service(edge_driver_path)

# Specify the path to your Edge user data directory and the profile directory
edge_options = webdriver.EdgeOptions()
edge_options.add_argument(r"user-data-dir=C:\Users\Farhan\AppData\Local\Microsoft\Edge\User Data")
edge_options.add_argument(r"profile-directory=Default")
edge_options.add_argument("disable-gpu")
edge_options.add_argument("no-sandbox")

# Initialize Edge WebDriver
driver = webdriver.Edge(service=service, options=edge_options)
driver.maximize_window()  # Open browser in full-screen mode

# Base directory for screenshots
base_screenshots_dir = r"\screenshots\trump"

# Create directories if they don't exist
os.makedirs(base_screenshots_dir, exist_ok=True)

# Global variables for pausing, resuming, and stopping
is_paused = False
is_stopped = False

# Function to reset global control variables
def reset_control_variables():
    global is_paused, is_stopped
    is_paused = False
    is_stopped = False

# Function to monitor pause, resume, and stop keys
def monitor_keys():
    global is_paused, is_stopped
    while not is_stopped:
        if keyboard.is_pressed('='):
            is_paused = not is_paused
            print("Paused" if is_paused else "Resumed")
            time.sleep(1)  # Debounce delay

        if keyboard.is_pressed('-'):
            is_stopped = True
            print("Stopping...")
            break
        time.sleep(0.1)  # Prevents CPU overutilization

# Function to capture screenshots while scrolling through the tweet page
def capture_screenshots(tweet_link, save_dir):
    global is_paused, is_stopped
    print(f"Processing: {tweet_link}")

    # Validate that the tweet_link starts with "http"
    if not tweet_link.startswith("http"):
        print(f"Invalid URL: {tweet_link}")
        return

    try:
        # Open the tweet link
        driver.get(tweet_link)
        time.sleep(5)  # Wait for the tweet page to load

        screenshot_count = 0
        max_screenshots = 200  # Set limit to 200 screenshots

        # Start the key monitoring thread
        key_monitor_thread = threading.Thread(target=monitor_keys, daemon=True)
        key_monitor_thread.start()

        while screenshot_count < max_screenshots:
            if is_stopped:
                print("Stopped by user.")
                break

            if is_paused:
                time.sleep(1)
                continue

            # Capture a screenshot of the current page
            screenshot = driver.get_screenshot_as_png()
            image = Image.open(BytesIO(screenshot))

            # Save screenshot in the specified directory
            screenshot_filename = os.path.join(save_dir, f"screenshot_{screenshot_count}.png")
            image.save(screenshot_filename)
            screenshot_count += 1
            print(f"Captured screenshot {screenshot_count}")

            # Scroll down the page
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(2)  # Adjust based on how long it takes for new content to load

        # Reset control variables after finishing each link
        reset_control_variables()

    except Exception as e:
        print(f"Error processing {tweet_link}: {e}")

# Define the path to your CSV file
tweet_csv_path = r"\trumptweets.csv"

# Read each tweet link from the CSV and start the process
with open(tweet_csv_path, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        tweet_link = row[0]  # Get each tweet link

        # Debug print statement to check if the link is valid
        print(f"Read tweet link: {tweet_link}")

        # Create unique directory for each link's screenshots
        link_id = tweet_link.split('/')[-1]
        link_replies_dir = os.path.join(base_screenshots_dir, 'replies', link_id)
        os.makedirs(link_replies_dir, exist_ok=True)

        # Capture 200 screenshots from the original tweet (replies)
        capture_screenshots(tweet_link, link_replies_dir)

        # Reset stopping flag for the next link
        is_stopped = False

# Close the browser when done
driver.quit()
