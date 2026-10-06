# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import unittest
from flask import current_app
from flask_migrate import upgrade, downgrade

from app.extensions import db


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.test_client = current_app.test_client()
        # Apply all the database migrations
        upgrade()

    def tearDown(self):
        db.session.remove()
        downgrade(revision='base')


class ContextTestCase(BaseTestCase):
    def test_app_context_exists(self):
        self.assertFalse(current_app is None)
