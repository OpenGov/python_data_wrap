import re

'''
Defines regex strings which block prefixing or postfixing

Must be prefixed/trailed by whitespace/nothing
'''
_notPrefixedImpl = r"(?=^)(\s*)"
_notFollowedImpl = r"(\s*)(?=$)"

'''
This matches any integer based number with a possible '+-'
prepended.

It does not match any floating point numbers
'''
_containsIntegerImpl = r"([-+]?([0-9]+))"

containsIntegerRegex = re.compile(_containsIntegerImpl)

'''
Like containsInteger but also doesn't allow for 
trailing or following characters other than whitespace
'''
_integerImpl = (
    r"("+_notPrefixedImpl+
    _containsIntegerImpl+
    _notFollowedImpl+r")")

integerRegex = re.compile(_integerImpl)

'''
This matches any floating or integer based number with
a possible '+-' prepending _numericalImpl values with one or zero 
'.' characters.

This does not handle exponential cases indicated by 'e'.
'''
_containsNumericalNonExpImpl = (
    # Can start with or without a '-+'
    r"([-+]?"
    # Can be either a number-'.'-(possible:number)
    r"(([0-9]+(\.[0-9]*))|"
    # Or a (possible:number-'.')-number
    r"(([0-9]*\.)?[0-9]+)))")

# Faster than containsNumericalRegex
containsNumericalNonExpRegex = re.compile(_containsNumericalNonExpImpl)

'''
Like containsNumericalNonExpRegex but also doesn't allow for 
trailing or following characters other than whitespace
'''
_numericalNonExpImpl = (
    r"("+_notPrefixedImpl+
    _containsNumericalNonExpImpl+
    _notFollowedImpl+r")")

numericalNonExpRegex = re.compile(_numericalNonExpImpl)

'''
Like containsNumericalNonExp but also catches exponentials
marked by 'e'.
'''
_containsNumericalImpl = (
    r"("+_containsNumericalNonExpImpl+
    # Can contain an 'e'
    r"([eE]"+
        # 'e' must be followed by an integer
        _containsIntegerImpl+
    r")?)")

containsNumericalRegex = re.compile(_containsNumericalImpl)

'''
Like containsNumericalImpl but also doesn't allow for 
trailing or following characters other than whitespace
'''
_numericalImpl = (
    r"("+_notPrefixedImpl+
    _containsNumericalImpl+
    _notFollowedImpl+r")")

numericalRegex = re.compile(_numericalImpl)
    
'''
This matches any floating based number with a possible '+-' 
prepending numericalImpl values with one '.' character.

Integers without a '.' character are not matched.

This does not handle exponential cases indicated by 'e'.
'''
_containsFloatingNonExpImpl = (
    # Can start with or without a '-+'
    r"([-+]?"
    # Can be either a number-'.'-(possible:number)
    r"(([0-9]+(\.[0-9]*))|"
    # Or a (possible:number)-'.'-number
    r"(([0-9]*)(\.[0-9]+))))")

# Faster than containsFloatingRegex
containsFloatingNonExpRegex = re.compile(_containsFloatingNonExpImpl)

'''
Like containsNonExpFloating but also doesn't allow for 
trailing or following characters other than whitespace
'''
_floatingNonExpImpl = (
    r"("+_notPrefixedImpl+
    _containsFloatingNonExpImpl+
    _notFollowedImpl+r")")

floatingNonExpRegex = re.compile(_floatingNonExpImpl)
    
'''
Like containsNonExpFloating but also catches exponentials
marked by 'e'.
'''
_containsFloatingImpl = (
    # Can be an exponential numerical
    r"(("+_containsNumericalNonExpImpl+
    # Must contain an 'e'
    r"([eE]"+
        # 'e' must be followed by an integer
        _containsIntegerImpl+
     # Or must be non-exp floating value
    r"))|"+_containsFloatingNonExpImpl+r")")

containsFloatingRegex = re.compile(_containsFloatingImpl)
    
'''
Like containsFloating but also doesn't allow for 
trailing or following characters other than whitespace
'''
_floatingImpl = (
    r"("+_notPrefixedImpl+
    _containsFloatingImpl+
    _notFollowedImpl+r")")

floatingRegex = re.compile(_floatingImpl)

'''
This matches any string based boolean indicator.
'''
# Inefficient detector, but doesn't need any flags
_containsTrueImpl = r"([tT][rR][uU][eE])"
_containsFalseImpl = r"([fF][aA][lL][sS][eE])"
_containsBoolImpl = r"("+_containsTrueImpl+r"|"+_containsFalseImpl+r")"

containsBoolRegex = re.compile(_containsBoolImpl)
containsTrueRegex = re.compile(_containsTrueImpl)
containsFalseRegex = re.compile(_containsFalseImpl)

'''
Like containsBool but also doesn't allow for 
trailing or following characters other than whitespace
'''
_trueImpl = (
    r"("+_notPrefixedImpl+
    _containsTrueImpl+
    _notFollowedImpl+r")")
_falseImpl = (
    r"("+_notPrefixedImpl+
    _containsFalseImpl+
    _notFollowedImpl+r")")
_boolImpl = (
    r"("+_notPrefixedImpl+
    _containsBoolImpl+
    _notFollowedImpl+r")")

boolRegex = re.compile(_boolImpl)
trueBoolRegex = re.compile(_trueImpl)
falseBoolRegex = re.compile(_falseImpl)
