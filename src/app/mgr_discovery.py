# (C) 2025 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

# mgr_discovery.py
#
# Simple UDP discovery server for Kapri
#
# Listens for a broadcast datagram containing a token (e.g. b"KAPRI_DISCOVERY")
# and responds with a datagram containing sImageVersion.

import socket
import threading
import json
import logging
from typing import Tuple


class MgrDiscovery:

    DISCOVERY_IP = '0.0.0.0'
    DISCOVERY_PORT = 60100
    DISCOVERY_TOKEN = b'KAPRI_DISCOVERY'  # Token expected in the request
    RECV_BUFFER_SIZE = 1024  # Max bytes per incoming datagram

    def __init__(self, app, mgr_knprxupdater, mgr_hardware_info):
        self.app = app
        self.mgr_knprxupdater = mgr_knprxupdater
        self.mgr_hardware_info = mgr_hardware_info

    def start(self):
        self._start_udp_discovery_server(
            listen_ip=MgrDiscovery.DISCOVERY_IP,
            listen_port=MgrDiscovery.DISCOVERY_PORT,
            token=MgrDiscovery.DISCOVERY_TOKEN
        )

    def _build_response(self, remote_addr: Tuple[str, int]) -> bytes:
        """
        Build the response payload.
        """
        sImageVersion = self.mgr_knprxupdater.get_image_version()
        sEUI64 = self.mgr_hardware_info.get('sEUI64')
        payload = {
            'type': 'kapri_discovery',
            'sImageVersion': sImageVersion,
            'sEUI64': sEUI64
        }
        return json.dumps(payload).encode("ascii")


    def _server_loop(self, listen_ip: str, listen_port: int, token: bytes) -> None:
        """
        Blocking loop: listens for discovery requests and replies via BROADCAST.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Reuse address and ENABLE BROADCAST mode
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            # Bind to all interfaces on the given port
            sock.bind((listen_ip, listen_port))

            logging.info("Kapri UDP discovery server listening on %s:%d (Broadcast enabled)", listen_ip, listen_port)

            while True:
                try:
                    data, addr = sock.recvfrom(MgrDiscovery.RECV_BUFFER_SIZE)
                except Exception:
                    logging.exception("Error receiving UDP discovery packet")
                    continue

                if not data.startswith(token):
                    continue

                logging.debug("Received discovery request from %s:%d", addr[0], addr[1])

                try:
                    response = self._build_response(addr)
                    broadcast_dest = ("255.255.255.255", listen_port)
                    sock.sendto(response, broadcast_dest)
                    logging.debug("Broadcasted discovery response to %s", broadcast_dest[0])
                except Exception:
                    logging.exception("Error sending UDP discovery response")

        except Exception:
            logging.exception("Fatal error in UDP discovery server")
        finally:
            try:
                sock.close()
            except Exception:
                pass
            logging.info("Kapri UDP discovery server stopped")

    def _start_udp_discovery_server(
        self,
        listen_ip,
        listen_port,
        token: bytes,
    ) -> threading.Thread:
        """
        Starts the UDP discovery server in a background daemon thread.
        Returns the thread object.
        """
        thread = threading.Thread(
            target=self._server_loop,
            args=(listen_ip, listen_port, token),
            name="KapriUDPDiscovery",
            daemon=True,  # Daemon so it won't block process exit
        )
        thread.start()
        logging.info(
            "Kapri UDP discovery server started (IP=%s, port=%d, token=%s)",
            listen_ip,
            listen_port,
            token.decode(errors="ignore"),
        )
        return thread
