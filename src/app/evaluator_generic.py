# (C) 2024 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

from app.evaluator_utilities import EvaluatorUtilities


class EvaluatorGeneric:
    """
    Analitza una cadena procedent d'un lector DQMINI o d'un lector QR integrat
    i en retorna la credencial (codi RF o QR) continguda a `s_code`.

    El paràmetre `s_code` pot ser:
        - Una cadena procedent del lector QR integrat, en aquest cas
          `s_code` coincideix amb el contingut del codi QR.
        - Una cadena procedent d'un lector DQMINI, en aquest cas `s_code`
          està formatada segons l'estàndard DQMINI i el mètode n'extreu
          i retorna el codi RF o QR corresponent.

    Si la cadena no segueix el format DQMINI ni conté cap payload RF/QR
    reconeixible, es retorna la cadena original netejada (strip()).
    """

    @staticmethod
    def parse_dqmini(s_code):
        rf_payload, qr_payload = EvaluatorUtilities.split_dqmini_standard(s_code)
        if rf_payload:
            return rf_payload
        if qr_payload:
            return qr_payload
        return s_code.strip()