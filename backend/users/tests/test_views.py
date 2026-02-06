import json
from urllib.parse import urlparse

from common.utils.tests import TestCaseUtils
from model_bakery import baker

from ..models import User


class UserApiTest(TestCaseUtils):
    def test_list_users_requires_admin(self):
        response = self.auth_client.get("/api/users/")
        self.assertResponse403(response)

    def test_list_users_returns_paginated_results(self):
        baker.make(User, _fill_optional=True, _quantity=20)

        first_page = self.admin_client.get("/api/users/")
        self.assertResponse200(first_page)
        first_payload = first_page.json()
        self.assertEqual(first_payload["count"], 22)
        self.assertEqual(len(first_payload["results"]), 10)
        self.assertIsNotNone(first_payload["next"])
        self.assertIsNone(first_payload["previous"])

        next_url = first_payload["next"]
        next_path = f"{urlparse(next_url).path}?{urlparse(next_url).query}"
        second_page = self.admin_client.get(next_path)
        self.assertResponse200(second_page)
        second_payload = second_page.json()
        self.assertEqual(second_payload["count"], 22)
        self.assertEqual(len(second_payload["results"]), 10)
        self.assertIsNotNone(second_payload["previous"])

    def test_create_user_requires_admin(self):
        data = {"email": "testuser@test.com", "password": "12345678"}
        response = self.auth_client.post(
            "/api/users/", data=json.dumps(data), content_type="application/json"
        )
        self.assertResponse403(response)

    def test_create_user_requires_csrf_token(self):
        data = {"email": "testuser@test.com", "password": "12345678"}
        response = self.admin_csrf_client.post(
            "/api/users/",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertResponse403(response)

    def test_create_user_rejects_invalid_payload(self):
        invalid_email = {"email": "not-an-email", "password": "12345678"}
        short_password = {"email": "testuser@test.com", "password": "123"}

        invalid_email_response = self.admin_client.post(
            "/api/users/",
            data=json.dumps(invalid_email),
            content_type="application/json",
        )
        short_password_response = self.admin_client.post(
            "/api/users/",
            data=json.dumps(short_password),
            content_type="application/json",
        )

        self.assertResponse400(invalid_email_response)
        self.assertResponse400(short_password_response)

    def test_create_user(self):
        data = {"email": "testuser@test.com", "password": "12345678"}
        response = self.admin_client.post(
            "/api/users/", data=json.dumps(data), content_type="application/json"
        )

        self.assertResponse201(response)
        payload = response.json()
        user = User.objects.get(id=payload["id"])
        self.assertEqual(user.email, data["email"])
        self.assertTrue(user.check_password(data["password"]))

    def test_retrieve_user_allows_self(self):
        response = self.auth_client.get(f"/api/users/{self.user.id}/")
        self.assertResponse200(response)
        self.assertEqual(response.json()["email"], self.user.email)

    def test_retrieve_user_forbids_other_non_admin(self):
        other_user = baker.make(User, _fill_optional=True)
        response = self.auth_client.get(f"/api/users/{other_user.id}/")
        self.assertResponse403(response)

    def test_put_update_user_as_self(self):
        data = {"email": "user@test.com", "password": "87654321"}
        response = self.auth_client.put(
            f"/api/users/{self.user.id}/",
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertResponse200(response)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, data["email"])
        self.assertTrue(self.user.check_password(data["password"]))

    def test_put_update_user_forbids_other_non_admin(self):
        other_user = baker.make(User, email="other@test.com", _fill_optional=True)
        data = {"email": "user@test.com", "password": "87654321"}
        response = self.auth_client.put(
            f"/api/users/{other_user.id}/",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertResponse403(response)

    def test_patch_update_user(self):
        data = {"email": "user@test.com", "password": "87654321"}
        response = self.admin_client.patch(
            f"/api/users/{self.user.id}/",
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertResponse200(response)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, data["email"])
        self.assertTrue(self.user.check_password(data["password"]))

    def test_delete_user_forbids_other_non_admin(self):
        other_user = baker.make(User, _fill_optional=True)
        response = self.auth_client.delete(f"/api/users/{other_user.id}/")
        self.assertResponse403(response)

    def test_delete_user_as_admin(self):
        target_user = baker.make(User, _fill_optional=True)
        response = self.admin_client.delete(f"/api/users/{target_user.id}/")

        self.assertResponse204(response)
        self.assertFalse(User.objects.filter(id=target_user.id).exists())
