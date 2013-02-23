'''
Created on Feb 23, 2013

@author: Ohad Lutzky
'''

import unittest
from translationese import explicit_naming
import translationese

class TestExplicitation(unittest.TestCase):
    def testExplicitNaming(self):
        a = translationese.Analysis("She and he are better than John, Marie "
                                    "and Jim.")
        result = explicit_naming.quantify(a)
        self.assertAlmostEqual(2.0 / 3.0, result["explicit_naming"])

if __name__ == "__main__":
    unittest.main()