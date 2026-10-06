# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
from flask_restful import Resource, reqparse
import logging

from app.ktp_ret import KtpRet
from app.messages import Messages


class ScreenImagesList(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def get(self):
        try:
            uc_ret, listImgNames = self.kapri_app.mgr_images.list()
            if uc_ret == KtpRet.RET_OK:
                return {'status_code': 200, 'listImgNames': listImgNames}
            else:
                raise Exception('Failed ')
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_SCREEN_IMAGES_LIST_ERROR


class ScreenimagesView(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def get(self, sImgName):
        try:
            uc_ret, s_img_b64 = self.kapri_app.mgr_images.retrieve(sImgName)
            if uc_ret == KtpRet.RET_OK:
                return {'status_code': 200, 'sImgB64': s_img_b64}
            else:
                raise Exception('Failed ')
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_SCREEN_IMAGES_VIEW_ERROR


class ScreenImagesDelete(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def get(self, sImgName):
        try:
            uc_ret = self.kapri_app.mgr_images.remove(sImgName)
            if uc_ret == KtpRet.RET_OK:
                return {'status_code': 200}
            else:
                raise Exception('Failed ')
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_SCREEN_IMAGES_DELETE_ERROR


class ScreenImagesStore(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('sImgName', type=str, help='Image name')
            parser.add_argument('sImgB64', type=str, help='Image b64')
            args = parser.parse_args()

            sImgName = args['sImgName']
            sImgB64 = args['sImgB64']

            uc_ret = self.kapri_app.mgr_images.store(sImgName, sImgB64)
            if uc_ret == KtpRet.RET_OK:
                return {'status_code': 200}
            else:
                raise Exception('Failed ')
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_SCREEN_IMAGES_ADD_ERROR

