from .models import AchievementDifficulty, BasicAchievementAwardType

# Achievements in this list are triggered from other parts of the application
# This is not to be used for manually assigned basic achievements.
BUILTIN_BASIC_ACHIEVEMENTS = {
    ## Triggered in GCHQ.NET Server
    "f42b1ff0-f559-47d0-b6ec-b092169ccf9e": (
        # Fake SQL injection in leaderboard search.
        AchievementDifficulty.MEDIUM,
        "Hacked the planet",
        BasicAchievementAwardType.INTERNAL,
    ),
    "193d8853-8000-4261-bdf0-80b73f88e970": (
        # Created or joined a leaderboard
        AchievementDifficulty.EASY,
        "Part of a small community <3",
        BasicAchievementAwardType.INTERNAL,
    ),
    "a5927f71-f60a-4d7b-9abe-7427bf617dac": (
        # Updated display name
        AchievementDifficulty.EASY,
        "Identity Upgrade",
        BasicAchievementAwardType.INTERNAL,
    ),
    "a3db72f7-6f7a-4f27-8996-ae1006df4b0d": (
        # Updated password
        AchievementDifficulty.EASY,
        "Crypt Keeper",
        BasicAchievementAwardType.INTERNAL,
    ),
    "145047b2-697b-4ce9-9f2d-b3ef03c2e507": (
        # Logged in with OTP
        AchievementDifficulty.EASY,
        "Beyond the badge",
        BasicAchievementAwardType.INTERNAL,
    ),
    ## Triggered in Charlie's thing
    "8dbb038c-6545-4b34-9df9-d6cad379ff53": (
        # Logged in via SSH
        AchievementDifficulty.EASY,
        "Totally not backdoored access",
        BasicAchievementAwardType.EXTERNAL,
    ),
    "b8f87b0b-eb90-490a-92b5-73096bdb592d": (
        # Logged in via Telnet - using OTP
        AchievementDifficulty.EASY,
        "Woefully insecure access",
        BasicAchievementAwardType.EXTERNAL,
    ),
    "6d540a11-7035-444a-934c-dbe8a733631e": (
        # Logged in via Telnet - using password login
        AchievementDifficulty.EASY,
        "hunter2",
        BasicAchievementAwardType.EXTERNAL,
    ),
    "541a691e-2824-43e2-bfa7-d07deb3f636a": (
        # Logged in via Dial-up
        AchievementDifficulty.MEDIUM,
        "Beep boop access",
        BasicAchievementAwardType.EXTERNAL,
    ),
    "32d1e1dc-c31b-4cc7-ae04-b155d6f3c336": (
        # Accessed the fake Ctrl+C shell
        AchievementDifficulty.MEDIUM,
        "Crash Bandicoot",
        BasicAchievementAwardType.EXTERNAL,
    ),
}
