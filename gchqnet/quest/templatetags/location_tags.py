from django import template

from gchqnet.quest.models import LocationDifficulty

register = template.Library()


@register.inclusion_tag("components/govuk/tag.html")
def difficulty_tag(difficulty: int) -> dict[str, str]:
    lut = {
        LocationDifficulty.EASY.value: "blue",
        LocationDifficulty.MEDIUM.value: "purple",
        LocationDifficulty.HARD.value: "red",
        LocationDifficulty.INSANE.value: "orange",
        LocationDifficulty.IMPOSSIBLE.value: "green",
    }
    colour = lut[difficulty]
    return {
        "content": LocationDifficulty(difficulty).label,
        "colour": colour,
    }
