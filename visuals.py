import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from math import pi

# Set the directory containing the files
directory = 'C:/Users/Farhan/Desktop/Sem 7/Computational Social Science/Gemini_Image_Analysis'

# Load the datasets
trump_df = pd.read_csv(os.path.join(directory, 'trump_sentiment.csv'))
kamala_df = pd.read_csv(os.path.join(directory, 'kamala_sentiment.csv'))

# Add a new column to label each dataset
trump_df['candidate'] = 'Trump'
kamala_df['candidate'] = 'Kamala'

# Concatenate both dataframes
combined_df = pd.concat([trump_df, kamala_df], ignore_index=True)

# List of sentiment columns for analysis
sentiment_columns = [
    'supportive', 'hostile', 'sarcastic', 'ambivalent', 'nationalist', 
    'anti_elite', 'fearful', 'optimistic', 'skeptical', 'disengaged'
]

# Set a theme for clarity
sns.set_theme(style="whitegrid")

# 1. Bar Plot of Mean Sentiment Scores by Candidate
print("Visualization: Mean Sentiment Scores by Candidate")
print("Interpretation: Shows average sentiment scores. Higher bars indicate stronger expressions of that sentiment for each candidate.")
plt.figure(figsize=(14, 8))
mean_sentiments = combined_df.groupby('candidate')[sentiment_columns].mean().reset_index()
mean_sentiment_melted = mean_sentiments.melt(id_vars='candidate', var_name='Sentiment', value_name='Mean Score')
sns.barplot(data=mean_sentiment_melted, x='Sentiment', y='Mean Score', hue='candidate', palette='coolwarm')
plt.title('Mean Sentiment Scores by Candidate')
plt.xlabel('Sentiment Type')
plt.ylabel('Average Score')
plt.xticks(rotation=45)
plt.legend(title='Candidate')
plt.tight_layout()
plt.show()

# 2. Box Plot of Sentiment Score Distribution by Candidate
print("Visualization: Sentiment Score Distribution by Candidate")
print("Interpretation: Box plot shows score range and spread. Wider boxes indicate more variability in sentiment expressions.")
plt.figure(figsize=(14, 8))
sns.boxplot(data=combined_df.melt(id_vars=['candidate'], value_vars=sentiment_columns), 
            x='variable', y='value', hue='candidate', palette='coolwarm')
plt.title('Sentiment Score Distribution by Candidate')
plt.xlabel('Sentiment Type')
plt.ylabel('Score Distribution')
plt.xticks(rotation=45)
plt.legend(title='Candidate')
plt.tight_layout()
plt.show()

# 3. Violin Plot for Density and Distribution of Sentiment Scores
print("Visualization: Density and Distribution of Sentiment Scores")
print("Interpretation: Shows the density of scores. Thicker sections indicate where most scores fall for each candidate.")
plt.figure(figsize=(14, 8))
sns.violinplot(data=combined_df.melt(id_vars=['candidate'], value_vars=sentiment_columns), 
               x='variable', y='value', hue='candidate', split=True, palette='coolwarm')
plt.title('Density and Distribution of Sentiment Scores by Candidate')
plt.xlabel('Sentiment Type')
plt.ylabel('Density of Scores')
plt.xticks(rotation=45)
plt.legend(title='Candidate')
plt.tight_layout()
plt.show()

# 4. Heatmap of Sentiment Correlations by Candidate
for candidate in ['Trump', 'Kamala']:
    print(f"Visualization: Sentiment Correlation Matrix for {candidate}")
    print("Interpretation: Highlights correlations between sentiments. Strong correlations (closer to 1 or -1) suggest frequent co-occurrence.")
    candidate_df = combined_df[combined_df['candidate'] == candidate]
    corr_matrix = candidate_df[sentiment_columns].corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title(f'Sentiment Correlation Matrix for {candidate}')
    plt.show()

# Radar Chart of Mean Sentiment Scores by Candidate
print("Visualization: Radar Chart of Mean Sentiment Scores")
print("Interpretation: Displays mean sentiment levels in a circular layout, useful for quick sentiment profile comparisons.")

# Calculate mean sentiments
mean_sentiments = combined_df.groupby('candidate')[sentiment_columns].mean()

# Radar chart setup
labels = sentiment_columns
num_vars = len(labels)

# Compute angle of each axis
angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
angles += angles[:1]  # repeat the first angle to close the circle

plt.figure(figsize=(8, 8))
ax = plt.subplot(111, polar=True)

# Plot for each candidate
for candidate in mean_sentiments.index:
    values = mean_sentiments.loc[candidate].tolist()
    values += values[:1]  # repeat the first value to close the circle

    ax.plot(angles, values, linewidth=2, linestyle='solid', label=candidate)
    ax.fill(angles, values, alpha=0.25)

# Add labels and title
plt.xticks(angles[:-1], labels)
plt.title('Radar Chart of Mean Sentiment Scores by Candidate')
plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
plt.show()


# 6. Joint Plot (Scatter + Density) of Two Sentiments
print("Visualization: Joint Density Plot for Supportive vs Hostile")
print("Interpretation: Joint density plot highlights areas where sentiment pairs cluster or diverge.")
sns.jointplot(data=combined_df, x='supportive', y='hostile', hue='candidate', kind="kde", palette='coolwarm')
plt.suptitle('Joint Density Plot of Supportive vs Hostile Sentiments by Candidate', y=1.05)
plt.show()

# Strip plot for individual sentiment scores
plt.figure(figsize=(14, 8))
sns.stripplot(data=combined_df.melt(id_vars=['candidate'], value_vars=sentiment_columns), 
              x='variable', y='value', hue='candidate', dodge=True, palette='coolwarm', jitter=0.3)
plt.title('Strip Plot of Sentiment Scores by Candidate')
plt.xlabel('Sentiment Type')
plt.ylabel('Sentiment Score')
plt.xticks(rotation=45)
plt.legend(title='Candidate')
plt.tight_layout()
plt.show()

# 8. KDE Plot Grid for Sentiment Density
print("Visualization: KDE Plot Grid for Sentiment Density")
print("Interpretation: Each subplot shows the density of scores for a sentiment, split by candidate. Useful for comparison across sentiments.")
g = sns.FacetGrid(combined_df.melt(id_vars='candidate', value_vars=sentiment_columns), 
                  col='variable', hue='candidate', sharey=False, palette='coolwarm', col_wrap=3)
g.map(sns.kdeplot, 'value', fill=True, common_norm=False)
g.add_legend()
g.set_titles("{col_name}")
g.set_axis_labels("Sentiment Score", "Density")
plt.suptitle('Sentiment Score Density by Candidate (KDE)', y=1.02)
plt.tight_layout()
plt.show()

# 9. Stacked Bar Plot of Sentiment Polarity Counts
# Function to categorize sentiment based on score
def sentiment_category(score):
    if isinstance(score, (int, float)):  # Check if score is numeric
        if score > 0:
            return 'Positive'
        elif score < 0:
            return 'Negative'
        else:
            return 'Neutral'
    return 'Neutral'  # Default category for non-numeric values

# Apply sentiment categorization to relevant columns
print("Visualization: Stacked Bar Plot of Sentiment Polarity Counts")
print("Interpretation: Shows counts of positive, neutral, and negative sentiments per candidate. Useful for visualizing sentiment polarity balance.")

# Apply the categorization only to sentiment columns
sentiment_counts = combined_df[sentiment_columns + ['candidate']].applymap(sentiment_category)

# Reshape data for plotting
sentiment_counts = sentiment_counts.melt(id_vars='candidate', var_name='Sentiment', value_name='Category')
sentiment_counts = sentiment_counts.groupby(['candidate', 'Sentiment', 'Category']).size().unstack(fill_value=0)

# Plot stacked bar chart
sentiment_counts.plot(kind='bar', stacked=True, figsize=(12, 8), colormap='coolwarm')
plt.title('Stacked Bar Plot of Sentiment Polarity Counts by Candidate')
plt.xlabel('Sentiment Type')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.legend(title='Sentiment Polarity')
plt.tight_layout()
plt.show()

