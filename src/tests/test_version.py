# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

from flask import current_app
from test_base import BaseTestCase
from ztest_elements import Rock


class VersionTestCase(BaseTestCase):
    def test_get_version(self):
        Rock.get_version(capp=current_app, tco=self)
