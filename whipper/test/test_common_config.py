# -*- Mode: Python; test-case-name: whipper.test.test_common_config -*-
# vi:si:et:sw=4:sts=4:ts=4

import os
import tempfile

from whipper.common import config

from whipper.test import common as tcommon


class ConfigTestCase(tcommon.TestCase):

    def setUp(self):
        fd, self._path = tempfile.mkstemp(suffix=u'.whipper.test.config')
        os.close(fd)
        self._config = config.Config(self._path)

    def tearDown(self):
        os.unlink(self._path)

    def testAddReadOffset(self):
        self.assertRaises(KeyError,
            self._config.getReadOffset, 'PLEXTOR ', 'DVDR   PX-L890SA', '1.05')
        self._config.setReadOffset('PLEXTOR ', 'DVDR   PX-L890SA', '1.05', 6)

        # getting it from memory should work
        offset = self._config.getReadOffset('PLEXTOR ', 'DVDR   PX-L890SA',
            '1.05')
        self.assertEquals(offset, 6)

        # and so should getting it after reading it again
        self._config.open()
        offset = self._config.getReadOffset('PLEXTOR ', 'DVDR   PX-L890SA',
            '1.05')
        self.assertEquals(offset, 6)

    def testAddReadOffsetSpaced(self):
        self.assertRaises(KeyError,
            self._config.getReadOffset, 'Slimtype', 'eSAU208   2     ', 'ML03')
        self._config.setReadOffset('Slimtype', 'eSAU208   2     ', 'ML03', 6)

        # getting it from memory should work
        offset = self._config.getReadOffset(
            'Slimtype', 'eSAU208   2     ', 'ML03')
        self.assertEquals(offset, 6)

        # and so should getting it after reading it again
        self._config.open()
        offset = self._config.getReadOffset(
            'Slimtype', 'eSAU208   2     ', 'ML03')
        self.assertEquals(offset, 6)

    def testDefeatsCache(self):
        self.assertRaises(KeyError, self._config.getDefeatsCache,
            'PLEXTOR ', 'DVDR   PX-L890SA', '1.05')

        self._config.setDefeatsCache(
            'PLEXTOR ', 'DVDR   PX-L890SA', '1.05', False)
        defeats = self._config.getDefeatsCache(
            'PLEXTOR ', 'DVDR   PX-L890SA', '1.05')
        self.assertEquals(defeats, False)

        self._config.setDefeatsCache(
            'PLEXTOR ', 'DVDR   PX-L890SA', '1.05', True)
        defeats = self._config.getDefeatsCache(
            'PLEXTOR ', 'DVDR   PX-L890SA', '1.05')
        self.assertEquals(defeats, True)
