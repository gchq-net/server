# Referential Integrity

The following things do not have referential integrity being enforced:

- CaptureEvent.score
    - This should always be the same as CaptureEvent.location.difficulty
- CaptureEvent.created_by
    - This should always be the same as CaptureEvent.raw_event.badge.created_by
- BasicAchievementEvent.score
    - This should always be the same as BasicAchievementEvent.achievement.difficulty