# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

from flask_restful import Resource
import inspect
import logging

from app.global_consts import GlobalConsts


class Version(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def get(self):
        try:
            return {'version': GlobalConsts.get('const_my_version')}
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return {}

