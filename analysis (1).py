"""
This file calculates NFL home and away statistics for teams,
quarterbacks, and defenses.
"""

import pandas as pd


def calculate_win_percentage(wins, games):
    """Return the win percentage, excluding ties from games."""
    # Return 0 if there are no games
    if games == 0:
        return 0
    return wins / games


def team_home_away_summary(games):
    """Calculate home and away records and point differences."""
    # Make a list of all teams without repeating names
    teams = []

    for team in games['home_team'].dropna():
        if team not in teams:
            teams.append(team)

    for team in games['away_team'].dropna():
        if team not in teams:
            teams.append(team)

    teams = sorted(teams)

    # Make a list to hold each team's stats
    results = []

    # Get the stats for each team
    for team in teams:

        # Get the games where the team played at home and away
        home = games[games['home_team'] == team]
        away = games[games['away_team'] == team]

        # Count the team's home and away wins
        home_wins = (home['home_score'] > home['away_score']).sum()
        away_wins = (away['away_score'] > away['home_score']).sum()

        # Count games that did not end in a tie
        # Do not count ties when finding win percentages
        home_decisions = (home['home_score'] != home['away_score']).sum()
        away_decisions = (away['away_score'] != away['home_score']).sum()

        # Find the home and away win percentages
        home_pct = calculate_win_percentage(home_wins, home_decisions)
        away_pct = calculate_win_percentage(away_wins, away_decisions)

        # Find the average point difference at home and away
        # A positive number means the team scored more points
        home_margin = (home['home_score'] - home['away_score']).mean()
        away_margin = (away['away_score'] - away['home_score']).mean()

        # Save all the team's stats in a dictionary
        results.append({
            'team': team,
            'home_win_pct': home_pct,
            'away_win_pct': away_pct,
            'home_away_win_difference': home_pct - away_pct,
            'home_point_diff': home_margin,
            'away_point_diff': away_margin
        })

    # Turn the list of team stats into a DataFrame
    return pd.DataFrame(results)


def quarterback_summary(pbp, min_attempts=15):
    """Compare quarterback stats at home and away."""
    # Keep only plays where a pass was thrown
    passes = pbp[pbp['pass_attempt'] == 1]

    # Remove plays missing the quarterback or team name
    passes = passes.dropna(subset=['passer_player_name', 'posteam'])

    # Make a list to hold the quarterback stats
    summary_rows = []

    # Look at each quarterback's passes
    for name, qb_passes in passes.groupby('passer_player_name'):

        # Separate the quarterback's home and away passes
        home_passes = qb_passes[
            qb_passes['posteam'] == qb_passes['home_team']]
        away_passes = qb_passes[
            qb_passes['posteam'] == qb_passes['away_team']]

        # Make sure the quarterback has played at home and away
        if len(home_passes) > 0 and len(away_passes) > 0:

            # Find the stats for home and away games
            for location, location_passes in [
                ('Home', home_passes), ('Away', away_passes)
            ]:
                # Count the total number of passes
                attempts = location_passes['pass_attempt'].sum()

                # Skip this location if there are not enough passes
                if attempts >= min_attempts:

                    # Add up the passing stats
                    completions = location_passes['complete_pass'].sum()
                    yards = location_passes['passing_yards'].sum()
                    touchdowns = location_passes['pass_touchdown'].sum()
                    interceptions = location_passes['interception'].sum()

                    # Find the quarterback's percentages and averages
                    summary_rows.append({
                        'passer_player_name': name,
                        'location': location,
                        'attempts': attempts,
                        'completions': completions,
                        'passing_yards': yards,
                        'touchdowns': touchdowns,
                        'interceptions': interceptions,
                        'completion_pct': completions / attempts,
                        'yards_per_attempt': yards / attempts,
                        'touchdown_rate': touchdowns / attempts,
                        'interception_rate': interceptions / attempts
                    })

    # Turn the list of quarterback stats into a DataFrame
    return pd.DataFrame(summary_rows)


def defensive_drive_summary(pbp):
    """Calculate defensive interceptions by team and location."""
    # Remove plays missing important information
    plays = pbp.dropna(
        subset=['game_id', 'drive', 'defteam', 'posteam'])

    # Make a new column to show if the defense is home or away
    plays['location'] = None

    # Mark the defense as Home if it is the home team
    plays.loc[
        plays['defteam'] == plays['home_team'], 'location'
    ] = 'Home'

    # Mark the defense as Away if it is the away team
    plays.loc[
        plays['defteam'] == plays['away_team'], 'location'
    ] = 'Away'

    # Remove plays that could not be marked as home or away
    plays = plays.dropna(subset=['location'])

    # Make a list to hold each team's defense stats
    summary_rows = []

    # Group the plays by defense team and location
    for (team, location), team_plays in plays.groupby(
        ['defteam', 'location']
    ):
        # Count the defense plays and interceptions
        defensive_plays = len(team_plays)
        interceptions = team_plays['interception'].sum()

        # Find the interception rate
        if defensive_plays > 0:
            interception_rate = interceptions / defensive_plays
        else:
            interception_rate = 0

        # Save the stats for this team and location
        summary_rows.append({
            'defteam': team,
            'location': location,
            'defensive_plays': defensive_plays,
            'interceptions': interceptions,
            'interception_rate': interception_rate
        })

    # Turn the list of defense stats into a DataFrame
    return pd.DataFrame(summary_rows)


def third_down_summary(pbp):
    """Calculate third-down conversions allowed."""
    # Keep only plays that happened on third down
    third_downs = pbp[pbp['down'] == 3]

    # Remove plays missing the offense or defense team
    third_downs = third_downs.dropna(subset=['defteam', 'posteam'])

    # Make a column to show if the defense is home or away
    third_downs['location'] = None

    # Mark the defense as Home if it is the home team
    third_downs.loc[
        third_downs['defteam'] == third_downs['home_team'],
        'location'] = 'Home'

    # Mark the defense as Away if it is the away team
    third_downs.loc[
        third_downs['defteam'] == third_downs['away_team'],
        'location'] = 'Away'

    # Remove plays that could not be marked as home or away
    third_downs = third_downs.dropna(subset=['location'])

    # Make a list to hold the third-down stats
    summary_rows = []

    # Group the plays by defense team and location
    for (team, location), team_plays in third_downs.groupby(
        ['defteam', 'location']):

        # Count the third-down plays and successful conversions
        attempts = len(team_plays)
        conversions = team_plays['third_down_converted'].sum()

        # Find the percentage of third downs converted
        if attempts > 0:
            conversion_pct = conversions / attempts
        else:
            conversion_pct = 0

        # Save the stats for this team and location
        summary_rows.append({
            'defteam': team,
            'location': location,
            'third_down_attempts': attempts,
            'conversions_allowed': conversions,
            'conversion_pct': conversion_pct
        })

    # Turn the list of third-down stats into a DataFrame
    return pd.DataFrame(summary_rows)