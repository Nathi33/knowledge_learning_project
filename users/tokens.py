from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone

class TimedActivationTokenGenerator(PasswordResetTokenGenerator):
    def __init__(self, expiry_minutes=60):
        super().__init__()
        self.expiry_minutes = expiry_minutes
    
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}-{user.is_active}-{timestamp}"

    def _num_minutes(self, dt):
        return int(dt.timestamp() // 60)
    
    def _now(self):
        return timezone.now()
    
    def check_token(self, user, token):
        """
        Validate that a token is correct and has not expired.
        """
        if not (user and token):
            return False

        try:
            ts_b36 = token.split("-")[-1]
            ts = int(ts_b36, 36)
        except Exception:
            return False

        now_ts = self._num_minutes(self._now())
        # Compare the timestamp in token with current timestamp
        if (now_ts - ts) > self.expiry_minutes:
            return False
        
        return True

activation_token_generator = TimedActivationTokenGenerator(expiry_minutes=60)
