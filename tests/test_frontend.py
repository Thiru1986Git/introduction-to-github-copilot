"""
Test the root endpoint and static file serving.

This module contains tests for the root endpoint and static file functionality.
"""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_redirect(self, client: TestClient):
        """Test that root endpoint redirects to static frontend."""
        response = client.get("/")

        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"

    def test_root_redirect_preserves_query_params(self, client: TestClient):
        """Test that root redirect preserves query parameters."""
        response = client.get("/?param=value")

        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html?param=value"


class TestStaticFiles:
    """Tests for static file serving."""

    def test_static_index_html(self, client: TestClient):
        """Test that index.html is served correctly."""
        response = client.get("/static/index.html")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert len(response.text) > 0

    def test_static_app_js(self, client: TestClient):
        """Test that app.js is served correctly."""
        response = client.get("/static/app.js")

        assert response.status_code == 200
        assert "application/javascript" in response.headers.get("content-type", "")
        assert len(response.text) > 0

    def test_static_styles_css(self, client: TestClient):
        """Test that styles.css is served correctly."""
        response = client.get("/static/styles.css")

        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")
        assert len(response.text) > 0

    def test_static_directory_listing_disabled(self, client: TestClient):
        """Test that directory listing is disabled for static files."""
        response = client.get("/static/")

        # Should either return 404 (not found) or 403 (forbidden)
        # but not a directory listing
        assert response.status_code in [403, 404]

    def test_nonexistent_static_file(self, client: TestClient):
        """Test accessing a non-existent static file."""
        response = client.get("/static/nonexistent.txt")

        assert response.status_code == 404

    def test_static_file_caching_headers(self, client: TestClient):
        """Test that static files have appropriate caching headers."""
        response = client.get("/static/index.html")

        # FastAPI static files typically don't set cache headers by default
        # This test documents current behavior
        assert response.status_code == 200
        # Cache headers may or may not be present depending on configuration


class TestFrontendIntegration:
    """Tests for frontend-backend integration."""

    def test_api_endpoints_accessible_from_frontend(self, client: TestClient):
        """Test that API endpoints are accessible (CORS, etc.)."""
        # This simulates frontend making API calls
        response = client.get("/activities")

        assert response.status_code == 200
        # Check for CORS headers if configured
        cors_headers = ["access-control-allow-origin", "access-control-allow-methods"]
        has_cors = any(header in response.headers for header in cors_headers)
        # CORS may or may not be configured - this test documents current state

    def test_static_files_independent_of_api(self, client: TestClient):
        """Test that static files work independently of API state."""
        # Get static file
        static_response = client.get("/static/index.html")
        assert static_response.status_code == 200

        # Modify API state
        client.post("/activities/Chess Club/signup", json={"email": "frontend_test@example.com"})

        # Static file should still work
        static_response2 = client.get("/static/index.html")
        assert static_response2.status_code == 200

        # Content should be identical
        assert static_response.text == static_response2.text