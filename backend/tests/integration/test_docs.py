"""
Integration tests for the docs blueprint.
"""

from typing import TYPE_CHECKING
from unittest.mock import patch

if TYPE_CHECKING:
    from flask.testing import FlaskClient


class TestDocsEndpoint:
    """Test the /api endpoint."""

    def test_docs_with_dev_mode_true(self, client: "FlaskClient") -> None:
        """When DEV_MODE=True, endpoint returns 200."""
        # In our fixture, DEV_MODE is True
        response = client.get("/api")
        assert response.status_code == 200
        # Should return HTML
        assert response.content_type == "text/html; charset=utf-8"

    def test_docs_with_dev_mode_false(self, client: "FlaskClient") -> None:
        """When DEV_MODE=False, endpoint returns 404."""
        # Temporarily patch get_app_config to return DEV_MODE=False
        with patch("blueprints.docs.get_app_config") as mock_get:
            mock_get.return_value.DEV_MODE = False
            response = client.get("/api")
            assert response.status_code == 404
