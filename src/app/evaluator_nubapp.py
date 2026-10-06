# (C) 2024 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

from app.evaluator_utilities import EvaluatorUtilities


class EvaluatorNubapp:
    """
    El mètode qr_b4a63890ed97() té per missió comprovar que la cadena passada per argument verifiqui el criteri de
    QR de NubApp.
    La cadena passada per argument pot ser:
        - La que procedeix del lector QR integrat, cas en què la cadena coincideix amb el contingut del QR.
        - La cadena procedeix d'un lector DQMINI, cas en què la cadena estarà formatada segons el format DQMINI.
    El mètode intentarà avaluar el criteri de virtuagym amb tots dos supòsits.
    """

    @staticmethod
    def qr_b4a63890ed97(s_code):
        if EvaluatorNubapp.common_criteria(s_code):
            return True
        rf_payload, qr_payload = EvaluatorUtilities.split_dqmini_standard(s_code)
        if EvaluatorNubapp.common_criteria(qr_payload):
            return True
        return False

    @staticmethod
    def common_criteria(s_code):
        return False
