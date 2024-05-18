from django import template

from gchqnet.quest.repository import grade_for_score

register = template.Library()


@register.filter
def score_grade(score: int) -> str:
    return grade_for_score(score)
