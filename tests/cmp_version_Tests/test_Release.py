#!/usr/bin/env GoodTests.py
'''
    Test various comparison methods specific to releases i.e. the X in 'A.B.C-X'
'''

import copy
import sys
import subprocess

import cmp_version

class TestRelease(object):


    def test_compareWithRelease(self):

        cmpFunc = cmp_version.cmp_version

        # Some equal stancing, different release
        assert cmpFunc('1.0-1', '1.0-1') == 0 , 'Expected 1.0-1 to be equal to 1.0-1'

        assert cmpFunc('1.8-2', '1.8-4') < 0 , 'Expected "1.8-2" to be less than "1.8-4"'
        assert cmpFunc('1.8-4', '1.8-2') > 0 , 'Expected "1.8-4" to be greater than "1.8-2"'

        # Different stance, different release
        assert cmpFunc('2.49.93-1', '2.49-3') > 0 , 'Expected "2.49.93-1" to be greater than "2.49-3"'
        assert cmpFunc('2.49-6', '2.49.1-6') < 0 , 'Expected "2.49-6" to be less than "2.49.1-6"'

        assert cmpFunc('5-9', '5.1') < 0 , 'Expected "5-9" to be less than "5.1"'

    def test_defaultReleaseValue(self):

        cmpFunc = cmp_version.cmp_version

        # Check release in one, not in other
        assert cmpFunc('1.5.0-1', '1.5.0') > 0 , 'Expected "1.5.0-1" to be greater than "1.5.0"'
        assert cmpFunc('1.5.0', '1.5.0-1') < 0 , 'Expected "1.5.0" to be less than "1.5.0-1"'

        # Check that a -0 release is treated same as no release
        assert cmpFunc('1.1-0', '1.1') == 0 , 'Expected "1.1-0" to be equal to "1.1"'

    def test_diffEqualVersionRelease(self):
        '''
            test_diffEqualVersionRelease - Test when a different (but equal) version has a different release
        '''

        cmpFunc = cmp_version.cmp_version

        assert cmpFunc('1.9.0-2', '1.9-3') < 0 , 'Expect "1.9.0-2" to be less than "1.9-3"'
        assert cmpFunc('1.9.0-4', '1.9-3') > 0 , 'Expect "1.9.0-4" to be greater than "1.9-3"'

        assert cmpFunc('1.1.4.0', '1.1.4-0') == 0 , 'Expected "1.1.4.0" to equal "1.1.4-0"'
        assert cmpFunc('1.1.4.0-0', '1.1.4-0') == 0 , 'Expected "1.1.4.0-0" to equal "1.1.4-0"'
        assert cmpFunc('1.1.4.0-0', '1.1.4') == 0 , 'Expected "1.1.4.0-0" to equal "1.1.4"'

    def test_complexRelease(self):

        cmpFunc = cmp_version.cmp_version

        assert cmpFunc('1.14b.6-4a',  '1.14b.6-3z') > 0 , 'Expected "1.114b.6-4a" to be greater than "1.14b.6-3z"'
        assert cmpFunc('1.14b.6-3a',  '1.14b.6-3z') < 0 , 'Expected "1.114b.6-3a" to be less than "1.14b.6-3z"'
        assert cmpFunc('1.14b.6-B',  '1.14b.6-B') == 0 , 'Expected "1.114b.6-B" to be less than "1.14b.6-B"'
        assert cmpFunc('1.14b.6-0.A',  '1.14b.6-0.A') == 0 , 'Expected "1.114b.6-0.A" to be less than "1.14b.6-0.A"'

    def test_compoundRelease(self):
        '''
            test_compoundRelease - Test when the release is a complex version
        '''

        cmpFunc = cmp_version.cmp_version

        assert cmpFunc('1.5-6.23-1', '1.5-6.23-1') == 0 , 'Expected "1.5-6.23-1" to be equal to "1.5-6.23-1"'
        assert cmpFunc('1.5-6.23', '1.5-6.23-1') < 0 , 'Expected "1.5-6.23" to be less than "1.5-6.23-1"'
        assert cmpFunc('1.5-6.23-0', '1.5-6.23') == 0 , 'Expected "1.5-6.23-0" to be equal to "1.5-6.23"'

    def test_unevenRelease(self):

        cmpFunc = cmp_version.cmp_version

        assert cmpFunc('1.0-2.0-3.0', '1.0-2.0') > 0 , 'Expected "1.0-2.0-3.0" to be greater than "1.0-2.0"'
        assert cmpFunc('1.0-2.0', '1.0-2.0-3.0') < 0 , 'Expected "1.0-2.0" to be less than "1.0-2.0-3.0"'
        assert cmpFunc('1.0-2.0', '1.0-2.0-0-0-0') == 0 , 'Expected "1.0-2.0" to be equal to "1.0-2.0-0-0-0"'
        assert cmpFunc('1.0-1.el7_6', '1.0-1.1.el7_6') < 0, 'Expected "1.0-1.el7_6" to be less than "1.0-1.1.el7_6"'


if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
