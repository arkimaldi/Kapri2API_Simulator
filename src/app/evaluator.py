# (C) 2024 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

"""
Aquest mòdul té per missió avaluar les expressions condicionals que poden acompanyar a les instruccions d'un lot semi-offline.
Les expressions podran tenir:
    Les variables d'event:
        v_event (el diccionari de l'event que dispara el processament semi-offline)
    Les variables d'instrucció:
        v_eval_0, v_eval_1, v_eval_2, v_eval_3 (contenen el resultat de l'avaluació anterior desada amb "@v_eval_x" on x=0, 1,2,3)
    Les variables de resposta:
        v_answer (el diccionari de l'answer de la instrucció anterior)
    Les funcions:
        len()
        int()
        str()
        hex()
        f_in_white_list()
        f_in_black_list()
        f_time()
        f_trim()
        f_parse_dqmini()     - personalització Genrèrica
        f_qr_b4a63890ed97()  - personalització NubApp
        f_qr_f84399dbec2e()  - personalització Virtuagym



Quan s'inicia el processament d'un lot caldrà instanciar un objecte d'aquesta classe, passant-li l'event que l'ha disparat.
    La variable v_event s'inicialitzarà amb les dades de l'event on_event
    La variable v_answer s'inicialitza a None
    Les variables v_eval_x on x=0..3, s'inicien a True

Llavors, mentre es bucla per cadascuna de les instruccions del lot, es cridarà al mètode enter_conditioned_instruction(conditioned_instruction),
que retornarà la instrucció sense la clàusula de condicionament si la avaluació es True, o {} si la avaluació es False.
En cas que retorni la instrucció, aquesta s'enviarà a l'intèrpret, i la resposta de la qual s'incorporarà a l'evaluator
mitjançant el mètode enter_answer(answer) que la desarà a v_answer.

"""

import inspect
import json
import time

from app.evaluator_generic import EvaluatorGeneric
from app.evaluator_nubapp import EvaluatorNubapp
from app.evaluator_virtuagym import EvaluatorVirtuagym

import logging


class Evaluator:

    def __init__(self, app, mgr_semi_offline_lists, original_on_event):
        self.app = app
        self.mgr_semi_offline_lists = mgr_semi_offline_lists
        # variable d'event
        try:
            self.v_event = json.loads(json.dumps(original_on_event))
        except Exception as e:
            self.v_event = None
        # variables de la condició
        self.v_eval_x = [True, True, True, True]  # contenen el resultat de la avaluació anterior desada amb "@x" on x=0,1,2,3). Inicialment True
        # variable de l'answer
        self.v_answer = None

    def enter_conditioned_instruction(self, original_conditioned_instruction):
        instruction = {}
        try:
            v_dict = {
                'v_event': self.v_event,
                'v_eval_x': self.v_eval_x,
                'v_answer': self.v_answer,
            }
            conditioned_instruction = json.loads(json.dumps(original_conditioned_instruction))
            expression_to_eval = conditioned_instruction.get('c')
            if expression_to_eval is None:
                instruction = conditioned_instruction
            else:
                b_eval_store = False
                i_eval_idx = 0
                expression_to_eval = expression_to_eval.strip()
                if expression_to_eval[-9:] in ['@v_eval_0', '@v_eval_1', '@v_eval_2', '@v_eval_3']:
                    b_eval_store = True
                    i_eval_idx = int(expression_to_eval[-1:])
                    expression_to_eval = expression_to_eval[:-9]
                eval_result = self.b_evalue(expression_to_eval, v_dict)
                if b_eval_store:
                    self.v_eval_x[i_eval_idx] = eval_result
                if eval_result:
                    del conditioned_instruction['c']
                    instruction = conditioned_instruction
                else:
                    instruction = {}
            instruction = self.o_evalue_lblmgr_odata(instruction, v_dict)
        except Exception as e:
            instruction = {}
        finally:
            return instruction

    def enter_answer(self, original_answer):
        try:
            self.v_answer = json.loads(json.dumps(original_answer))
        except Exception as e:
            self.v_answer = None

    def b_evalue(self, expression_to_eval, v_dict):
        b_eval = False
        try:
            b_eval = self.o_evalue(expression_to_eval, v_dict)
            if not isinstance(b_eval, bool):
                raise
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            b_eval = False
        finally:
            return b_eval

    def o_evalue(self, expression_to_eval, v_dict):
        """
        :param expression_to_eval: string
        :param v_dict: exemple {'pv_a': pv_a, 'pv_b': pv_b}
        :return: None si hi ha hagut error,
                 True: si l'expressió s'avalua com True,
                 False si s'avalua com False
        """

        # definim les funcions estrictament locals
        def f_in_white_list(s_code):
            return self.mgr_semi_offline_lists.is_in_white_list(s_code)

        def f_in_black_list(s_code):
            return self.mgr_semi_offline_lists.is_in_black_list(s_code)

        def f_time():
            return time.time()

        def f_trim(s_code):
            return s_code.strip()

        def f_parse_dqmini(s_code):
            return EvaluatorGeneric.parse_dqmini(s_code)

        def f_qr_b4a63890ed97(s_code):
            return EvaluatorNubapp.qr_b4a63890ed97(s_code)

        def f_qr_f84399dbec2e(s_code):
            return EvaluatorVirtuagym.qr_f84399dbec2e(s_code)

        # fi definicions de funcions estrictament locals

        o_eval = None
        try:
            # validem el paràmetre expression_to_eval
            if not isinstance(expression_to_eval, str):
                raise
            if expression_to_eval.find('__') > 0:
                raise
            if len(expression_to_eval) > 1024:
                raise

            # copiem els valors de les variables d'interès en noves variables estrictament locals
            v_dict = json.loads(json.dumps(v_dict))
            v_event = v_dict['v_event']
            v_eval_0 = v_dict['v_eval_x'][0]
            v_eval_1 = v_dict['v_eval_x'][1]
            v_eval_2 = v_dict['v_eval_x'][2]
            v_eval_3 = v_dict['v_eval_x'][3]
            v_answer = v_dict['v_answer']

            # generem el diccionari d'objectes que es podran evaluar
            lo = locals()
            safe_list = ['f_in_white_list', 'f_in_black_list', 'f_time', 'f_trim',  'f_parse_dqmini', 'f_qr_b4a63890ed97', 'f_qr_f84399dbec2e', 'v_event', 'v_eval_0', 'v_eval_1', 'v_eval_2', 'v_eval_3', 'v_answer']
            safe_dict = dict([(k, lo.get(k, None)) for k in safe_list])
            # add any needed builtins back in
            safe_dict['len'] = len
            safe_dict['int'] = int
            safe_dict['str'] = str
            safe_dict['hex'] = hex
            o_eval = eval(expression_to_eval, {"__builtins__": None}, safe_dict)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            o_eval = None
        finally:
            return o_eval

    def o_evalue_lblmgr_odata(self, instruction, v_dict):
        try:
            if instruction.get('msgType') == 'ins_lblmgr_set':
                o_data = instruction['msgArg']['oData']
                evaluated_odata = {}
                for k, v in o_data.items():
                    evaluated_odata[k] = v
                    if self.b_contain_safe_list(v):
                        evaluated_v = self.o_evalue(v, v_dict)
                        if evaluated_v is not None:
                            evaluated_odata[k] = evaluated_v
                instruction['msgArg']['oData'] = evaluated_odata
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            return instruction

    def b_contain_safe_list(self, s_value):
        if isinstance(s_value, str):
            safe_list = ['f_in_white_list', 'f_in_black_list', 'f_time', 'f_trim',  'f_parse_dqmini', 'f_qr_b4a63890ed97', 'f_qr_f84399dbec2e', 'v_event', 'v_eval_0', 'v_eval_1', 'v_eval_2', 'v_eval_3', 'v_answer']
            for w in safe_list:
                if s_value.find(w) >= 0:
                    return True
        return False
