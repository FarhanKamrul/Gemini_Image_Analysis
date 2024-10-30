import pandas as pd

# Load the CSV file into a DataFrame
csv_file_path = "twitter_analysis_CSV.csv"
df = pd.read_csv(csv_file_path)

# View summary statistics for the DataFrame
summary_statistics = df.describe()


# Save the summary statistics to a new CSV file (optional)
summary_output_file = "summary_statistics.csv"
summary_statistics.to_csv(summary_output_file)



# Print the summary statistics
print(summary_statistics)
