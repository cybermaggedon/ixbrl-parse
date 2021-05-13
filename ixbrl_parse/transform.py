
# 
# Implements some iXBRL transformations.  Internal, not expected to be called
# by the API user.
#

from lxml import etree as ET
import datetime
import number_parser
import re
import sys

FORMAT_boolballotbox = ET.QName(
    "http://www.sec.gov/inlineXBRL/transformation/2015-08-31",
    "boolballotbox"
)

FORMAT_datemonthdayyearen = ET.QName(
    "http://www.xbrl.org/inlineXBRL/transformation/2015-02-26",
    "datemonthdayyearen"
)

FORMAT_datemonthdayen = ET.QName(
    "http://www.xbrl.org/inlineXBRL/transformation/2015-02-26",
    "datemonthdayen"
)

FORMAT_datedaymonthyearen = ET.QName(
    "http://www.xbrl.org/inlineXBRL/transformation/2015-02-26",
    "datedaymonthyearen"
)

FORMAT_stateprovnameen = ET.QName(
    "http://www.sec.gov/inlineXBRL/transformation/2015-08-31",
    "stateprovnameen"
)

FORMAT_exchnameen = ET.QName(
    "http://www.sec.gov/inlineXBRL/transformation/2015-08-31",
    "exchnameen"
)

FORMAT_entityfilercategoryen = ET.QName(
    "http://www.sec.gov/inlineXBRL/transformation/2015-08-31",
    "entityfilercategoryen"
)

FORMAT_duryear = ET.QName(
    "http://www.sec.gov/inlineXBRL/transformation/2015-08-31",
    "duryear"
)

FORMAT_durwordsen = ET.QName(
    "http://www.sec.gov/inlineXBRL/transformation/2015-08-31",
    "durwordsen"
)

FORMAT_durmonth = ET.QName(
    "http://www.sec.gov/inlineXBRL/transformation/2015-08-31",
    "durmonth"
)

FORMAT_durday = ET.QName(
    "http://www.sec.gov/inlineXBRL/transformation/2015-08-31",
    "durday"
)

FORMAT_datemonthday = ET.QName(
    "http://www.xbrl.org/inlineXBRL/transformation/2015-02-26",
    "datemonthday"
)

FORMAT_datedaymonthyear = ET.QName(
    "http://www.xbrl.org/inlineXBRL/transformation/2015-02-26",
    "datedaymonthyear"
)

FORMAT_booleanfalse = ET.QName(
    "http://www.xbrl.org/inlineXBRL/transformation/2015-02-26",
    "booleanfalse"
)

FORMAT_booleantrue = ET.QName(
    "http://www.xbrl.org/inlineXBRL/transformation/2015-02-26",
    "booleantrue"
)

FORMAT_nocontent = ET.QName(
    "http://www.xbrl.org/inlineXBRL/transformation/2015-02-26",
    "nocontent"
)

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

#    sys.stderr.write(">>>>>>>" + pre.format.localname + "\n")

    if pre.format == FORMAT_boolballotbox:
        value = value.strip()
        if value == "☐":
            value = False
        elif value == "☑":
            value = True
        elif value == "☒":
            value = False
        else:
            raise RuntimeError(
                "Can't parse boolballotbox value %s" % value
            )
    elif pre.format == FORMAT_datemonthdayyearen:
        value = value.strip()
        try:
            value = datetime.datetime.strptime(value, "%B %d, %Y").date()
        except:
            value = datetime.datetime.strptime(value, "%B %d , %Y").date()
    elif pre.format == FORMAT_datemonthdayen:
        value = value.strip()
        value = datetime.datetime.strptime(value, "%B %d").date()
    elif pre.format == FORMAT_stateprovnameen:
        value = value.strip()
        if value in states:
            value = states[value]
        else:
            raise RuntimeError("Don't know state %s" % value)
    elif pre.format == FORMAT_exchnameen:
        # Leave it alone
        value = value.strip()
    elif pre.format == FORMAT_entityfilercategoryen:
        # Leave it alone
        value = value.strip()
    elif pre.format == FORMAT_duryear:
        value = value.strip()
        value = float(value)
        # FIXME: Er... precision, year is imprecise
        value = datetime.timedelta(days=value * 356)
    elif pre.format == FORMAT_durwordsen:
        value = value.strip()
        v = value
        value = parse_durwordsen(value)
    elif pre.format == FORMAT_durmonth:
        value = value.strip()
        value = int(value)
        # FIXME: Er... precision, month is imprecise
        value = datetime.timedelta(days=value * 30)
    elif pre.format == FORMAT_durday:
        value = value.strip()
        value = int(value)
        value = datetime.timedelta(days=value)
    elif pre.format == FORMAT_datemonthday:
        value = value.strip()
        elts = re.split(r'[ ,.:;/-]+', value)
        # FIXME: A string, like the ixbrl2 spec says.  Can't be represented
        # in a Python type
        value = "--" + str(int(elts[0])) + "-" + str(int(elts[1]))
    # FIXME: Some test data has earlier namespace.
    elif pre.format.localname == "datedaymonthyear":
        value = value.strip()
        elts = re.split(r'[^0-9]+', value)
        value = datetime.date(int(elts[2]), int(elts[1]), int(elts[0]))
    elif pre.format.localname == "datedaymonthyearen":
        value = value.strip()
        value = re.sub("([0-9]+)st", "\\1", value)
        value = re.sub("([0-9]+)nd", "\\1", value)
        value = re.sub("([0-9]+)rd", "\\1", value)
        value = re.sub("([0-9]+)th", "\\1", value)
        value = datetime.datetime.strptime(value, "%d %B %Y").date()
    elif pre.format.localname == "booleanfalse":
        value = False
    elif pre.format.localname == "booleantrue":
        value = True
    elif pre.format.localname == "nocontent":
        value = ""
    elif pre.format.localname == "numdotdecimal":
        value = value.replace(",", "")
        if value == "-": value = "0"

        # Must be non-negative
        value = abs(float(value))
        value = str(value)
    elif pre.format.localname == "numcommadot":
        value = value.replace(",", "")
        if value == "-": value = "0"

        # Must be non-negative
        value = abs(float(value))
        value = str(value)
    elif pre.format.localname == "numdash":
        value = "0"
    elif pre.format.localname == "zerodash":
        value = "0"
    elif pre.format.localname == "datelonguk":
        value = value.strip()
        value = re.sub("([0-9]+)st", "\\1", value)
        value = re.sub("([0-9]+)nd", "\\1", value)
        value = re.sub("([0-9]+)rd", "\\1", value)
        value = re.sub("([0-9]+)th", "\\1", value)
        value = datetime.datetime.strptime(value, "%d %B %Y").date()
    elif pre.format.localname == "numwordsen":
        value = value.strip()
        value = number_parser.parse(value)
    else:
        raise RuntimeError(
            "Don't know format %s on value %s" % (pre.format, value)
        )

    return value
