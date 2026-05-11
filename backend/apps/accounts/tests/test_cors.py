from django.test import TestCase, override_settings
from django.conf import settings

class CORSTest(TestCase):
    def test_cors_middleware_is_present(self):
        self.assertIn("corsheaders.middleware.CorsMiddleware", settings.MIDDLEWARE)
        self.assertIn("corsheaders", settings.INSTALLED_APPS)

    @override_settings(CORS_ALLOWED_ORIGINS=["http://example.com"])
    def test_cors_allowed_origin(self):
<<<<<<< fix/cors-protection-11636812703175948810
        response = self.client.get("/api/v1/auth/login/", HTTP_ORIGIN="http://example.com")
=======
        response = self.client.get("/api/v1/auth/login", HTTP_ORIGIN="http://example.com")
>>>>>>> main
        self.assertEqual(response.status_code, 405)  # Method Not Allowed for GET on login, but should have CORS headers
        self.assertEqual(response["Access-Control-Allow-Origin"], "http://example.com")

    @override_settings(CORS_ALLOWED_ORIGINS=["http://example.com"])
    def test_cors_disallowed_origin(self):
<<<<<<< fix/cors-protection-11636812703175948810
        response = self.client.get("/api/v1/auth/login/", HTTP_ORIGIN="http://malicious.com")
=======
        response = self.client.get("/api/v1/auth/login", HTTP_ORIGIN="http://malicious.com")
>>>>>>> main
        self.assertNotIn("Access-Control-Allow-Origin", response)
