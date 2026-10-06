# (C) 2024 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

from app.evaluator_utilities import EvaluatorUtilities


class EvaluatorVirtuagym:
    """
    El mètode qr_f84399dbec2e() té per missió comprovar que la cadena passada per argument verifiqui el criteri "tou" de
    QR de Virtuagym. Aquest criteri consisteix en comprovar que el QR comença amb la subcadena 'vg_checkin_qr='.
    La cadena passada per argument pot ser:
        - La que procedeix del lector QR integrat, cas en què la cadena coincideix amb el contingut del QR.
        - La cadena procedeix d'un lector DQMINI, cas en què la cadena estarà formatada segons el format DQMINI.
    El mètode intentarà avaluar el criteri de virtuagym amb tots dos supòsits.
    """

    @staticmethod
    def qr_f84399dbec2e(s_code):
        if EvaluatorVirtuagym.common_criteria(s_code):
            return True
        rf_payload, qr_payload = EvaluatorUtilities.split_dqmini_standard(s_code)
        if EvaluatorVirtuagym.common_criteria(qr_payload):
            return True
        return False

    @staticmethod
    def common_criteria(s_code):
        return s_code.startswith('vg_checkin_qr=')
