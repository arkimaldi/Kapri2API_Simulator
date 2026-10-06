# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
import json
import logging

from app.post_woman import PostWoman


class MgrSemiOfflineApiCaller:

    def __init__(self, app):
        self.app = app

    def autocall_let_me_know(self, my_dictio):
        # Farem servir aquesta funció per totes les crides API al LetMeKnow del propi Kapri2API
        # per tal de processar les instruccions que venen en batch del semi-offline
        try:
            # fem una còpia del diccionari original i li afegim  l' sInsPwd si cal
            my_dictio_expanded = json.loads(json.dumps(my_dictio))
            try:
                if self.app.mgr_interface_global.get_interface_ins_pwd() is not None:
                    my_dictio_expanded['msgArg']['sInsPwd'] = self.app.mgr_interface_global.get_interface_ins_pwd()
            except Exception as e:
                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            # l'enviem a la API let_me_know_instruction_from_semi_offline
            api_port = self.app.config['API']['api_port']
            my_url = f'http://127.0.0.1:{api_port}/api/let_me_know_instruction_from_semi_offline'
            result = PostWoman.send_post(my_url, my_dictio_expanded)
            return result
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return {'Error': str(e)}




