import ssl
from django.core.mail.backends.smtp import EmailBackend


class InsecureEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False
        try:
            # Use the default SSL context for secure connections
            self.connection = self.connection_class(self.host, self.port,
                                                    timeout=self.timeout)
            if self.use_tls:
                self.connection.starttls()
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception:
            if not self.fail_silently:
                raise