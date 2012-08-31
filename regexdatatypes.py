import re
from regextypes import _notPrefixedImpl, _notFollowedImpl

'''
The following are common string cases used in transparency
data extraction.

These checks find the pressense of monetary value indicators,
$, pound sign, euro sign.
'''
_dollarAmountImpl = r"\$"
_poundAmountImpl = ur"\u00A3"
_euroAmoundImpl = ur"\u20AC"
_containsMonetarySymbolImpl = (
    r"(["+_dollarAmountImpl+
    _poundAmountImpl+
    _euroAmoundImpl+r"])")

containsMonetarySymbolRegex = re.compile(_containsMonetarySymbolImpl)
containsDollarSymbolRegex = re.compile(_dollarAmountImpl)
containsPoundSymbolRegex = re.compile(_poundAmountImpl)
containsEuroSymbolRegex = re.compile(_euroAmoundImpl)

'''
Like containsMonetarySymbol but requires that the string be
preceded by whitespace or nothing.
'''
_beginsWithMonetarySymbolImpl = (
    r"("+_notPrefixedImpl+
    _containsMonetarySymbolImpl+r")")
_beginsWithDollarSymbolImpl = (
    r"("+_notPrefixedImpl+
    _dollarAmountImpl+r")")
_beginsWithPoundSymbolImpl = (
    r"("+_notPrefixedImpl+
    _poundAmountImpl+r")")
_beginsWithEuroSymbolImpl = (
    r"("+_notPrefixedImpl+
    _euroAmoundImpl+r")")

beginsWithMonetarySymbol = re.compile(_beginsWithMonetarySymbolImpl)
beginsWithDollarSymbol = re.compile(_beginsWithDollarSymbolImpl)
beginsWithPoundSymbol = re.compile(_beginsWithPoundSymbolImpl)
beginsWithEuroSymbol = re.compile(_beginsWithEuroSymbolImpl)

'''
Indicators for being scaled by a thousand or million. These
only match if following a numeric value.
'''
_prefacedByNumericImpl = r"(([0-9]\.?)\s*)"
_endsWithThousandsScalingImpl = r"("+_prefacedByNumericImpl+"k"+_notFollowedImpl+r")"
endsWithThousandsScalingRegex = re.compile(_endsWithThousandsScalingImpl)

_endsWithMillionsScalingImpl = r"("+_prefacedByNumericImpl+r"M{1,2}"+_notFollowedImpl+r")"
endsWithMillionsScalingRegex = re.compile(_endsWithMillionsScalingImpl)

'''
Regex for capturing wrapped information. Brackets, parens,
and curly brackets can all be detected.
'''
# White space or non-whitespace repeated => match everything
_anythingImpl = r"[\s\S]*"
# Bracket type
_containsBracketedImpl = r"(\["+_anythingImpl+"\])"
_bracketedImpl = (
    r"("+_notPrefixedImpl+
    _containsBracketedImpl+
    _notFollowedImpl+r")")

containsBracketedRegex = re.compile(_containsBracketedImpl)
bracketedRegex = re.compile(_bracketedImpl)

# Curly Bracket type
_containsCurlyBracketedImpl = r"({"+_anythingImpl+"})"
_curlyBracketedImpl = (
    r"("+_notPrefixedImpl+
    _containsCurlyBracketedImpl+
    _notFollowedImpl+r")")

curlyBracketedRegex = re.compile(_curlyBracketedImpl)
containsCurlyBracketedRegex = re.compile(_containsCurlyBracketedImpl)

# Parens type
_containsParensImpl = r"(\("+_anythingImpl+"\))"
_parensImpl = (
    r"("+_notPrefixedImpl+
    _containsParensImpl+
    _notFollowedImpl+r")")

containsParensRegex = re.compile(_containsParensImpl)
parensRegex = re.compile(_parensImpl)

# Single quotes type
_containsSingleQuotesImpl = r"('"+_anythingImpl+"')"
_singleQuotesImpl = (
    r"("+_notPrefixedImpl+
    _containsSingleQuotesImpl+
    _notFollowedImpl+r")")

containsSingleQuotesRegex = re.compile(_containsSingleQuotesImpl)
singleQuotesRegex = re.compile(_singleQuotesImpl)

# Double quotes type
_containsDoubleQuotesImpl = r'("'+_anythingImpl+'")'
_doubleQuotesImpl = (
    r"("+_notPrefixedImpl+
    _containsDoubleQuotesImpl+
    _notFollowedImpl+r")")

containsDoubleQuotesRegex = re.compile(_containsDoubleQuotesImpl)
doubleQuotesRegex = re.compile(_doubleQuotesImpl)

# Any of the above types
_containsControlWrappingImpl = (
    r"("+_containsBracketedImpl+
    r"|"+_containsCurlyBracketedImpl+
    r"|"+_containsParensImpl+
    r"|"+_containsSingleQuotesImpl+
    r"|"+_containsDoubleQuotesImpl+r")")
_controlWrappedImpl = (
    r"("+_notPrefixedImpl+
    _containsControlWrappingImpl+
    _notFollowedImpl+r")")

containsControlWrappingRegex = re.compile(_containsControlWrappingImpl)
controlWrappedRegex = re.compile(_controlWrappedImpl)
