
# 
# Implements some iXBRL transformations.  Internal, not expected to be called
# by the API user.
#

from lxml import etree as ET
import datetime
import number_parser
import re
import sys
from . value import *


states = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota":" ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY"
}

def parse_durwordsen(val):

    delta = datetime.timedelta()
    num = None

    val = number_parser.parse(val)

    val = val.replace("\xa0", " ")

    res = re.split(r'[ ,.:;-]+', val)

    for v in res:

        if num == None:
            if v in {"and", "plus", "with", "then"}: continue
            try:
                num = int(v)
            except:
                raise RuntimeError("Not a number: %s" % v)
        else:
            if v == "year" or v == "years":
                delta += datetime.timedelta(days=(num * 356))
            elif v == "month" or v == "months":
                delta += datetime.timedelta(days=(num * 30))
            elif v == "day" or v == "days":
                delta += datetime.timedelta(days=num)
            elif v == "hour" or v == "hours":
                delta += datetime.timedelta(hours=num)
            elif v == "minute" or v == "minutes":
                delta += datetime.timedelta(minutes=num)
            elif v == "second" or v == "seconds":
                delta += datetime.timedelta(seconds=num)
            else:
                raise RuntimeError("Stalled on token %s" % v)
            num = None

    return delta


def transform(pre, value):
    if pre.format in registry:
        return registry[pre.format](pre, value)
    else:
        # FIXME: Downgrade to just returning the string.
        raise RuntimeError(
            "Don't know format %s on value %s" % (pre.format, value)
        )
    return value

def boolballotbox(pre, value):
    value = value.strip()
    if value == "☐":
        return Boolean(False)
    elif value == "☑":
        return Boolean(True)
    elif value == "☒":
        return Boolean(False)
    else:
        raise RuntimeError(
            "Can't parse boolballotbox value %s" % value
        )
    
def datemonthdayyearen(pre, value):
    value = value.strip()
    try:
        value = datetime.datetime.strptime(value, "%B %d, %Y").date()
        return Date(value)
    except:
        value = datetime.datetime.strptime(value, "%B %d , %Y").date()
        return Date(value)

def datemonthdayen(pre, value):
    value = value.strip()
    value = datetime.datetime.strptime(value, "%B %d").date()
    return Date(value)

def stateprovnameen(pre, value):
    value = value.strip()
    if value in states:
        return String(states[value])
    else:
        raise RuntimeError("Don't know state %s" % value)

def exchnameen(pre, value):
    # Leave it alone
    value = value.strip()
    return String(value)

def entityfilercategoryen(pre, value):
    # Leave it alone
    value = value.strip()
    return String(value)

def duryear(pre, value):
    value = value.strip()
    value = float(value)

    # Year is imprecise
    value = datetime.timedelta(days=value * 356)

    # This rounds off the seconds
    value = datetime.timedelta(days = value.days)
    
    return Duration(value)

def durwordsen(pre, value):
    value = value.strip()
    v = value
    value = parse_durwordsen(value)
    return Duration(value)

def durmonth(pre, value):
    value = value.strip()
    value = int(value)

    # Month is imprecise
    value = datetime.timedelta(days=value * 30)

    # This rounds off the seconds
    value = datetime.timedelta(days = value.days)

    return Duration(value)

def durday(pre, value):
    value = value.strip()
    value = int(value)
    value = datetime.timedelta(days=value)
    return Duration(value)

def datemonthday(pre, value):
    value = value.strip()
    elts = re.split(r'[ ,.:;/-]+', value)
    # FIXME: A string, like the ixbrl2 spec says.  Can't be represented
    # in a Python type
    value = "--" + str(int(elts[0])) + "-" + str(int(elts[1]))
    return MonthDay(int(elts[0]), int(elts[1]))

def datedaymonthyear(pre, value):
    value = value.strip()
    elts = re.split(r'[^0-9]+', value)
    value = datetime.date(int(elts[2]), int(elts[1]), int(elts[0]))
    return Date(value)

def datedaymonthyearen(pre, value):
    value = value.strip()
    value = re.sub("([0-9]+)st", "\\1", value)
    value = re.sub("([0-9]+)nd", "\\1", value)
    value = re.sub("([0-9]+)rd", "\\1", value)
    value = re.sub("([0-9]+)th", "\\1", value)
    value = datetime.datetime.strptime(value, "%d %B %Y").date()
    return Date(value)

def booleanfalse(pre, value):
    return Boolean(False)

def booleantrue(pre, value):
    return Boolean(True)

def nocontent(pre, value):
    return String("")

def numdotdecimal(pre, value):
    value = value.replace(",", "")
    if value == "-": value = "0"

    # Must be non-negative
    value = abs(float(value))
    f = Float(value * pre.scale)
    if pre.unit: f.unit = pre.unit
    return f

def numcommadot(pre, value):
    value = value.replace(",", "")
    if value == "-": value = 0

    # Must be non-negative
    value = abs(float(value))

    f = Float(value * pre.scale)
    if pre.unit: f.unit = pre.unit
    return f

def numdash(pre, value):
    f = Float(0)
    if pre.unit: f.unit = pre.unit
    return f

def zerodash(pre, value):
    f = Float(0)
    if pre.unit: f.unit = pre.unit
    return f

def datelonguk(pre, value):
    value = value.strip()
    value = re.sub("([0-9]+)st", "\\1", value)
    value = re.sub("([0-9]+)nd", "\\1", value)
    value = re.sub("([0-9]+)rd", "\\1", value)
    value = re.sub("([0-9]+)th", "\\1", value)
    value = datetime.datetime.strptime(value, "%d %B %Y").date()
    return Date(value)

def numwordsen(pre, value):
    value = value.strip()
    if value in { "nil", "None", "none", "", "no", "No" }:
        value = 0
    else:
        value = number_parser.parse(value)
    f = Float(float(value) * pre.scale)
    if pre.unit: f.unit = pre.unit
    return f


SEC_XFORM = "http://www.sec.gov/inlineXBRL/transformation/2015-08-31"
XBRL_XFORM = "http://www.xbrl.org/inlineXBRL/transformation/2015-02-26"
XBRL_XFORM_0 = "http://www.xbrl.org/inlineXBRL/transformation/2011-07-31"
XBRL_XFORM_1 = "http://www.xbrl.org/inlineXBRL/transformation/2010-04-20"
registry = {}

registry[ET.QName(SEC_XFORM, "boolballotbox")] = boolballotbox
registry[ET.QName(XBRL_XFORM, "datemonthdayyearen")] = datemonthdayyearen
registry[ET.QName(XBRL_XFORM, "datemonthdayen")] = datemonthdayen
registry[ET.QName(XBRL_XFORM, "datedaymonthyearen")] = datedaymonthyearen
registry[ET.QName(XBRL_XFORM_0, "datedaymonthyearen")] = datedaymonthyearen
registry[ET.QName(SEC_XFORM, "stateprovnameen")] = stateprovnameen
registry[ET.QName(SEC_XFORM, "exchnameen")] = exchnameen
registry[ET.QName(SEC_XFORM, "entityfilercategoryen")] = entityfilercategoryen
registry[ET.QName(SEC_XFORM, "duryear")] = duryear
registry[ET.QName(SEC_XFORM, "durwordsen")] = durwordsen
registry[ET.QName(SEC_XFORM, "durmonth")] = durmonth
registry[ET.QName(SEC_XFORM, "durday")] = durday
registry[ET.QName(XBRL_XFORM, "datemonthday")] = datemonthday
registry[ET.QName(XBRL_XFORM, "datedaymonthyear")] = datedaymonthyear
registry[ET.QName(XBRL_XFORM_0, "datedaymonthyear")] = datedaymonthyear
registry[ET.QName(XBRL_XFORM, "booleanfalse")] = booleanfalse
registry[ET.QName(XBRL_XFORM, "booleantrue")] = booleantrue
registry[ET.QName(XBRL_XFORM_0, "booleanfalse")] = booleanfalse
registry[ET.QName(XBRL_XFORM_0, "booleantrue")] = booleantrue
registry[ET.QName(XBRL_XFORM, "nocontent")] = nocontent
registry[ET.QName(XBRL_XFORM_0, "nocontent")] = nocontent
registry[ET.QName(XBRL_XFORM, "numdotdecimal")] = numdotdecimal
registry[ET.QName(XBRL_XFORM_0, "numdotdecimal")] = numdotdecimal
registry[ET.QName(XBRL_XFORM, "zerodash")] = zerodash
registry[ET.QName(XBRL_XFORM_0, "zerodash")] = zerodash
registry[ET.QName(SEC_XFORM, "numwordsen")] = numwordsen
registry[ET.QName(XBRL_XFORM, "numcommadot")] = numcommadot
registry[ET.QName(XBRL_XFORM_0, "numcommadot")] = numcommadot
registry[ET.QName(XBRL_XFORM_1, "numcommadot")] = numcommadot
registry[ET.QName(XBRL_XFORM_0, "datelonguk")] = datelonguk
registry[ET.QName(XBRL_XFORM_1, "datelonguk")] = datelonguk
registry[ET.QName(XBRL_XFORM_0, "numdash")] = numdash
registry[ET.QName(XBRL_XFORM_1, "numdash")] = numdash

