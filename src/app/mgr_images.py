# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
import os
from PIL import Image
import io
import base64
import logging

from app.global_consts import GlobalConsts
from app.ktp_ret import KtpRet
from k_check import KCheck


class MgrImages:

    def __init__(self, app):
        self.app = app

    def store(self, sImgName, sImgB64):
        ucRet = KtpRet.RET_EXCEPTION
        try:
            listOfFiles = os.listdir(self.app.config['ROUTES']['routes_imgrepo_dir'])
            if len(listOfFiles) > GlobalConsts.get('const_images_max_number_of_files_in_directory'):
                ucRet = KtpRet.RET_FAILED
            elif len(sImgB64) > (8 / 6) * GlobalConsts.get('const_images_max_file_size'):
                ucRet = KtpRet.RET_INVALIDARGUMENT
            elif sImgName.lower() in GlobalConsts.get('const_images_excluded_names_to_store'):
                ucRet = KtpRet.RET_INVALIDARGUMENT
            elif not KCheck.is_ending_in_list(sImgName.lower(), GlobalConsts.get('const_images_included_extensions')):
                ucRet = KtpRet.RET_INVALIDARGUMENT
            else:
                try:
                    bImgB64 = sImgB64.encode()
                    binimage = base64.b64decode(bImgB64)
                    # Validem que sigui imatge correcta
                    with io.BytesIO(binimage) as buffer:
                        with Image.open(buffer) as ImgCandidate:
                            bValidImage = True
                    img_file = os.path.join(self.app.config['ROUTES']['routes_imgrepo_dir'], sImgName)
                    with open(img_file, "wb") as fh:
                        fh.write(base64.decodebytes(bImgB64))
                        ucRet = KtpRet.RET_OK
                except IOError as ioe:
                    logging.debug(f'{inspect.stack()[0][3]} Exception: {str(ioe)} (called by: {inspect.stack()[1][3]})')
                    ucRet = KtpRet.RET_INVALIDARGUMENT
                except Exception as e:
                    logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
                    ucRet = KtpRet.RET_EXCEPTION
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_EXCEPTION
        finally:
            return ucRet

    def retrieve(self, sImgName):
        ucRet = KtpRet.RET_EXCEPTION
        sImgB64 = ''
        try:
            img_file = os.path.join(self.app.config['ROUTES']['routes_imgrepo_dir'], sImgName)
            with open(img_file, 'rb') as fh:
                binimage = fh.read()
                sImgB64 = base64.b64encode(binimage).decode()
                ucRet = KtpRet.RET_OK
        except FileNotFoundError as fnfe:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(fnfe)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_INVALIDARGUMENT
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_EXCEPTION
        finally:
            return ucRet, sImgB64

    def list(self):
        ucRet = KtpRet.RET_EXCEPTION
        listImgNames = []
        try:
            listImgNames = [fn for fn in os.listdir(self.app.config['ROUTES']['routes_imgrepo_dir'])
                           if any(fn.lower().endswith(ext) for ext in GlobalConsts.get('const_images_included_extensions'))]
            ucRet = KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_EXCEPTION
        finally:
            return ucRet, listImgNames

    def remove(self, sImgName):
        ucRet = KtpRet.RET_EXCEPTION
        try:
            if sImgName.lower() in GlobalConsts.get('const_images_excluded_names_to_remove'):
                ucRet = KtpRet.RET_INVALIDARGUMENT
            else:
                img_file = os.path.join(self.app.config['ROUTES']['routes_imgrepo_dir'], sImgName)
                os.remove(img_file)
                ucRet = KtpRet.RET_OK
        except OSError as ose:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(ose)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_INVALIDARGUMENT
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_EXCEPTION
        finally:
            return ucRet
