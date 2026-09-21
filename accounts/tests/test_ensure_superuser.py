from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase


class EnsureSuperuserCommandTests(TestCase):
    @patch.dict(
        "os.environ",
        {"ADMIN_USERNAME": "admin", "ADMIN_PASSWORD": "test-password", "ADMIN_EMAIL": "admin@example.com"},
    )
    def test_creates_and_updates_superuser(self):
        call_command("ensure_superuser")
        user = get_user_model().objects.get(username="admin")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("test-password"))

        with patch.dict("os.environ", {"ADMIN_USERNAME": "admin", "ADMIN_PASSWORD": "new-password"}, clear=True):
            call_command("ensure_superuser")
        user.refresh_from_db()
        self.assertTrue(user.check_password("new-password"))
