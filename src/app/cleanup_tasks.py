# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

# import inspect
# from datetime import datetime, timedelta
# from flask import current_app
# import logging
#
# from app.db_models import DeviceLogs, CredentialsRequests, AccessRequests
# from app.extensions import scheduler, db
#
#
# @scheduler.task(trigger='interval', id='clean_device_logs', days=30)
# def task_clean_device_logs():
#     """
#     Gestió d'esborrat de logs més antics de cfg_devices_logs_delete_threshold_in_days.
#     """
#     with scheduler.app.app_context():
#         threshold_in_days = current_app.config['API']['devices_logs_delete_threshold_in_days']
#         dt_threshold = datetime.utcnow() + timedelta(days=threshold_in_days)
#         try:
#             db.session.query(DeviceLogs).filter(DeviceLogs.datetimestamp < dt_threshold).delete()
#             db.session.commit()
#         except Exception as e:
#             db.session.rollback()
#             logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

