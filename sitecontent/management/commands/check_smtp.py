# sitecontent/management/commands/check_smtp.py
from django.core.management.base import BaseCommand
from django.conf import settings
import socket, ssl


class Command(BaseCommand):
    help = "Teste la connectivité SMTP (socket + éventuellement STARTTLS)."

    def handle(self, *args, **opts):
        host = settings.EMAIL_HOST
        port = settings.EMAIL_PORT
        use_ssl = settings.EMAIL_USE_SSL
        use_tls = settings.EMAIL_USE_TLS

        self.stdout.write(
            f"Testing SMTP connect to {host}:{port} (SSL={use_ssl}, STARTTLS={use_tls})"
        )

        # 1) connexion socket
        with socket.create_connection(
            (host, port), timeout=getattr(settings, "EMAIL_TIMEOUT", 20)
        ) as sock:
            self.stdout.write("TCP connect: OK")

            if use_ssl:
                ctx = ssl.create_default_context()
                with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                    self.stdout.write(f"SSL handshake: OK (protocol={ssock.version()})")
                    self.stdout.write("Done.")
                    return

            # 2) si STARTTLS on fait juste un EHLO minimaliste (sans authentifier)
            sock.sendall(b"EHLO example.com\r\n")
            resp = sock.recv(2048)
            self.stdout.write("EHLO response:")
            self.stdout.write(resp.decode(errors="replace"))

            if use_tls:
                sock.sendall(b"STARTTLS\r\n")
                resp2 = sock.recv(2048)
                self.stdout.write("STARTTLS response:")
                self.stdout.write(resp2.decode(errors="replace"))

                if b"220" not in resp2:
                    self.stderr.write("STARTTLS refused.")
                    return

                ctx = ssl.create_default_context()
                with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                    self.stdout.write(
                        f"TLS handshake after STARTTLS: OK (protocol={ssock.version()})"
                    )
                    self.stdout.write("Done.")
