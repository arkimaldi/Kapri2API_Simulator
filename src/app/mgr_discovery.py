# (C) 2025 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

# mgr_discovery.py
#
# Simple UDP discovery server for Kapri
#
# Listens for a broadcast datagram containing a token (e.g. b"KAPRI_DISCOVERY")
# and responds with a datagram containing sImageVersion, sEUI64 and sRemoteUrl.
#
# sRemoteUrl is the URL the device is currently bound to; an empty string means
# the device is not configured. It is up to the server to compare it against its
# own URL to tell whether the device belongs to it or to another server.
#
# It also accepts a unicast 'kapri_link' datagram that binds the device to a
# server by setting its remote URL. For simulation purposes the value is kept
# in RAM only, so it is lost on restart; the real firmware must persist it.

import socket
import threading
import json
import logging
from typing import Optional, Tuple


class MgrDiscovery:

    DISCOVERY_IP = '0.0.0.0'
    DISCOVERY_PORT = 60100
    DISCOVERY_TOKEN = b'KAPRI_DISCOVERY'  # Token expected in the request
    RECV_BUFFER_SIZE = 1024  # Max bytes per incoming datagram
    LINK_TYPE = 'kapri_link'  # Unicast datagram that binds the device

    # Simulació per a proves: valor que s'informarà com a remote_url.
    # '' (string buit) = dispositiu no configurat, lliure per vincular.
    # Posar-hi, p.ex., 'https://kora.exemple.com/api' per simular un
    # dispositiu ja vinculat.
    SIMULATED_REMOTE_URL = ''

    def __init__(self, app, mgr_knprxupdater, mgr_hardware_info,
                 simulated_remote_url: Optional[str] = None):
        self.app = app
        self.mgr_knprxupdater = mgr_knprxupdater
        self.mgr_hardware_info = mgr_hardware_info
        # Si és None s'usa la constant de classe. Permet injectar el valor
        # des del test sense tocar el codi.
        self.simulated_remote_url = (
            MgrDiscovery.SIMULATED_REMOTE_URL
            if simulated_remote_url is None
            else simulated_remote_url
        )

    def start(self):
        self._start_udp_discovery_server(
            listen_ip=MgrDiscovery.DISCOVERY_IP,
            listen_port=MgrDiscovery.DISCOVERY_PORT,
            token=MgrDiscovery.DISCOVERY_TOKEN
        )

    def get_remote_url(self) -> str:
        """
        Retorna la remote_url configurada al dispositiu.

        De moment retorna el valor simulat. Quan existeixi la configuració
        real, aquest és l'únic punt a canviar: llegir-la d'allà i deixar la
        simulació només per a l'entorn de proves.
        """
        return self.simulated_remote_url or ''

    def set_remote_url(self, remote_url: str) -> None:
        """
        Permet canviar el valor simulat en calent, per encadenar proves
        (lliure -> vinculat -> lliure) sense reiniciar el procés.
        """
        self.simulated_remote_url = remote_url or ''
        logging.info("Discovery: simulated remote_url set to '%s'", self.simulated_remote_url)

    def _apply_link(self, payload: dict, remote_addr: Tuple[str, int]) -> None:
        """
        Aplica una ordre de vinculació rebuda per unicast.

        Un dispositiu ja vinculat NO es pot re-vincular per UDP: si s'acceptés,
        qualsevol equip de la xarxa podria redirigir el terminal cap a un altre
        servidor sense autenticar-se. Per alliberar-lo cal un reset físic.

        El token no arriba mai per aquesta via: l'escriu el servidor durant la
        seqüència d'enrolament, que ja circula per HTTPS.
        """
        new_url = (payload.get('sRemoteUrl') or '').strip()
        if not new_url:
            logging.warning("Link request from %s without sRemoteUrl: ignored", remote_addr[0])
            return

        current = self.get_remote_url()
        if current:
            logging.warning(
                "Link request from %s rejected: device already bound to '%s'",
                remote_addr[0], current
            )
            return

        self.set_remote_url(new_url)
        logging.info("Device bound to '%s' by %s", new_url, remote_addr[0])

    def _build_response(self, remote_addr: Tuple[str, int]) -> bytes:
        """
        Build the response payload.
        """
        sImageVersion = self.mgr_knprxupdater.get_image_version()
        sEUI64 = self.mgr_hardware_info.get('sEUI64')
        sRemoteUrl = self.get_remote_url()
        payload = {
            'type': 'kapri_discovery',
            'sImageVersion': sImageVersion,
            'sEUI64': sEUI64,
            'sRemoteUrl': sRemoteUrl,
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
                    # Pot ser una ordre de vinculació, o bé la resposta d'un
                    # altre dispositiu (les respostes van per broadcast) o la
                    # nostra pròpia. Només s'atén 'kapri_link'.
                    self._handle_non_discovery_datagram(data, addr)
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

    def _handle_non_discovery_datagram(self, data: bytes, addr: Tuple[str, int]) -> None:
        try:
            payload = json.loads(data.decode('ascii', errors='replace'))
        except Exception:
            return  # no és JSON: s'ignora en silenci
        if not isinstance(payload, dict):
            return
        if payload.get('type') != MgrDiscovery.LINK_TYPE:
            return  # resposta de discovery d'un altre dispositiu, o la pròpia
        try:
            self._apply_link(payload, addr)
        except Exception:
            logging.exception("Error applying link request from %s", addr[0])

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
