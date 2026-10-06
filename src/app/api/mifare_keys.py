# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
from flask_restful import Resource
from flask_restful import reqparse, request
import logging

from app.ktp_ret import KtpRet
from app.messages import Messages
from app.utilities import Utils


class AssistWriteMifareKeys(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        try:
            jso_ = request.get_json()
            parser = reqparse.RequestParser()

            parser.add_argument('position', type=str)

            # One Block, Three Blocks, Multisector
            parser.add_argument('KEYxx', type=str)
            parser.add_argument('cfg_mif_key_number', type=int)
            parser.add_argument('aux_mif_key_number', type=int)

            # Desfire
            parser.add_argument('AID', type=str)
            parser.add_argument('FID', type=str)
            parser.add_argument('F_Offset', type=int)
            parser.add_argument('F_Len', type=int)

            parser.add_argument('3KTDES', type=str)

            parser.add_argument('2KTDES', type=str)

            # MAD One Block, MAD_Three Blocks
            parser.add_argument('AID_MAD', type=str)

            args = parser.parse_args()
            uc_ret, param_failed = self.write_mifare_keys(args)
            if uc_ret == KtpRet.RET_OK:
                return Messages.MSG_MIFARE_KEYS_WRITE_OK
            else:
                raise Exception('Failed '+ param_failed)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_MIFARE_KEYS_WRITE_ERROR

    def write_mifare_keys(self, dict_params):
        ucRet = KtpRet.RET_OK
        param_failed = None
        try:
            s_position = dict_params['position']
            if dict_params.get('KEYxx') is not None:
                # One Block, Three Blocks, Multisector
                param_failed = 'KEYxx'
                if s_position == 'main' and dict_params.get('cfg_mif_key_number') is not None:
                    uc_key_number = dict_params.get('cfg_mif_key_number')
                elif s_position == 'aux' and dict_params.get('aux_mif_key_number') is not None:
                    uc_key_number = dict_params.get('aux_mif_key_number')
                else:
                    raise Exception('One Block or Three Blocks, invalid parameters')
                s_key = dict_params.get('KEYxx')
                instruction_dictio = {
                    'msgType': 'ins_mifare_key_write',
                    'msgArg': {
                        'sPosition': s_position,
                        'ucKeyNumber': uc_key_number,
                        'sKey': s_key
                    }
                }
                ans_dict = self.kapri_app.mgr_semi_offline_api_caller.autocall_let_me_know(instruction_dictio)
                ucRet = ans_dict['msgArg']['ucRet']
            elif dict_params.get('AID') is not None and dict_params.get('FID') is not None and \
                dict_params.get('F_Offset') is not None and dict_params.get('F_Len') is not None:
                # Desfire AID, FID, F_Offset, F_Len
                # ucKeyNumber == 19
                uc_key_number = 19
                param_failed = 'AID, FID, F_Offset, F_Len'
                s_f_offset = Utils.Hex2(dict_params.get('F_Offset'))
                s_f_len = Utils.Hex2(dict_params.get('F_Len'))
                s_key = dict_params.get('AID')+dict_params.get('FID')+s_f_offset+s_f_len
                instruction_dictio = {
                    'msgType': 'ins_mifare_key_write',
                    'msgArg': {
                        'sPosition': s_position,
                        'ucKeyNumber': uc_key_number,
                        'sKey': s_key
                    }
                }
                ans_dict = self.kapri_app.mgr_semi_offline_api_caller.autocall_let_me_know(instruction_dictio)
                ucRet = ans_dict['msgArg']['ucRet']
            elif dict_params.get('3KTDES') is not None:
                # Desfire
                # ucKeyNumber == 20, 21, 22, 23
                param_failed = '3KTDES'
                for uc_key_number in range(20, 24):
                    if ucRet != KtpRet.RET_OK:
                        break
                    if uc_key_number == 20:
                        s_key = dict_params.get('3KTDES')[0:12]
                    elif uc_key_number == 21:
                        s_key = dict_params.get('3KTDES')[12:24]
                    elif uc_key_number == 22:
                        s_key = dict_params.get('3KTDES')[24:36]
                    elif uc_key_number == 23:
                        s_key = dict_params.get('3KTDES')[36:48]
                    instruction_dictio = {'msgType': 'ins_mifare_key_write',
                                          'msgArg': {'sPosition': s_position, 'ucKeyNumber': uc_key_number,
                                                     'sKey': s_key}}
                    ans_dict = self.kapri_app.mgr_semi_offline_api_caller.autocall_let_me_know(instruction_dictio)
                    ucRet = ans_dict['msgArg']['ucRet']
            elif dict_params.get('2KTDES') is not None:
                # Desfire
                # ucKeyNumber == 20, 21, 22
                param_failed = '2KTDES'
                for uc_key_number in range(20, 23):
                    if ucRet != KtpRet.RET_OK:
                        break
                    if uc_key_number == 20:
                        s_key = dict_params.get('2KTDES')[0:12]
                    elif uc_key_number == 21:
                        s_key = dict_params.get('2KTDES')[12:24]
                    elif uc_key_number == 22:
                        s_key = dict_params.get('2KTDES')[24:32]+'FFFF'
                    instruction_dictio = {'msgType': 'ins_mifare_key_write',
                                          'msgArg': {'sPosition': s_position, 'ucKeyNumber': uc_key_number,
                                                     'sKey': s_key}}
                    ans_dict = self.kapri_app.mgr_semi_offline_api_caller.autocall_let_me_know(instruction_dictio)
                    ucRet = ans_dict['msgArg']['ucRet']
            elif dict_params.get('AID_MAD') is not None:
                # Mad One Block, Mad Three Blocks
                # ucKeyNumber == 19
                uc_key_number = 19
                param_failed = 'AID_MAD'
                s_key = dict_params.get('AID_MAD')+'FFFFFFFF'
                instruction_dictio = {
                    'msgType': 'ins_mifare_key_write',
                    'msgArg': {
                        'sPosition': s_position,
                        'ucKeyNumber': uc_key_number,
                        'sKey': s_key
                    }
                }
                ans_dict = self.kapri_app.mgr_semi_offline_api_caller.autocall_let_me_know(instruction_dictio)
                ucRet = ans_dict['msgArg']['ucRet']
            else:
                raise Exception('Mifare mode not specified, invalid parameters')
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_INVALIDARGUMENT
        finally:
            return ucRet, param_failed

