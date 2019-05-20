'''
    The following work authored by Tim Savannah has been dedicated to the Public Domain.
    You are free to use or modify.
'''


import re
import sys

# Python3 got rid of "cmp" for some reason :(
try:
    cmp
except NameError:
    def cmp(a, b):
        if a < b:
            return -1
        if a > b:
            return 1
        return 0

__all__ = ('cmp_version', 'VersionString')

__version__ = '3.0.0'

__version_tuple__ = (3, 0, 0)

ALPHA_OR_NUM_RE = re.compile('([a-zA-Z]+)|([0-9]+)')

EPOCH_RE = re.compile('^(?P<epoch>[0-9]+):(?P<version>.+)$')

def cmp_version(version1, version2):
    '''
        cmp_version - Compare two strings which contain versions, checking which one represents a "newer" (greater) release.

        Note that even if two version strings are not equal string-wise, they may still be equal version-wise (e.x. 1.0.0 is the same version as 1.0)

        This supports handling "release" parts (-whatever) and "Epochs" ( N:version )

        @param version1 <str> - A string containing a version
        @param version2 <str> - A string containing a version

        @return <int>
            -1  if version1 is older/less than version2
            0   if version1 is equal to version2
            1   if version1 is newer/greater than version2

        So for example,

            cmp_version('1.0.5b', '1.0.5a') would return 1 because 1.0.5b comes after 1.0.5a
    '''
    # Call the "internal" function so we can call recursively and apply logic like
    #   "only if at the start of version" (consideration for Epoch) accurately
    #   without fudging up the public interface
    return _cmp_version_internal(version1, version2)


def _cmp_version_internal(version1, version2, versionIdxNum=0):
    '''
        _cmp_version_internal - Internal worker for cmp_version
            
            @param versionIdxNum - The version "part" (e.x. split on release)


            @see cmp_version

    '''
    # Ensure we are using strings, so VersionString doesn't recurse
    version1 = str(version1) or '0'
    version2 = str(version2) or '0'


    # Check if they are the same
    if version1 == version2:
        return 0

    
    if versionIdxNum == 0:
        # If we are on the first part of version, 
        #  check if we have epochs to consider
        #    Default to epoch 0
        epochMatch1 = EPOCH_RE.match(version1)
        if epochMatch1:
            epochMatch1Groupdict = epochMatch1.groupdict()

            epoch1 = int(epochMatch1Groupdict['epoch'] or '0')
            version1 = epochMatch1Groupdict['version'] or '0'
        else:
            epoch1 = 0

        epochMatch2 = EPOCH_RE.match(version2)
        if epochMatch2:
            epochMatch2Groupdict = epochMatch2.groupdict()

            epoch2 = int(epochMatch2Groupdict['epoch'] or '0')
            version2 = epochMatch2Groupdict['version'] or '0'
        else:
            epoch2 = 0

        # If epochs are not equal, the higher one wins no matter what
        if epoch1 > epoch2:
            return 1
        elif epoch1 < epoch2:
            return -1
    

    # If there is a release portion, split it out and treat it as a lower-proirity version compare
    version1ReleaseSplit = version1.split('-') #re.split('-', version1)
    version2ReleaseSplit = version2.split('-') #re.split('-', version2)

    # If we have at least one release
    if len(version1ReleaseSplit) > 1 or len(version2ReleaseSplit) > 1:
        # Compare the first part as normal version
        firstPartCmp = _cmp_version_internal(version1ReleaseSplit[0], version2ReleaseSplit[0], versionIdxNum+1)
        if firstPartCmp != 0:
            # If first part is not equal, return that
            return firstPartCmp
        else:
            # Otherwise move onto the next section ( release )
            popVal1 = version1ReleaseSplit.pop(0)
            popVal2 = version2ReleaseSplit.pop(0)

            # Defalt to 0 if no entry
            if version1ReleaseSplit:
                nextVal1 = version1ReleaseSplit.pop(0)
            else:
                nextVal1 = '0'
            if version2ReleaseSplit:
                nextVal2 = version2ReleaseSplit.pop(0)
            else:
                nextVal2 = '0'
            
            # Compare second entry
            cmpRes = _cmp_version_internal(nextVal1, nextVal2, versionIdxNum+1)
            if cmpRes != 0:
                # If not equal, return result
                return cmpRes
            else:
                if not version1ReleaseSplit and not version2ReleaseSplit:
                    # If parts are equal and no parts remain, we are equal
                    return 0
                else:
                    # Recurse on remaining parts
                    return _cmp_version_internal('-'.join(version1ReleaseSplit), '-'.join(version2ReleaseSplit), versionIdxNum+1)


    # If prefixed or suffixed with a ., insert a '0'
    if version1.startswith('.'):
        version1 = '0' + version1
    if version1.endswith('.'):
        version1 = version1 + '0'

    if version2.startswith('.'):
        version2 = '0' + version2
    if version2.endswith('.'):
        version2 = version2 + '0'

    # Split into "blocks", wherein each . is a unit
    #  which will be compared left-to-right.
    version1Split = version1.split('.')
    version2Split = version2.split('.')

    version1Len = len(version1Split)
    version2Len = len(version2Split)

    # Ensure we have the same number of blocks by
    #  appending '0' until length is the same.
    # This ensures that things like 1.1.0 == 1.1
    #  and simplifies the loop below as well.
    while version1Len < version2Len:
        version1Split += ['0']
        version1Len += 1
    else:
        while version2Len < version1Len:
            version2Split += ['0']
            version2Len += 1

    # Check if the additional padding has made the items equal
    if version1Split == version2Split:
        return 0

    # Transverse through each block
    for i in range(version1Len):
        try:
            # If block contains only integers, do a direct comparison.
            cmpRes = cmp(int(version1Split[i]), int(version2Split[i]))
            if cmpRes != 0:
                return cmpRes
        except ValueError:
            # Some sort of letter in here

            # Split intro groups of numbers and groups of letters
            #  for comparison
            # Letters are considered greater than numbers,
            #  e.x. 1.1a > 1.19

            # Results of these findall will be list of tuples,
            #  where first element of tuple is alpha characters
            #  and second element is numeric.
            try1 = ALPHA_OR_NUM_RE.findall(version1Split[i])
            try1Len = len(try1)
            try2 = ALPHA_OR_NUM_RE.findall(version2Split[i])
            try2Len = len(try2)
            for j in range(len(try1)):

                if j >= try2Len:
                    # We've gone past the end of version2
                    #  but there is more in version1, so
                    #  version1 is greater.
                    return 1

                # Compare next two blocks
                (alpha1, numeric1) = try1[j]
                (alpha2, numeric2) = try2[j]

                # Some of alpha is empty string, so don't compare them
                if alpha1 and alpha2:
                    resAlpha = cmp(alpha1.lower(), alpha2.lower())
                    if resAlpha != 0:
                        # Alpha blocks are not the same, we are done.
                        return resAlpha

                # Alpha are same or empty, so compare digits
                resNumeric = 0
                if numeric1:
                    if numeric2:
                        # Have digits in both, compare them
                        resNumeric = cmp(int(numeric1), int(numeric2))
                        if resNumeric != 0:
                            # Difference in numbers, return cmp result.
                            return resNumeric
                    else:
                        # Only digits in version1's block, thus version1 is greater
                        return 1
                else:
                    if numeric2:
                        # Only digits in version2's block, thus version1 is smaller
                        return -1

            if try2Len > try1Len:
                # All in version1's block match version2's block
                #  up to this point, and version2 has more to go,
                #  so it wins.
                return -1

    # End of the line,
    return 0


class VersionString(str):
    '''
        A string where all comparison methods will compare as versions.

        This supports all the rich comparison operators.

        Example:

            >> version1 = VersionString('1.1b')
            >> version2 = VersionString('1.1a')
            >> version1 > version2
            True

    '''

    def __cmp__(self, other):
        return cmp_version(self, other)

    def __lt__(self, other):
        return bool(cmp_version(self, other) < 0)

    def __le__(self, other):
        return bool(cmp_version(self, other) <= 0)

    def __gt__(self, other):
        return bool(cmp_version(self, other) > 0)

    def __ge__(self, other):
        return bool(cmp_version(self, other) >= 0)

    def __eq__(self, other):
        return bool(cmp_version(self, other) == 0)

    def __ne__(self, other):
        return bool(cmp_version(self, other) != 0)


    def __add__(self, other):
        return VersionString(str(self) + str(other))

    def __repr__(self):
        return 'VersionString(%s)' %(str.__repr__(self),)
