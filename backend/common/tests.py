from common.utils.tests import TestCaseUtils


class TestIndexView(TestCaseUtils):
    view_name = "common:index"

    def test_returns_status_200(self):
        response = self.auth_client.get(self.reverse(self.view_name))
        self.assertResponse200(response)


class TestRestCheckApi(TestCaseUtils):
    def test_rest_check_is_public_and_returns_expected_message(self):
        response = self.client.get("/api/rest/rest-check/")

        self.assertResponse200(response)
        payload = response.json()
        self.assertEqual(
            payload["message"],
            "This message comes from the backend. If you're seeing this, the REST API is working!",
        )
