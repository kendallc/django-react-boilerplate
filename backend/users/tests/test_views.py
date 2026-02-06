import json

from common.utils.tests import TestCaseUtils
from model_bakery import baker

from ..models import User


class UserApiTest(TestCaseUtils):
    def test_list_users(self):
        baker.make(User, _fill_optional=True, _quantity=5)

        response = self.auth_client.get("/api/users/")

        self.assertResponse200(response)
        payload = response.json()
        # Note: One user is already created in the setUp method of TestCaseUtils
        self.assertEqual(payload.get("count"), 6)
        self.assertEqual(len(payload.get("results")), 6)

    def test_create_user(self):
        data = {
            "email": "testuser@test.com",
            "password": "12345678",
        }

        response = self.auth_client.post(
            "/api/users/", data=json.dumps(data), content_type="application/json"
        )

        self.assertResponse201(response)
        payload = response.json()
        user = User.objects.get(id=payload["id"])
        self.assertEqual(user.email, data["email"])

    def test_retrieve_user(self):
        user = baker.make(User, _fill_optional=True)

        response = self.auth_client.get(f"/api/users/{user.id}/")

        self.assertResponse200(response)
        payload = response.json()
        self.assertEqual(payload["id"], user.id)
        self.assertEqual(payload["email"], user.email)

    def test_put_update_user(self):
        user = baker.make(User, email="testuser@test.com", _fill_optional=True)
        data = {
            "email": "user@test.com",
            "password": "87654321",
        }

        response = self.auth_client.put(
            f"/api/users/{user.id}/", data=json.dumps(data), content_type="application/json"
        )

        self.assertResponse200(response)
        user.refresh_from_db()
        self.assertEqual(user.email, data["email"])

    def test_patch_update_user(self):
        user = baker.make(User, email="testuser@test.com", _fill_optional=True)
        data = {
            "email": "user@test.com",
        }

        response = self.auth_client.patch(
            f"/api/users/{user.id}/", data=json.dumps(data), content_type="application/json"
        )

        self.assertResponse200(response)
        user.refresh_from_db()
        self.assertEqual(user.email, data["email"])

    def test_delete_user(self):
        user = baker.make(User, _fill_optional=True)

        response = self.auth_client.delete(f"/api/users/{user.id}/")

        self.assertResponse204(response)
        self.assertFalse(User.objects.filter(id=user.id).exists())
