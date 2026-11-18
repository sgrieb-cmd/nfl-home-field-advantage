"""
This file loads NFL game and play-by-play data, explores the
datasets, calculates statistics, and creates visualizations.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

from analysis import (
    team_home_away_summary,
    quarterback_summary,
    defensive_drive_summary,
    third_down_summary
)


def load_games():
    """Load NFL game results from 2015 through 2024."""
    # Read the game results dataset
    games = pd.read_csv('games.csv')

    # Create an empty list to store games from the selected seasons
    selected_games = []

    # Go through each game and check whether it is from 2015-2024
    for index, game in games.iterrows():
        if game['season'] in range(2015, 2025):
            selected_games.append(game)

    # Turn the selected games back into a DataFrame
    games = pd.DataFrame(selected_games)

    # Only use regular-season games
    games = games[games['game_type'] == 'REG']

    # Remove games that are missing either team's final score
    games = games.dropna(
        subset=['home_score', 'away_score']
    )

    return games


def load_play_by_play():
    """Load and combine the ten play-by-play datasets."""

    # These are the columns needed for the analysis
    columns_needed = [
        'season', 'game_id', 'season_type',
        'home_team', 'away_team', 'posteam', 'defteam',
        'drive', 'down', 'third_down_converted',
        'interception', 'pass_attempt', 'pass_touchdown',
        'complete_pass', 'passer_player_name', 'passing_yards'
    ]

    # Create a dictionary with an empty list for each column
    all_data = {}

    for column in columns_needed:
        all_data[column] = []

    # Load each year's play-by-play file separately
    for year in range(2015, 2025):

        # Create the filename using the current year
        filename = 'play_by_play_' + str(year) + '.csv'

        # Read the current year's dataset
        year_data = pd.read_csv(filename)

        # Go through each column that is needed
        for column in columns_needed:

            # Add every value from that column to the main list
            for value in year_data[column]:
                all_data[column].append(value)

    # Combine all the lists into one DataFrame
    pbp = pd.DataFrame(all_data)

    # Only use regular-season plays
    pbp = pbp[pbp['season_type'] == 'REG']

    return pbp


def describe_dataset(data, name):
    """Print information about a dataset."""

    # Print the name of the dataset being examined
    print('\n' + name)

    # Print the total number of rows and columns
    print('Number of rows:', len(data))
    print('Number of columns:', len(data.columns))

    # Print the names of every column
    print('\nColumn names:')
    for column in data.columns:
        print(column)

    # Count and print the missing values in each column
    print('\nMissing values:')
    for column in data.columns:
        missing = len(data) - len(data[column].dropna())
        print(column, ':', missing)

    # Print summary statistics for numerical columns
    print('\nNumerical summary:')
    for column in data:
        if data[column].mean() == data[column].mean():
            values = data[column].dropna()

            print(column)
            print('Mean:', values.mean())
            print('Standard deviation:', values.std())
            print('Minimum:', values.min())
            print('Median:', values.median())
            print('Maximum:', values.max())


def plot_team_results(team_stats):
    """Create graphs comparing team home and away results."""

    # Graph 1: Top 10 teams by home win percentage
    home_teams = []

    # Get each team's
    # name and home win percentage in a list
    for index, row in team_stats.iterrows():
        home_teams.append(
            (row['team'], row['home_win_pct'])
        )

    # Put the teams in order from highest to lowest
    # win percentage
    home_teams = sorted(
        home_teams, key=lambda team: team[1], reverse=True
    )

    # Select only the first 10 teams from the sorted list
    top_teams = home_teams[:10]

    # Create separate lists for team names and win percentages
    team_names = []
    win_percentages = []

    # Separate each team's name and percentage into the lists
    for team in top_teams:
        team_names.append(team[0])
        win_percentages.append(team[1])

    # Create the first graph using the top 10 teams
    plt.figure(figsize=(12, 6))
    plt.bar(team_names, win_percentages)

    # Add the graph title and axis labels
    plt.title('Top 10 NFL Teams by Home Win Percentage')
    plt.xlabel('NFL Team')
    plt.ylabel('Home Win Percentage')

    # Set the vertical axis to show percentages from 0 to 1
    plt.ylim(0, 1)

    # Adjust the graph layout and save the image
    plt.tight_layout()
    plt.savefig('figures/home_win_percentage.png')
    plt.close()

    # Graph 2: Home and away point differentials
    point_teams = []

    # Find the difference between each team's home and
    # away point differentials
    for index, row in team_stats.iterrows():
        difference = (
            row['home_point_diff'] - row['away_point_diff']
        )

        # Save the team name and both score differences
        # and their difference together
        point_teams.append((
            row['team'],
            row['home_point_diff'],
            row['away_point_diff'],
            difference
        ))

    # Put teams in order from biggest to smallest
    # to the smallest
    point_teams = sorted(
        point_teams, key=lambda team: team[3], reverse=True
    )

    # Create lists for team names and both point differentials
    team_names = []
    home_differences = []
    away_differences = []

    # Separate the information from each team's data
    for team in point_teams:
        team_names.append(team[0])
        home_differences.append(team[1])
        away_differences.append(team[2])

    # Create a position for each team on the horizontal axis
    positions = range(len(point_teams))

    # Set the width of each bar
    width = 0.35

    # Set spots for the home and away bars
    # so they appear next to each other
    home_positions = []
    away_positions = []

    for position in positions:
        home_positions.append(position - width / 2)
        away_positions.append(position + width / 2)

    # Create the home point differential bars
    plt.figure(figsize=(12, 6))
    plt.bar(
        home_positions, home_differences,
        width, label='Home'
    )

    # Create the away point differential bars
    plt.bar(
        away_positions, away_differences,
        width, label='Away'
    )

    # Add team names below the bars
    plt.xticks(positions, team_names)

    # Add the graph title, labels, and legend
    plt.title('Home vs. Away Point Differential')
    plt.xlabel('NFL Team')
    plt.ylabel('Average Point Differential')
    plt.legend()

    # Adjust the layout and save the second graph
    plt.tight_layout()
    plt.savefig('figures/home_away_point_difference.png')
    plt.close()


def plot_quarterback_results(qb_stats):
    """Create graphs comparing quarterback performance."""

    # Check whether there are any quarterback statistics
    if qb_stats.empty:
        print('No quarterbacks met the attempt requirement.')
        return

    # Find the quarterbacks with the most total passing attempts
    qb_attempts = qb_stats.groupby(
        'passer_player_name'
    )['attempts'].sum()

    # Sort the quarterbacks by their total attempts
    # Keep only the 30 quarterbacks with the most attempts
    top_qbs = sorted(
        qb_attempts.index,
        key=lambda name: qb_attempts[name],
        reverse=True
    )[:30]

    # Create empty lists to store each quarterback's results
    names = []
    home_completion = []
    away_completion = []
    home_yards = []
    away_yards = []

    # Go through each of the selected quarterbacks
    for name in top_qbs:

        # Select the statistics belonging to the current quarterback
        player = qb_stats[
            qb_stats['passer_player_name'] == name
        ]

        # Separate the quarterback's home and away statistics
        home = player[player['location'] == 'Home']
        away = player[player['location'] == 'Away']

        # Only include quarterbacks who have both home and away data
        if len(home) > 0 and len(away) > 0:

            # Save the quarterback's name
            names.append(name)

            # Save the home and away completion percentages
            home_completion.append(home.iloc[0]['completion_pct'])
            away_completion.append(away.iloc[0]['completion_pct'])

            # Save the home and away passing yards per attempt
            home_yards.append(home.iloc[0]['yards_per_attempt'])
            away_yards.append(away.iloc[0]['yards_per_attempt'])

    # Graph 3: Completion percentage
    # Create positions for the quarterbacks on the graph
    positions = range(len(names))

    # Set the width of the home and away bars
    width = 0.35

    # Move the home and away bars slightly apart
    home_positions = []
    away_positions = []

    for position in positions:
        home_positions.append(position - width / 2)
        away_positions.append(position + width / 2)

    # Create the completion percentage graph
    plt.figure(figsize=(12, 6))
    plt.bar(home_positions, home_completion, width, label='Home')
    plt.bar(away_positions, away_completion, width, label='Away')

    # Add quarterback names and graph labels
    plt.xticks(positions, names, rotation=90)
    plt.title('Quarterback Completion Percentage: Home vs. Away')
    plt.xlabel('Quarterback')
    plt.ylabel('Completion Percentage')
    plt.legend(title='Location')

    # Adjust the layout and save the graph
    plt.tight_layout()
    plt.savefig('figures/qb_completion_percentage.png')
    plt.close()

    # Graph 4: Passing yards per attempt
    # Use the same quarterback positions to compare passing efficiency
    plt.figure(figsize=(12, 6))
    plt.bar(home_positions, home_yards, width, label='Home')
    plt.bar(away_positions, away_yards, width, label='Away')

    # Add quarterback names and graph labels
    plt.xticks(positions, names, rotation=90)
    plt.title('Quarterback Passing Yards per Attempt')
    plt.xlabel('Quarterback')
    plt.ylabel('Passing Yards per Attempt')
    plt.legend(title='Location')

    # Adjust the layout and save the graph
    plt.tight_layout()
    plt.savefig('figures/qb_passing_efficiency.png')
    plt.close()


def plot_defensive_results(defense_stats, third_down_stats):
    """Create graphs comparing home and away defense."""

    # Graph 5: Defensive interception rate
    # Only create this graph if defensive statistics are available
    if not defense_stats.empty:

        # Get all of the unique defensive teams
        teams = defense_stats['defteam'].unique()

        # Create lists to store home and away interception rates
        home_rates = []
        away_rates = []
        team_names = []

        # Go through each defensive team
        for team in teams:

            # Select the statistics for the current team
            team_data = defense_stats[
                defense_stats['defteam'] == team
            ]

            # Separate the team's home and away statistics
            home = team_data[
                team_data['location'] == 'Home'
            ]

            away = team_data[
                team_data['location'] == 'Away'
            ]

            # Remove rows that are missing interception rates
            home = home.dropna(subset=['interception_rate'])
            away = away.dropna(subset=['interception_rate'])

            # Only include teams with both home and away results
            if len(home) > 0 and len(away) > 0:

                # Save the team name and its interception rates
                team_names.append(team)
                home_rates.append(home.iloc[0]['interception_rate'])
                away_rates.append(away.iloc[0]['interception_rate'])

        # Create positions for the teams on the graph
        positions = range(len(team_names))

        # Set the width of the bars
        width = 0.35

        # Position the home and away bars next to each other
        home_positions = []
        away_positions = []

        for position in positions:
            home_positions.append(position - width / 2)
            away_positions.append(position + width / 2)

        # Create the defensive interception rate graph
        plt.figure(figsize=(12, 6))
        plt.bar(home_positions, home_rates, width, label='Home')
        plt.bar(away_positions, away_rates, width, label='Away')

        # Add team names, graph title, labels, and legend
        plt.xticks(positions, team_names)
        plt.title('Defensive Interception Rate: Home vs. Away')
        plt.xlabel('NFL Team')
        plt.ylabel('Interception Rate')
        plt.legend(title='Location')

        # Adjust the layout and save the graph
        plt.tight_layout()
        plt.savefig('figures/defensive_interception_rate.png')
        plt.close()

    # Graph 6: Third-down conversion percentage allowed
    # Only create this graph if third-down statistics are available
    if not third_down_stats.empty:

        # Get all of the unique defensive teams
        teams = third_down_stats['defteam'].unique()

        # Create lists to store home and away conversion rates
        home_rates = []
        away_rates = []
        team_names = []

        # Go through each defensive team
        for team in teams:

            # Select the statistics for the current team
            team_data = third_down_stats[
                third_down_stats['defteam'] == team
            ]

            # Separate the team's home and away statistics
            home = team_data[
                team_data['location'] == 'Home'
            ]

            away = team_data[
                team_data['location'] == 'Away'
            ]

            # Remove rows that are missing conversion percentages
            home = home.dropna(subset=['conversion_pct'])
            away = away.dropna(subset=['conversion_pct'])

            # Only include teams with both home and away results
            if len(home) > 0 and len(away) > 0:

                # Save the team name and its conversion percentages
                team_names.append(team)
                home_rates.append(home.iloc[0]['conversion_pct'])
                away_rates.append(away.iloc[0]['conversion_pct'])

        # Create positions for the teams on the graph
        positions = range(len(team_names))

        # Set the width of the bars
        width = 0.35

        # Position the home and away bars next to each other
        home_positions = []
        away_positions = []

        for position in positions:
            home_positions.append(position - width / 2)
            away_positions.append(position + width / 2)

        # Create the third-down conversion percentage graph
        plt.figure(figsize=(12, 6))
        plt.bar(home_positions, home_rates, width, label='Home')
        plt.bar(away_positions, away_rates, width, label='Away')

        # Add team names, graph title, labels, and legend
        plt.xticks(positions, team_names)
        plt.title('Third-Down Conversion Percentage Allowed')
        plt.xlabel('NFL Team')
        plt.ylabel('Offensive Conversion Percentage')
        plt.legend(title='Defensive Location')

        # Adjust the layout and save the graph
        plt.tight_layout()
        plt.savefig('figures/third_down_conversion.png')
        plt.close()


def get_eda_numbers(data, name):
    """Print EDA information for a dataset."""

    print(name)
    print('Rows:', len(data))
    print('Columns:', len(data.keys()))

    missing_total = 0

    for column in data:
        missing = len(data) - len(data[column].dropna())
        missing_total = missing_total + missing

        if missing > 0:
            print(column, 'missing:', missing)

    print('Total missing:', missing_total)

    for column in data:
        values = data[column].dropna()

        if len(values) > 0 and values.mean() == values.mean():
            print(column)
            print('Mean:', values.mean())
            print('Standard deviation:', values.std())
            print('Minimum:', values.min())
            print('Median:', values.median())
            print('Maximum:', values.max())

        else:
            print(column)
            print(data[column].unique())


def combined_dataset_summary(games, pbp):
    """Join the datasets and summarize the combined data."""

    combined = pbp.merge(
        games,
        on='game_id',
        how='left',
        suffixes=('_pbp', '_game')
    )

    print("\nCombined Dataset")
    print("Rows:", combined.shape[0])
    print("Columns:", combined.shape[1])

    print("\nMissing Values:")
    for column in combined:
        missing = len(combined) - len(combined[column].dropna())
        percentage = missing / len(combined) * 100

        if missing > 0:
            print(
                column,
                missing,
                percentage,
                "%"
            )

    return combined


def main():
    """Load data, calculate statistics, and create graphs."""

    # Load the game results and play-by-play datasets
    print('Loading NFL datasets...')

    games = load_games()
    pbp = load_play_by_play()

    combined = combined_dataset_summary(games, pbp)
    
    get_eda_numbers(games, 'Games Dataset')
    get_eda_numbers(pbp, 'Play-by-Play Dataset')

    # Print facts about both sets of data, like
    # their sizes, columns, missing values, and numerical summaries
    describe_dataset(games, 'NFL Game Results')
    describe_dataset(pbp, 'NFL Play-by-Play')

    # Calculate and display home and away statistics for each team
    print('\nCalculating team statistics...')
    team_stats = team_home_away_summary(games)
    print(team_stats)

    # Save the team statistics to a CSV file
    team_stats.to_csv(
        'team_home_away_summary.csv', index=False
    )

    # Calculate and display quarterback statistics
    print('\nCalculating quarterback statistics...')
    qb_stats = quarterback_summary(pbp)
    print(qb_stats)

    # Save the quarterback statistics to a CSV file
    qb_stats.to_csv(
        'quarterback_summary.csv', index=False
    )

    # Calculate and display defensive interception statistics
    print('\nCalculating defensive statistics...')
    defense_stats = defensive_drive_summary(pbp)
    print(defense_stats)

    # Save the defensive statistics to a CSV file
    defense_stats.to_csv(
        'defensive_summary.csv', index=False
    )

    # Calculate and display third-down defensive statistics
    print('\nCalculating third-down statistics...')
    third_down_stats = third_down_summary(pbp)
    print(third_down_stats)

    # Save the third-down statistics to a CSV file
    third_down_stats.to_csv(
        'third_down_summary.csv', index=False
    )

    # Create all six graphs using the calculated statistics
    print('\nCreating graphs...')

    plot_team_results(team_stats)
    plot_quarterback_results(qb_stats)
    plot_defensive_results(defense_stats, third_down_stats)

    # Print messages when the EDA process is finished
    print('\nEDA completed successfully!')
    print('Graphs saved in the figures folder.')


# Run main() when this file is executed directly
if __name__ == '__main__':
    main()