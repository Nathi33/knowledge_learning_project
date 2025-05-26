from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import datetime, timedelta
from django.utils.http import base36_to_int

class TimedActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}-{user.is_active}-{timestamp}"

    def check_token(self, user, token):
        if not super().check_token(user, token):
            return False

        try:
            ts_b36 = token.split("-")[1]
            timestamp = base36_to_int(ts_b36)
        except (IndexError, ValueError):
            return False

        current_timestamp = self._now_timestamp()
        if (current_timestamp - timestamp) > 60:
            return False
        return True

    def _now_timestamp(self):
        return int(datetime.now().timestamp() // 60)

activation_token_generator = TimedActivationTokenGenerator()
