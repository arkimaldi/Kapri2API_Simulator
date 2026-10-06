# (C) 2024 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.


class EvaluatorUtilities:

    @staticmethod
    def split_dqmini_standard(in_frame):
        """
        Donada una trama de DQ-MINI, n'extreu la lectura discriminant si procedeix de RF o de QR
        """
        rf_payload = None
        qr_payload = None
        try:
            open_pos = in_frame.find('[')
            close_pos = in_frame.find(']')
            if open_pos >= 2 and close_pos >= 3 and close_pos > open_pos:
                payload = in_frame[open_pos + 1:close_pos]
                channel = in_frame[open_pos - 2:open_pos]
                if channel == 'QR':
                    qr_payload = payload
                elif channel == 'RF':
                    rf_payload = payload
        except Exception as e:
            pass
        finally:
            return rf_payload, qr_payload