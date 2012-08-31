# Import this to be able to load parent directory modules
from initSubdir import checkSubdirPath; checkSubdirPath(__name__)
import unittest
import re
import itertools
import regextypes
import regexdatatypes

def allCasings(inStr):
    return (''.join(t) for t in itertools.product(*zip(inStr.lower(), inStr.upper())))
                
def prefixSuffixWhitespace(prefix, suffix):
    return (not prefix or prefix.isspace()) and (not suffix or suffix.isspace())

class RegexTypesTest(unittest.TestCase):
    def setUp(self):
        # Don't put any 'true' or 'false' statements in falseChecks, prefixes, or suffixes
        self.falseChecks = ["", " \t \n ", "a", "a ", " a", " a ", ".", " . ", "e", " e "]
        self.prefixes = ["", " ", "a", "abcd", "two words", " space sep "]
        self.suffixes = self.prefixes
        self.integerStrs = ["0", "1", "-1", "12345", "-12345"]
        self.floatStrs = ["0.0", "0.", ".0",
                          "1.0", "1.", ".1", 
                          "-1.0", "-1.", "-.1",
                          "12345.", "123.45", ".12345",
                          "-12345.", "-123.45", "-.12345"]
        # Python can't handle floating exponentials in the num-'e'-num format
        self.expStrs = [estrPre+"e"+estrPost for estrPre in self.integerStrs + self.floatStrs
                                             for estrPost in self.integerStrs]
        self.trueStrs = [tc for tc in allCasings("true")]
        self.falseStrs = [fc for fc in allCasings("false")]
    
    # Helper function for function naming
    def noneCheckStr(self, testFunc):
        if testFunc == self.assertIsNotNone:
            return "not None"
        elif testFunc == self.assertIsNone:
            return "None"
        else:
            raise ValueError("Invalid test function to convert")
        
    '''
    Runs a suite of tests on a regular expression. The intAssertChooser
    and other Chooser paramters should be functions of the following form:
    
    intAssertChooser : [assertIsNone or assertIsNotNone]  <= prefix, string, suffix
    floatAssertChooser : [assertIsNone or assertIsNotNone]  <= prefix, string, suffix 
    expAssertChooser : [assertIsNone or assertIsNotNone]  <= prefix, string, suffix
    boolAssertChooser : [assertIsNone or assertIsNotNone]  <= prefix, string, suffix, isTrueStr
    
    additionalTests can define an iterable of other tests to be run with
    the form:
    
    intAssertChooser : None  <= prefix, suffix
    '''
    def runRegexTest(self, regex, intAssertChooser, floatAssertChooser, 
                     expAssertChooser, boolAssertChooser, additionalTests=None):
        assertFunc = self.assertIsNone
        for checkstr in self.falseChecks:
            assertFunc(re.search(regex, checkstr),
                       "String '"+checkstr+"' should have returned "+
                       self.noneCheckStr(assertFunc))
            
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                # Test integer strings
                for checkstr in self.integerStrs:
                    assertFunc = intAssertChooser(prefix, checkstr, suffix)
                    assertFunc(re.search(regex, prefix+checkstr+suffix), 
                               "String '"+prefix+checkstr+suffix+"' should have returned "+
                               self.noneCheckStr(assertFunc))
                    
                # Test float strings
                for checkstr in self.floatStrs:
                    assertFunc = floatAssertChooser(prefix, checkstr, suffix)
                    assertFunc(re.search(regex, prefix+checkstr+suffix), 
                               "String '"+prefix+checkstr+suffix+"' should have returned "+
                               self.noneCheckStr(assertFunc))
                    
                # Test exponential strings
                for checkstr in self.expStrs:
                    assertFunc = expAssertChooser(prefix, checkstr, suffix)
                    assertFunc(re.search(regex, prefix+checkstr+suffix), 
                               "String '"+prefix+checkstr+suffix+"' should have returned "+
                               self.noneCheckStr(assertFunc))
            
                for checkstr in self.trueStrs:
                    assertFunc = boolAssertChooser(prefix, checkstr, suffix, True)
                    assertFunc(re.search(regex, prefix+checkstr+suffix), 
                               "String '"+prefix+checkstr+suffix+"' should have returned "+
                               self.noneCheckStr(assertFunc))
                
                for checkstr in self.falseStrs:
                    assertFunc = boolAssertChooser(prefix, checkstr, suffix, False)
                    assertFunc(re.search(regex, prefix+checkstr+suffix), 
                               "String '"+prefix+checkstr+suffix+"' should have returned "+
                               self.noneCheckStr(assertFunc))
                
                # Run any additional tests provided for the prefix/suffix
                if additionalTests != None:
                    for test in additionalTests:
                        test(prefix, suffix)
    
    '''
    Numerics Tests
    '''
    def testContainsNonExpNumericalRegex(self):
        def checkNumberExpMatches(prefix, suffix):
            for checkstr in self.expStrs:
                numExpected = 2
                findAllResults = len(re.findall(regextypes.containsNumericalNonExpRegex, prefix+checkstr+suffix))
                self.assertEqual(findAllResults, numExpected, "String '"+prefix+checkstr+suffix+
                                    "' should have returned "+str(numExpected)+
                                    " matches and instead returned " + str(findAllResults))
        
        self.runRegexTest(regex=regextypes.containsNumericalNonExpRegex, 
                          intAssertChooser=lambda p,c,s: self.assertIsNotNone,
                          floatAssertChooser=lambda p,c,s: self.assertIsNotNone,
                          expAssertChooser=lambda p,c,s: self.assertIsNotNone,
                          boolAssertChooser=lambda p,c,s,t: self.assertIsNone,
                          additionalTests=[checkNumberExpMatches])
                    
    def testNonExpNumericalRegex(self):
        whiteSpaceSensAssert = lambda p,c,s: (self.assertIsNotNone if prefixSuffixWhitespace(p,s) 
                                              else self.assertIsNone)
        self.runRegexTest(regex=regextypes.numericalNonExpRegex, 
                          intAssertChooser=whiteSpaceSensAssert,
                          floatAssertChooser=whiteSpaceSensAssert,
                          expAssertChooser=lambda p,c,s: self.assertIsNone,
                          boolAssertChooser=lambda p,c,s,t: self.assertIsNone)

    def testContainsNumericalRegex(self):
        def checkNumberExpMatches(prefix, suffix):
            for checkstr in self.expStrs:
                numExpected = 1
                findAllResults = len(re.findall(regextypes.containsNumericalRegex, prefix+checkstr+suffix))
                self.assertEqual(findAllResults, numExpected, "String '"+prefix+checkstr+suffix+
                                    "' should have returned "+str(numExpected)+
                                    " matches and instead returned " + str(findAllResults))
        
        self.runRegexTest(regex=regextypes.containsNumericalRegex, 
                          intAssertChooser=lambda p,c,s: self.assertIsNotNone,
                          floatAssertChooser=lambda p,c,s: self.assertIsNotNone,
                          expAssertChooser=lambda p,c,s: self.assertIsNotNone,
                          boolAssertChooser=lambda p,c,s,t: self.assertIsNone,
                          additionalTests=[checkNumberExpMatches])
                    
    def testNumericalRegex(self):
        whiteSpaceSensAssert = lambda p,c,s: (self.assertIsNotNone if prefixSuffixWhitespace(p,s) 
                                              else self.assertIsNone)
        self.runRegexTest(regex=regextypes.numericalRegex, 
                          intAssertChooser=whiteSpaceSensAssert,
                          floatAssertChooser=whiteSpaceSensAssert,
                          expAssertChooser=whiteSpaceSensAssert,
                          boolAssertChooser=lambda p,c,s,t: self.assertIsNone)
    
    '''
    Float Tests
    '''
    def testContainsNonExpFloatRegex(self):
        def checkNumberExpMatches(prefix, suffix):
            for checkstr in self.expStrs:
                # Determine how many results we should have from findall
                numExpected = (prefix+checkstr+suffix).count('.')
                findAllResults = len(re.findall(regextypes.containsFloatingNonExpRegex, prefix+checkstr+suffix))
                self.assertEqual(findAllResults, numExpected, "String '"+prefix+checkstr+suffix+
                                    "' should have returned "+str(numExpected)+
                                    " matches and instead returned " + str(findAllResults))
        
        self.runRegexTest(regex=regextypes.containsFloatingNonExpRegex, 
                          intAssertChooser=lambda p,c,s: self.assertIsNone,
                          floatAssertChooser=lambda p,c,s: self.assertIsNotNone,
                          expAssertChooser=lambda p,c,s: (self.assertIsNone if c.count('.') == 0 
                                                                            else self.assertIsNotNone),
                          boolAssertChooser=lambda p,c,s,t: self.assertIsNone,
                          additionalTests=[checkNumberExpMatches])
                    
    def testNonExpFloatRegex(self):
        whiteSpaceSensAssert = lambda p,c,s: (self.assertIsNotNone if prefixSuffixWhitespace(p,s) 
                                              else self.assertIsNone)
        self.runRegexTest(regex=regextypes.floatingNonExpRegex, 
                          intAssertChooser=lambda p,c,s: self.assertIsNone,
                          floatAssertChooser=whiteSpaceSensAssert,
                          expAssertChooser=lambda p,c,s: self.assertIsNone,
                          boolAssertChooser=lambda p,c,s,t: self.assertIsNone)
                    
    def testContainsFloatRegex(self):
        def checkNumberExpMatches(prefix, suffix):
            for checkstr in self.expStrs:
                # Determine how many results we should have from findall
                numExpected = 1
                findAllResults = len(re.findall(regextypes.containsFloatingRegex, prefix+checkstr+suffix))
                self.assertEqual(findAllResults, numExpected, "String '"+prefix+checkstr+suffix+
                                    "' should have returned "+str(numExpected)+
                                    " matches and instead returned " + str(findAllResults))
        
        self.runRegexTest(regex=regextypes.containsFloatingRegex, 
                          intAssertChooser=lambda p,c,s: self.assertIsNone,
                          floatAssertChooser=lambda p,c,s: self.assertIsNotNone,
                          expAssertChooser=lambda p,c,s: self.assertIsNotNone,
                          boolAssertChooser=lambda p,c,s,t: self.assertIsNone,
                          additionalTests=[checkNumberExpMatches])
                    
    def testFloatRegex(self):
        whiteSpaceSensAssert = lambda p,c,s: (self.assertIsNotNone if prefixSuffixWhitespace(p,s) 
                                              else self.assertIsNone)
        def convertType(prefix, suffix):
            for checkstr in self.floatStrs + self.expStrs:
                if prefixSuffixWhitespace(prefix, suffix):
                    # This should not raise an exception
                    float(checkstr)
        self.runRegexTest(regex=regextypes.floatingRegex, 
                          intAssertChooser=lambda p,c,s: self.assertIsNone,
                          floatAssertChooser=whiteSpaceSensAssert,
                          expAssertChooser=whiteSpaceSensAssert,
                          boolAssertChooser=lambda p,c,s,t: self.assertIsNone,
                          additionalTests=[convertType])
    
    '''
    Integer Tests
    '''
    def testContainsIntegerRegex(self):
        self.runRegexTest(regex=regextypes.containsIntegerRegex, 
                          intAssertChooser=lambda p,c,s: self.assertIsNotNone,
                          floatAssertChooser=lambda p,c,s: self.assertIsNotNone,
                          expAssertChooser=lambda p,c,s: self.assertIsNotNone,
                          boolAssertChooser=lambda p,c,s,t: self.assertIsNone)
                    
    def testIntegerRegex(self):
        whiteSpaceSensAssert = lambda p,c,s: (self.assertIsNotNone if prefixSuffixWhitespace(p,s) 
                                              else self.assertIsNone)
        def convertType(prefix, suffix):
            for checkstr in self.integerStrs:
                if prefixSuffixWhitespace(prefix, suffix):
                    # This should not raise an exception
                    int(checkstr)
        self.runRegexTest(regex=regextypes.integerRegex, 
                          intAssertChooser=whiteSpaceSensAssert,
                          floatAssertChooser=lambda p,c,s: self.assertIsNone,
                          expAssertChooser=lambda p,c,s: self.assertIsNone,
                          boolAssertChooser=lambda p,c,s,t: self.assertIsNone,
                          additionalTests=[convertType])
    
    '''
    Bool Tests
    '''
    def testContainsBoolRegex(self):
        self.runRegexTest(regex=regextypes.containsBoolRegex, 
                          intAssertChooser=lambda p,c,s: self.assertIsNone,
                          floatAssertChooser=lambda p,c,s: self.assertIsNone,
                          expAssertChooser=lambda p,c,s: self.assertIsNone,
                          boolAssertChooser=lambda p,c,s,t: self.assertIsNotNone)
                    
    def testContainsTrueRegex(self):
        self.runRegexTest(regex=regextypes.containsTrueRegex, 
                          intAssertChooser=lambda p,c,s: self.assertIsNone,
                          floatAssertChooser=lambda p,c,s: self.assertIsNone,
                          expAssertChooser=lambda p,c,s: self.assertIsNone,
                          boolAssertChooser=lambda p,c,s,t: self.assertIsNotNone if t else self.assertIsNone)
                    
    def testContainsFalseRegex(self):
        self.runRegexTest(regex=regextypes.containsFalseRegex, 
                          intAssertChooser=lambda p,c,s: self.assertIsNone,
                          floatAssertChooser=lambda p,c,s: self.assertIsNone,
                          expAssertChooser=lambda p,c,s: self.assertIsNone,
                          boolAssertChooser=lambda p,c,s,t: self.assertIsNone if t else self.assertIsNotNone)
    
    def testBoolRegex(self):
        whiteSpaceSensAssert = lambda p,c,s,t: (self.assertIsNotNone if prefixSuffixWhitespace(p,s) 
                                                else self.assertIsNone)
        self.runRegexTest(regex=regextypes.boolRegex, 
                          intAssertChooser=lambda p,c,s: self.assertIsNone,
                          floatAssertChooser=lambda p,c,s: self.assertIsNone,
                          expAssertChooser=lambda p,c,s: self.assertIsNone,
                          boolAssertChooser=whiteSpaceSensAssert)
        
    def testTrueRegex(self):
        whiteSpaceSensAssert = lambda p,c,s,t: (self.assertIsNotNone if 
                                                t and prefixSuffixWhitespace(p,s) 
                                                else self.assertIsNone)
        self.runRegexTest(regex=regextypes.trueBoolRegex, 
                          intAssertChooser=lambda p,c,s: self.assertIsNone,
                          floatAssertChooser=lambda p,c,s: self.assertIsNone,
                          expAssertChooser=lambda p,c,s: self.assertIsNone,
                          boolAssertChooser=whiteSpaceSensAssert)
        
    def testFalseRegex(self):
        whiteSpaceSensAssert = lambda p,c,s,t: (self.assertIsNotNone if 
                                                not t and prefixSuffixWhitespace(p,s) 
                                                else self.assertIsNone)
        self.runRegexTest(regex=regextypes.falseBoolRegex, 
                          intAssertChooser=lambda p,c,s: self.assertIsNone,
                          floatAssertChooser=lambda p,c,s: self.assertIsNone,
                          expAssertChooser=lambda p,c,s: self.assertIsNone,
                          boolAssertChooser=whiteSpaceSensAssert)

class RegexDataTest(unittest.TestCase):
    def setUp(self):
        self.falseChecks = ["", " \t \n ", "a", "a ", " a", " a ", 
                            ".", " . ", "e", " e ", "3.14", "0"]
        self.prefixes = ["", " ", "a", "abcd", "two words", " space sep "]
        self.suffixes = self.prefixes
    
    # Helper function for function naming
    def noneCheckStr(self, testFunc):
        if testFunc == self.assertIsNotNone:
            return "not None"
        elif testFunc == self.assertIsNone:
            return "None"
        else:
            raise ValueError("Invalid test function to convert")
    
    '''
    Ensure we can detect occurrence of monetary symbol
    '''
    def testContainsMonetarySymbol(self):
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                # Contains Monetary Symbol
                assertFunc = self.assertIsNone
                for checkstr in self.falseChecks + ["k", "3.24", "2MM"]:
                   assertFunc(re.search(regexdatatypes.containsMonetarySymbolRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone
                for checkstr in ["$", u"\u00A3", u"\u20AC", "31.45$"]:
                   assertFunc(re.search(regexdatatypes.containsMonetarySymbolRegex, 
                                                 prefix+checkstr+suffix), 
                                       "String '"+prefix+checkstr+suffix+"' should have returned "+
                                       self.noneCheckStr(assertFunc))
                   
                # Contains Dollar Symbol
                assertFunc = self.assertIsNone
                for checkstr in self.falseChecks + ["k", "3.24", "2MM", u"\u00A3", u"\u20AC"]:
                    assertFunc(re.search(regexdatatypes.containsDollarSymbolRegex, 
                                                 prefix+checkstr+suffix), 
                                         "String '"+prefix+checkstr+suffix+"' should have returned "+
                                         self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone
                for checkstr in ["$", "31.45$"]:
                   assertFunc(re.search(regexdatatypes.containsDollarSymbolRegex, 
                                                 prefix+checkstr+suffix), 
                                         "String '"+prefix+checkstr+suffix+"' should have returned "+
                                         self.noneCheckStr(assertFunc))
                
                # Contains Pound Symbol
                assertFunc = self.assertIsNone
                for checkstr in self.falseChecks + ["k", "3.24", "2MM", u"\u20AC", "$", "31.45$"]:
                    assertFunc(re.search(regexdatatypes.containsPoundSymbolRegex, 
                                                 prefix+checkstr+suffix), 
                                         "String '"+prefix+checkstr+suffix+"' should have returned "+
                                         self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone
                for checkstr in [u"\u00A3", u"end pound\u00A3"]:
                   assertFunc(re.search(regexdatatypes.containsPoundSymbolRegex, 
                                                 prefix+checkstr+suffix), 
                                         "String '"+prefix+checkstr+suffix+"' should have returned "+
                                         self.noneCheckStr(assertFunc))
                   
                # Contains Euro Symbol
                assertFunc = self.assertIsNone
                for checkstr in self.falseChecks + ["k", "3.24", "2MM", u"\u00A3", "$", "31.45$"]:
                    assertFunc(re.search(regexdatatypes.containsEuroSymbolRegex, 
                                                 prefix+checkstr+suffix), 
                                         "String '"+prefix+checkstr+suffix+"' should have returned "+
                                         self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone
                for checkstr in [u"\u20AC", u"end euro\u20AC"]:
                    assertFunc(re.search(regexdatatypes.containsEuroSymbolRegex, 
                                                 prefix+checkstr+suffix), 
                                          "String '"+prefix+checkstr+suffix+"' should have returned "+
                                          self.noneCheckStr(assertFunc))
    
    '''
    Ensure we can detect beginning of monetary symbol
    '''        
    def testBeginsMonetarySymbol(self):
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                # Begins with Monetary Symbol
                assertFunc = self.assertIsNone
                for checkstr in self.falseChecks + ["k", "3.24", "2MM", "31.45$"]:
                    assertFunc(re.search(regexdatatypes.beginsWithMonetarySymbol, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone if not prefix or prefix.isspace() else self.assertIsNone
                for checkstr in ["$", u"\u00A3", u"\u20AC"]:
                    assertFunc(re.search(regexdatatypes.beginsWithMonetarySymbol, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                
                # Begins with Dollar Symbol
                assertFunc = self.assertIsNone
                for checkstr in self.falseChecks + ["k", "3.24", "2MM", u"\u00A3", u"\u20AC", "31.45$"]:
                    assertFunc(re.search(regexdatatypes.beginsWithDollarSymbol, 
                                                 prefix+checkstr+suffix), 
                                         "String '"+prefix+checkstr+suffix+"' should have returned "+
                                         self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone if not prefix or prefix.isspace() else self.assertIsNone
                for checkstr in ["$"]:
                    assertFunc(re.search(regexdatatypes.beginsWithDollarSymbol, 
                                                 prefix+checkstr+suffix), 
                                         "String '"+prefix+checkstr+suffix+"' should have returned "+
                                         self.noneCheckStr(assertFunc))
                
                # Begins with Pound Symbol
                assertFunc = self.assertIsNone
                for checkstr in self.falseChecks + ["k", "3.24", "2MM", u"\u20AC", "$", "31.45$", u"end pound\u00A3"]:
                     assertFunc(re.search(regexdatatypes.beginsWithPoundSymbol, 
                                                 prefix+checkstr+suffix), 
                                          "String '"+prefix+checkstr+suffix+"' should have returned "+
                                          self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone if not prefix or prefix.isspace() else self.assertIsNone
                for checkstr in [u"\u00A3"]:
                    assertFunc(re.search(regexdatatypes.beginsWithPoundSymbol, 
                                                 prefix+checkstr+suffix), 
                                         "String '"+prefix+checkstr+suffix+"' should have returned "+
                                         self.noneCheckStr(assertFunc))
                   
                # Begins with Euro Symbol
                assertFunc = self.assertIsNone
                for checkstr in self.falseChecks + ["k", "3.24", "2MM", u"\u00A3", "$", "31.45$", u"end euro\u20AC"]:
                    assertFunc(re.search(regexdatatypes.beginsWithEuroSymbol, 
                                                 prefix+checkstr+suffix), 
                                         "String '"+prefix+checkstr+suffix+"' should have returned "+
                                         self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone if not prefix or prefix.isspace() else self.assertIsNone
                for checkstr in [u"\u20AC"]:
                    assertFunc(re.search(regexdatatypes.beginsWithEuroSymbol, 
                                                 prefix+checkstr+suffix), 
                                         "String '"+prefix+checkstr+suffix+"' should have returned "+
                                         self.noneCheckStr(assertFunc))
                   
    '''
    Ensure we can detect numeric endings with multiplier symbols
    '''
    def testEndScaling(self):
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                # Ends with Thousands Indicator
                assertFunc = self.assertIsNone
                
                for checkstr in self.falseChecks + ["k", ".k", "3.24", "2MM", "31.45$"]:
                    assertFunc(re.search(regexdatatypes.endsWithThousandsScalingRegex, 
                                                 prefix+checkstr+suffix), 
                                       "String '"+prefix+checkstr+suffix+"' should have returned "+
                                       self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone if not suffix or suffix.isspace() else self.assertIsNone
                for checkstr in ["3.14k", "1.k", "0k \t ", "2k \t\r"]:
                    assertFunc(re.search(regexdatatypes.endsWithThousandsScalingRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                
                # Ends with Millions Indicator
                assertFunc = self.assertIsNone
                for checkstr in self.falseChecks + ["M", "MM", "3.14mm", ".M", ".MM", "2.14k", "3.24", "31.45$"]:
                    assertFunc(re.search(regexdatatypes.endsWithMillionsScalingRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone if not suffix or suffix.isspace() else self.assertIsNone
                for checkstr in ["3.14M", "1.M", "0M \t ", "2M \t\r",
                             "3.14MM", "1.MM", "0MM \t ", "2MM \t\r"]:
                    assertFunc(re.search(regexdatatypes.endsWithMillionsScalingRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))

    '''
    Ensure we can detect wrapped data
    '''
    def testContainsWrappedRegex(self):
        bracketTests = ["[3.14]", "[]", "[0] \t "]
        parensTests = ["(3.14)", "()", "(0) \t "]
        curlyBracketTests = ["{3.14}", "{}", "{0} \t "]
        falseBrackets = self.falseChecks + ["[", "]", "(", ")", "{", "}" "3.24"]
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                # Wrapped by any of brackets, curly brackets, or parens
                assertFunc = self.assertIsNone
                for checkstr in falseBrackets:
                    assertFunc(re.search(regexdatatypes.containsControlWrappingRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone
                for checkstr in bracketTests + parensTests + curlyBracketTests:
                    assertFunc(re.search(regexdatatypes.containsControlWrappingRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                    
                # Wrapped by brackets
                assertFunc = self.assertIsNone
                for checkstr in falseBrackets + parensTests + curlyBracketTests:
                    assertFunc(re.search(regexdatatypes.containsBracketedRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone
                for checkstr in bracketTests:
                    assertFunc(re.search(regexdatatypes.containsBracketedRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                    
                # Wrapped by parens
                assertFunc = self.assertIsNone
                for checkstr in falseBrackets + bracketTests + curlyBracketTests:
                    assertFunc(re.search(regexdatatypes.containsParensRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone
                for checkstr in parensTests:
                    assertFunc(re.search(regexdatatypes.containsParensRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                    
                # Wrapped by curly brackets
                assertFunc = self.assertIsNone
                for checkstr in falseBrackets + bracketTests + parensTests:
                    assertFunc(re.search(regexdatatypes.containsCurlyBracketedRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone
                for checkstr in curlyBracketTests:
                    assertFunc(re.search(regexdatatypes.containsCurlyBracketedRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
    
    '''
    Ensure we can detect current depth wrapped data
    '''           
    def testWrappedRegex(self):
        bracketTests = ["[3.14]", "[]", "[0] \t "]
        parensTests = ["(3.14)", "()", "(0) \t "]
        curlyBracketTests = ["{3.14}", "{}", "{0} \t "]
        singleQuotesTests = ["'3.14'", "''", "'0' \t "]
        doubleQuotesTests = ['"3.14"', '""', '"0" \t ']
        falseBrackets = self.falseChecks + ["[", "]", "(", ")", "{", "}" , "'", '"', 
                                            "[ )", "( ]", "{ ]", "[ }", "'\"", "\"'",
                                            "3.24"]
        for prefix in self.prefixes:
            for suffix in self.suffixes:
                # Wrapped by brackets
                assertFunc = self.assertIsNone
                for checkstr in (falseBrackets + parensTests + curlyBracketTests + 
                                 singleQuotesTests + doubleQuotesTests):
                    assertFunc(re.search(regexdatatypes.bracketedRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone if prefixSuffixWhitespace(prefix, suffix) else self.assertIsNone
                for checkstr in bracketTests:
                    assertFunc(re.search(regexdatatypes.bracketedRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                    
                # Wrapped by parens
                assertFunc = self.assertIsNone
                for checkstr in (falseBrackets + bracketTests + curlyBracketTests +
                                 singleQuotesTests + doubleQuotesTests):
                    assertFunc(re.search(regexdatatypes.parensRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone if prefixSuffixWhitespace(prefix, suffix) else self.assertIsNone
                for checkstr in parensTests:
                    assertFunc(re.search(regexdatatypes.parensRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                    
                # Wrapped by curly brackets
                assertFunc = self.assertIsNone
                for checkstr in (falseBrackets + bracketTests + parensTests +
                                 singleQuotesTests + doubleQuotesTests):
                    assertFunc(re.search(regexdatatypes.curlyBracketedRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone if prefixSuffixWhitespace(prefix, suffix) else self.assertIsNone
                for checkstr in curlyBracketTests:
                    assertFunc(re.search(regexdatatypes.curlyBracketedRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                    
                # Wrapped by single quotes
                assertFunc = self.assertIsNone
                for checkstr in (falseBrackets + bracketTests + parensTests +
                                 curlyBracketTests + doubleQuotesTests):
                    assertFunc(re.search(regexdatatypes.singleQuotesRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone if prefixSuffixWhitespace(prefix, suffix) else self.assertIsNone
                for checkstr in singleQuotesTests:
                    assertFunc(re.search(regexdatatypes.singleQuotesRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                    
                # Wrapped by double quotes
                assertFunc = self.assertIsNone
                for checkstr in (falseBrackets + bracketTests + parensTests +
                                 curlyBracketTests + singleQuotesTests):
                    assertFunc(re.search(regexdatatypes.doubleQuotesRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone if prefixSuffixWhitespace(prefix, suffix) else self.assertIsNone
                for checkstr in doubleQuotesTests:
                    assertFunc(re.search(regexdatatypes.doubleQuotesRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                    
                # Wrapped by any of brackets, curly brackets, parens, or quotes
                assertFunc = self.assertIsNone
                for checkstr in falseBrackets:
                    assertFunc(re.search(regexdatatypes.controlWrappedRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))
                   
                assertFunc = self.assertIsNotNone if prefixSuffixWhitespace(prefix, suffix) else self.assertIsNone
                for checkstr in (bracketTests + parensTests + curlyBracketTests + 
                                 singleQuotesTests + doubleQuotesTests):
                    assertFunc(re.search(regexdatatypes.controlWrappedRegex, 
                                                 prefix+checkstr+suffix), 
                                        "String '"+prefix+checkstr+suffix+"' should have returned "+
                                        self.noneCheckStr(assertFunc))

if __name__ == "__main__":
    unittest.main()
    