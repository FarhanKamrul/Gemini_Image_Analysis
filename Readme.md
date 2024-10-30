# Twitter Sentiment Analysis Application

This is a research tool developed for the Fall 2024 'Computational Social Science' course at New York University Abu Dhabi.

## Instructions

#### Creating API keys

1. Create a file called .env
2. Go to [Gemini API for Developers](https://ai.google.dev/?utm_source=website&utm_medium=referral&utm_campaign=geminichat&utm_content) and generate an API key.
3. Paste the API key in the .env file as GEMINI_API_KEY1.
4. You have to create a few other accounts and add GEMINI_API_KEY2, GEMINI_API_KEY3, and GEMINI_API_KEY4.

#### Microsoft Edge Driver

1. Download the Microsoft Edge Driver at: `/edgedriver_win64/msedgedriver.exe`

This has implications for the Screenshots.py program. Adopt it for Mac OS if you have one.

#### Running the application

1. Paste the Tweet links on to `trumptweets.csv`.
2. `python Screenshots.py` on the terminal will capture the screenshots. Modify to adjust the number of screenshots per page. Screenshots will be automatically captured unless you follow the manual controls below.
   - Manual Controls: Pressing `=` will pause/resume the screenshot capture and `-` to stop capturing on the current link and move on to the next.
3. Run `python Main.py` on the terminal to process the screenshots. The data will be stored in the `twitter_analysis_results.json` file.
4. Convert the data to CSV format for easier analysis. I'll provide a script for that later.
