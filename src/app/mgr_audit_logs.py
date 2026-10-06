# (C) 2026 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

"""
AuditLogs — Registre persistent d'events de seguretat (CRA Annex I, l)

Equivalent en Python del mòdul embedded `kapri_audit_log.c` del
kapricontroller, adaptat per desar les entrades a la taula `audit_entry`
de la BBDD en lloc d'un buffer circular a NVM.

Diferències respecte a la versió C:
  - No hi ha `init()`: no cal llegir cap buffer de NVM, la BBDD ja és la
    font de veritat. Tampoc hi ha detecció de "registre corrupte".
  - No es guarda `uptime_ms`: al servidor no té sentit (el rellotge de
    sistema del kapri1 sempre és fiable), per això la taula no té aquest
    camp.
  - El camp `ts` del C es substitueix per `dt_utc`, que la BBDD omple sola
    (mateix patró que `EventsSemiOffline`/`SemiOfflineLists` a models.py).
  - El camp `user` es diu `user_name` (paraula reservada en SQL).
  - En comptes de `strncpy` es fa un truncat explícit a la longitud de
    cada columna, per evitar errors de la BBDD si algun camp arriba massa
    llarg.
  - El buffer circular de mida fixa del dispositiu (50 entrades a NVM) es
    substitueix per un límit configurable a la BBDD (per defecte 100,
    AUDIT_LOG_MAX_ENTRIES): abans de cada inserció es comprova si s'ha
    arribat al límit i, si cal, s'esborren les entrades més antigues
    (`audit_log_prune`).
"""
import inspect

from app.ktp_ret import KtpRet
from app.utilities import Utils
from app.extensions import db
from app.db_models import AuditEntry

import logging


class MgrAuditLogs:
    # ---------------------------------------------------------------------------
    # Valors possibles de "via"
    # ---------------------------------------------------------------------------
    AUDIT_VIA_WEBADMIN = "webadmin"
    AUDIT_VIA_BUTTON = "button"
    AUDIT_VIA_INSTRUCTION = "instruction"

    # ---------------------------------------------------------------------------
    # Valors possibles de "event"
    # ---------------------------------------------------------------------------
    AUDIT_EVENT_LOGIN = "login"
    AUDIT_EVENT_LOGOUT = "logout"
    AUDIT_EVENT_PWD_CHANGE = "pwd_change"
    AUDIT_EVENT_PWD_RECOVERY = "pwd_recovery"
    AUDIT_EVENT_NVM_CORRUPTION = "nvm_corruption"
    AUDIT_EVENT_CFG_SAVE = "cfg_save"
    AUDIT_EVENT_CFG_WRITE = "cfg_write"
    AUDIT_EVENT_CFG_APPLY = "cfg_apply"
    AUDIT_EVENT_CFG_BACKUP = "cfg_backup"
    AUDIT_EVENT_CFG_RESTORE = "cfg_restore"
    AUDIT_EVENT_CFG_FACTORY_BACKUP = "cfg_factory_backup"
    AUDIT_EVENT_CFG_FACTORY_RESTORE = "cfg_factory_restore"
    AUDIT_EVENT_CFG_FACTORY_RESET = "cfg_factory_reset"

    # ---------------------------------------------------------------------------
    # Longituds màximes de cada camp (han de coincidir amb els String(...) de
    # AuditEntry a models.py)
    # ---------------------------------------------------------------------------
    AUDIT_VIA_LEN = 15
    AUDIT_USER_LEN = 23
    AUDIT_IP_LEN = 15
    AUDIT_EVENT_LEN = 23
    AUDIT_RESULT_LEN = 7

    # Límit de files que volem conservar a la taula. A diferència del dispositiu
    # (buffer circular fix de 50 entrades a NVM), aquí es controla esborrant les
    # entrades més antigues just abans d'inserir-ne una de nova quan se supera
    # aquest llindar (veure audit_log_write / audit_log_prune).
    AUDIT_LOG_MAX_ENTRIES = 100

    def __init__(self, app):
        self.app = app

    @staticmethod
    def _truncate(value, max_len, default=""):
        """Equivalent al strncpy(dst, value ? value : "", max_len) del C."""
        if value is None:
            value = default
        return str(value)[:max_len]

    def audit_log_write(self, via, user_name=None, ip=None, event=None, ok=True):
        """
        Escriu una nova entrada d'auditoria a la BBDD.

        user_name i ip poden ser None si no apliquen per al tipus d'event
        (mateix comportament que passar NULL a la versió C).

        Si la taula ja té AUDIT_LOG_MAX_ENTRIES files o més, primer es fa una
        neteja (audit_log_prune) per no créixer indefinidament.

        Retorna l'objecte AuditEntry creat.
        """
        try:
            # deixem espai per a la nova entrada
            if self.audit_log_prune(MgrAuditLogs.AUDIT_LOG_MAX_ENTRIES - 1) != KtpRet.RET_OK:
                return KtpRet.RET_EXCEPTION

            try:
                entry = AuditEntry(
                    via=MgrAuditLogs._truncate(via, MgrAuditLogs.AUDIT_VIA_LEN),
                    user_name=MgrAuditLogs._truncate(user_name, MgrAuditLogs.AUDIT_USER_LEN),
                    ip=MgrAuditLogs._truncate(ip, MgrAuditLogs.AUDIT_IP_LEN),
                    event=MgrAuditLogs._truncate(event, MgrAuditLogs.AUDIT_EVENT_LEN),
                    result=MgrAuditLogs._truncate("ok" if ok else "fail", MgrAuditLogs.AUDIT_RESULT_LEN),
                )
                db.session.add(entry)
                db.session.commit()
                db.session.close()
                return KtpRet.RET_OK
            except Exception as e:
                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
                db.session.rollback()
                db.session.close()
                return KtpRet.RET_EXCEPTION

        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return KtpRet.RET_EXCEPTION

    def audit_log_read_all(self):
        try:
            audit_log_list = []
            audit_logs_all_qry = AuditEntry.query.order_by(AuditEntry.dt_utc.asc()).all()
            for audit_log_qry in audit_logs_all_qry:
                audit_log_dict = Utils.get_qry_dict(audit_log_qry)
                del audit_log_dict['id']
                audit_log_dict['s_dt_utc'] = audit_log_dict['dt_utc'].isoformat()
                del audit_log_dict['dt_utc']
                audit_log_list.append(audit_log_dict)

            return KtpRet.RET_OK, audit_log_list
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return KtpRet.RET_EXCEPTION, None

    def audit_log_prune(self, max_entries=AUDIT_LOG_MAX_ENTRIES):
        """
        Esborra les entrades més antigues per no superar max_entries.

        Retorna OK/ERROR
        """
        try:
            total = AuditEntry.query.count()
            if total <= max_entries:
                return KtpRet.RET_OK

            excess = total - max_entries
            oldest = (
                AuditEntry.query.order_by(AuditEntry.dt_utc.asc())
                .limit(excess)
                .all()
            )
            try:
                for e in oldest:
                    db.session.delete(e)
                db.session.commit()
                db.session.close()
                return KtpRet.RET_OK
            except Exception as e:
                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
                db.session.rollback()
                db.session.close()
                return KtpRet.RET_EXCEPTION
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return KtpRet.RET_EXCEPTION
