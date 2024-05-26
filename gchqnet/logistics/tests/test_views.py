from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from gchqnet.accounts.models.user import User
from gchqnet.logistics.models import PlannedLocation


class LogisticsAccessTestMixin:
    url: str

    def test_unauthenticated(self, client: Client) -> None:
        resp = client.get(self.url)
        assertRedirects(
            resp,
            f"/accounts/login/?next={self.url}",
            302,
            fetch_redirect_response=False,
        )

    def test_get_not_superuser(self, client: Client, user: User) -> None:
        client.force_login(user)
        resp = client.get(self.url)
        assert resp.status_code == HTTPStatus.FORBIDDEN

    def test_get_superuser(self, client: Client, admin_user: User) -> None:
        client.force_login(admin_user)
        resp = client.get(self.url)
        assert resp.status_code == HTTPStatus.OK


@pytest.mark.django_db
class TestLogisticsHomeView(LogisticsAccessTestMixin):
    url = reverse("logistics:home")


@pytest.mark.django_db
class TestLogisticsLocationsListView(LogisticsAccessTestMixin):
    url = reverse("logistics:locations_list")


@pytest.mark.django_db
class TestLogisticsPlannedListView(LogisticsAccessTestMixin):
    url = reverse("logistics:planned_list")


@pytest.mark.django_db
class TestLogisticsPlannedCreateView(LogisticsAccessTestMixin):
    url = reverse("logistics:planned_create")


@pytest.mark.django_db
class TestLogisticsPlannedEditView(LogisticsAccessTestMixin):
    @property
    def url(self) -> str:  # type: ignore[override]
        pl, _ = PlannedLocation.objects.get_or_create(internal_name="foo")
        return reverse("logistics:planned_edit", args=[pl.id])


@pytest.mark.django_db
class TestLogisticsPlannedDeleteView(LogisticsAccessTestMixin):
    @property
    def url(self) -> str:  # type: ignore[override]
        pl, _ = PlannedLocation.objects.get_or_create(internal_name="foo")
        return reverse("logistics:planned_delete", args=[pl.id])
