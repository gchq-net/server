from django import template

from gchqnet.quest.models import LocationDifficulty

register = template.Library()


@register.filter
def difficulty_label(difficulty: int) -> str:
    return LocationDifficulty(difficulty).label
