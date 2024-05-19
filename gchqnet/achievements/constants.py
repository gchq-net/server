from .models import AchievementDifficulty

# Achievements in this list are triggered from other parts of the application
# This is not to be used for manually assigned basic achievements.
BUILTIN_BASIC_ACHIEVEMENTS = {
    "f42b1ff0-f559-47d0-b6ec-b092169ccf9e": (
        # Fake SQL injection in leaderboard search.
        AchievementDifficulty.MEDIUM,
        "Hacked the planet",
    ),
}
