# (C) 2025 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

# mgr_discovery.py
#
# Simple UDP discovery server for Kapri
#
# Listens for a broadcast datagram containing a token (e.g. b"KAPRI_DISCOVERY")
# and responds with a datagram containing sImageVersion, sEUI64 and sRemoteUrl.
#
# sRemoteUrl is read from the ACTIVE configuration (NanoConfiguration id 1),
# not from the pending one: it reports what the device is really using. An
# empty string means the device is not bound to any server, and it is up to
# the server to compare the value against its own URL to tell whether the
# device belongs to it or to another one.
#
# It also accepts a unicast 'kapri_link' datagram that binds the device to a
# server: it writes the cloud parameters and applies them, so that after the
# link the device actually starts calling. Its fields carry their native
# configuration names; only the discovery reply keeps the sRemoteUrl
# convention.

import socket
import threading
import json
import logging
from typing import Tuple

from app.db_models import NanoConfiguration
from app.extensions import db
from app.ktp_ret import KtpRet


class MgrDiscovery:

    DISCOVERY_IP = '0.0.0.0'
    DISCOVERY_PORT = 60100
    DISCOVERY_TOKEN = b'KAPRI_DISCOVERY'  # Token expected in the request
    RECV_BUFFER_SIZE = 1024  # Max bytes per incoming datagram
    LINK_TYPE = 'kapri_link'  # Unicast datagram that binds the device

    # Id of the row holding the configuration currently applied to the system.
    # Row 2 holds the pending one, written but not applied yet.
    ACTIVE_CONFIG_ID = 1

    # Configuration parameters a link datagram is allowed to set. They carry
    # their native configuration name, so the datagram maps one to one onto
    # ins_cfg_write. Nothing outside this set is ever written: the datagram
    # travels over UDP without authentication, so it must not be able to
    # overwrite settings made by the installer.
    LINK_PARAMS = (
        'cloud_remote_server_url',
        'cloud_interface',
        'cloud_allowed_events',
        'cloud_keep_alive_timeout',
    )

    def __init__(self, app, mgr_knprxupdater, mgr_hardware_info, mgr_config_kapri):
        self.app = app
        self.mgr_knprxupdater = mgr_knprxupdater
        self.mgr_hardware_info = mgr_hardware_info
        self.mgr_config_kapri = mgr_config_kapri

    def start(self):
        self._start_udp_discovery_server(
            listen_ip=MgrDiscovery.DISCOVERY_IP,
            listen_port=MgrDiscovery.DISCOVERY_PORT,
            token=MgrDiscovery.DISCOVERY_TOKEN
        )

    def get_remote_url(self) -> str:
        """
        Returns the cloud_remote_server_url of the ACTIVE configuration.

        An empty string means the device is not bound to any server.
        """
        try:
            with self.app.app_context():
                try:
                    qry = db.session.query(NanoConfiguration).filter(
                        NanoConfiguration.id == MgrDiscovery.ACTIVE_CONFIG_ID
                    ).one()
                    return qry.cloud_remote_server_url or ''
                finally:
                    db.session.close()
        except Exception:
            logging.exception("Error reading the active cloud_remote_server_url")
            return ''

    def _apply_link(self, payload: dict, remote_addr: Tuple[str, int]) -> None:
        """
        Applies a link request received by unicast: writes the cloud
        parameters and applies them, so the device starts calling the server.

        A device already bound is NOT re-bound over UDP: if it were, any host
        on the network could redirect the terminal to another server without
        authenticating. Freeing it requires a factory reset.

        The token never arrives this way: the server writes it during the
        enrollment sequence, which already runs over HTTPS.
        """
        dict_params = {
            name: payload[name]
            for name in MgrDiscovery.LINK_PARAMS
            if payload.get(name) is not None
        }
        if not dict_params.get('cloud_remote_server_url'):
            logging.warning("Link request from %s without a remote URL: ignored",
                            remote_addr[0])
            return

        current = self.get_remote_url()
        if current:
            logging.warning(
                "Link request from %s rejected: device already bound to '%s'",
                remote_addr[0], current
            )
            return

        with self.app.app_context():
            ucRet, param_failed = self.mgr_config_kapri.write_future(dict_params)
            if ucRet != KtpRet.RET_OK:
                logging.error("Link request from %s failed writing the configuration "
                              "(ucRet=%s, parameter=%s)",
                              remote_addr[0], ucRet, param_failed)
                return

            ucRet = self.mgr_config_kapri.apply()
            if ucRet != KtpRet.RET_OK:
                logging.error("Link request from %s failed applying the configuration "
                              "(ucRet=%s)", remote_addr[0], ucRet)
                return

        logging.info("Device bound to '%s' by %s",
                     dict_params['cloud_remote_server_url'], remote_addr[0])

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
                    # It may be a link request, or the discovery reply of
                    # another device (replies are broadcast) or our own. Only
                    # 'kapri_link' is acted upon.
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
            return  # not JSON: silently ignored
        if not isinstance(payload, dict):
            return
        if payload.get('type') != MgrDiscovery.LINK_TYPE:
            return  # another device's discovery reply, or our own
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
