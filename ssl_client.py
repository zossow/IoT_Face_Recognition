import socket
import threading
import ssl


class ClientSocketApp(threading.Thread):
    def __init__(self, _context, _host, _port):
        threading.Thread.__init__(self)
        self.context = _context
        self.host = _host
        self.port = _port

    def run(self):
        with socket.create_connection((self.host, self.port)) as sock:
            with self.context.wrap_socket(sock, server_hostname=self.host) as ssock:
                print(ssock.version())
                while True:
                    pass
                    # TODO tutaj bedzie odbieranie nowego modelu od serwera
                    # i aktualizowanie modelu do nowego watku


def main():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations('client.cer')
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    host = 'localhost'
    port = 51000

    clientApp = ClientSocketApp(context, host, port)
    clientApp.start()
    clientApp.join()


main()
