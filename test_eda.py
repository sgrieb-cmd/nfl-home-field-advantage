"""
This file tests the NFL analysis functions using small
example datasets with known results.
"""

import pandas as pd

from analysis import (
    calculate_win_percentage,
    team_home_away_summary
)


def test_win_percentage():
    """Test the calculation of winning percentages."""
    assert calculate_win_percentage(6, 10) == 0.6
    assert calculate_win_percentage(3, 5) == 0.6
    assert calculate_win_percentage(0, 0) == 0


def test_team_home_away_summary():
    """Test home and away statistics for a sample team."""
    games = pd.DataFrame({
        'home_team': ['A', 'C', 'A', 'B', 'A'],
        'away_team': ['B', 'A', 'C', 'A', 'D'],
        'home_score': [20, 7, 10, 3, 10],
        'away_score': [10, 14, 10, 6, 14]
    })

    results = team_home_away_summary(games)

    team_a = results[results['team'] == 'A'].iloc[0]

    assert team_a['home_win_pct'] == 0.5
    assert team_a['away_win_pct'] == 1.0
    assert team_a['home_away_win_difference'] == -0.5


def main():
    """Run all tests."""
    test_win_percentage()
    test_team_home_away_summary()

    print('All tests passed!')


if __name__ == '__main__':
    main()
