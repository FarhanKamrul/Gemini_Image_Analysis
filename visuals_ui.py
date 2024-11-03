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

# Define visualization functions with explanations
def bar_plot_mean_sentiment_scores():
    print("Visualization: Mean Sentiment Scores by Candidate")
    print("Interpretation: Shows average sentiment scores. Higher bars indicate stronger expressions of that sentiment for each candidate.")
    mean_sentiments = combined_df.groupby('candidate')[sentiment_columns].mean().reset_index()
    mean_sentiment_melted = mean_sentiments.melt(id_vars='candidate', var_name='Sentiment', value_name='Mean Score')
    plt.figure(figsize=(14, 8))
    sns.barplot(data=mean_sentiment_melted, x='Sentiment', y='Mean Score', hue='candidate', palette='coolwarm')
    plt.title('Mean Sentiment Scores by Candidate')
    plt.xlabel('Sentiment Type')
    plt.ylabel('Average Score')
    plt.xticks(rotation=45)
    plt.legend(title='Candidate')
    plt.tight_layout()
    plt.show()

def box_plot_sentiment_distribution():
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

def violin_plot_density_distribution():
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

def heatmap_correlation():
    for candidate in ['Trump', 'Kamala']:
        print(f"Visualization: Sentiment Correlation Matrix for {candidate}")
        print("Interpretation: Highlights correlations between sentiments. Strong correlations (closer to 1 or -1) suggest frequent co-occurrence.")
        candidate_df = combined_df[combined_df['candidate'] == candidate]
        corr_matrix = candidate_df[sentiment_columns].corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title(f'Sentiment Correlation Matrix for {candidate}')
        plt.show()

def radar_chart_mean_sentiments():
    print("Visualization: Radar Chart of Mean Sentiment Scores")
    print("Interpretation: Displays mean sentiment levels in a circular layout, useful for quick sentiment profile comparisons.")
    mean_sentiments = combined_df.groupby('candidate')[sentiment_columns].mean()
    labels = sentiment_columns
    num_vars = len(labels)
    angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
    angles += angles[:1]
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)
    for candidate in mean_sentiments.index:
        values = mean_sentiments.loc[candidate].tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=candidate)
        ax.fill(angles, values, alpha=0.25)
    plt.xticks(angles[:-1], labels)
    plt.title('Radar Chart of Mean Sentiment Scores by Candidate')
    plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
    plt.show()

def stacked_bar_sentiment_polarity():
    def sentiment_category(score):
        if isinstance(score, (int, float)):
            if score > 0:
                return 'Positive'
            elif score < 0:
                return 'Negative'
            else:
                return 'Neutral'
        return 'Neutral'
    print("Visualization: Stacked Bar Plot of Sentiment Polarity Counts")
    print("Interpretation: Shows counts of positive, neutral, and negative sentiments per candidate. Useful for visualizing sentiment polarity balance.")
    sentiment_counts = combined_df[sentiment_columns + ['candidate']].applymap(sentiment_category)
    sentiment_counts = sentiment_counts.melt(id_vars='candidate', var_name='Sentiment', value_name='Category')
    sentiment_counts = sentiment_counts.groupby(['candidate', 'Sentiment', 'Category']).size().unstack(fill_value=0)
    sentiment_counts.plot(kind='bar', stacked=True, figsize=(12, 8), colormap='coolwarm')
    plt.title('Stacked Bar Plot of Sentiment Polarity Counts by Candidate')
    plt.xlabel('Sentiment Type')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend(title='Sentiment Polarity')
    plt.tight_layout()
    plt.show()

# Console-based UI for visualization selection
while True:
    print("\nSelect a visualization to view:")
    print("1. Mean Sentiment Scores by Candidate (Bar Plot)")
    print("2. Sentiment Score Distribution by Candidate (Box Plot)")
    print("3. Density and Distribution of Sentiment Scores (Violin Plot)")
    print("4. Sentiment Correlation Matrix (Heatmap)")
    print("5. Radar Chart of Mean Sentiment Scores")
    print("6. Stacked Bar Plot of Sentiment Polarity Counts")
    print("0. Exit")
    
    choice = input("Enter your choice (0-6): ")
    
    if choice == '1':
        bar_plot_mean_sentiment_scores()
    elif choice == '2':
        box_plot_sentiment_distribution()
    elif choice == '3':
        violin_plot_density_distribution()
    elif choice == '4':
        heatmap_correlation()
    elif choice == '5':
        radar_chart_mean_sentiments()
    elif choice == '6':
        stacked_bar_sentiment_polarity()
    elif choice == '0':
        print("Exiting the program.")
        break
    else:
        print("Invalid choice, please enter a number between 0 and 6.")
