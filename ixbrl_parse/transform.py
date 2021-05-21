
# 
# Implements some iXBRL transformations.  Internal, not expected to be called
# by the API user.
#

# For SEC transforms, see:
#   https://www.sec.gov/edgar/searchedgar/edgarstatecodes.htm
#   https://www.sec.gov/info/edgar/specifications/edgarfm-vol2-v51_d.pdf


from lxml import etree as ET
import datetime
import number_parser
import re
import sys
from . value import *


states = {
    "ALABAMA": "AL",
    "ALASKA": "AK",
    "ARIZONA": "AZ",
    "ARKANSAS": "AR",
    "CALIFORNIA": "CA",
    "COLORADO": "CO",
    "CONNECTICUT": "CT",
    "DELAWARE": "DE",
    "DISTRICT OF COLUMBIA": "DC",
    "FLORIDA": "FL",
    "GEORGIA": "GA",
    "HAWAII": "HI",
    "IDAHO": "ID",
    "ILLINOIS": "IL",
    "INDIANA": "IN",
    "IOWA": "IA",
    "KANSAS": "KS",
    "KENTUCKY": "KY",
    "LOUISIANA": "LA",
    "MAINE": "ME",
    "MONTANA": "MT",
    "NEBRASKA": "NE",
    "NEVADA": "NV",
    "NEW HAMPSHIRE": "NH",
    "NEW JERSEY": "NJ",
    "NEW MEXICO": "NM",
    "NEW YORK": "NY",
    "NORTH CAROLINA": "NC",
    "NORTH DAKOTA":" ND",
    "OHIO": "OH",
    "OKLAHOMA": "OK",
    "OREGON": "OR",
    "MARYLAND": "MD",
    "MASSACHUSETTS": "MA",
    "MICHIGAN": "MI",
    "MINNESOTA": "MN",
    "MISSISSIPPI": "MS",
    "MISSOURI": "MO",
    "PENNSYLVANIA": "PA",
    # FIXME: Doesn't belong here?
    # https://www.sec.gov/edgar/searchedgar/edgarstatecodes.htm
    "PUERTO RICO": "PR",
    "RHODE ISLAND": "RI",
    "SOUTH CAROLINA": "SC",
    "SOUTH DAKOTA": "SD",
    "TENNESSEE": "TN",
    "TEXAS": "TX",
    "UTAH": "UT",
    "VERMONT": "VT",
    "VIRGINIA": "VA",
    "WASHINGTON": "WA",
    "WEST VIRGINIA": "WV",
    "WISCONSIN": "WI",
    "WYOMING": "WY",
    # FIXME: Should not be here.
    "QUEBEC": "A8",
    "BRITISH COLUMBIA": "A1",
}

state_country = {
    "ALABAMA": "AL",
    "ALASKA": "AK",
    "ARIZONA": "AZ",
    "ARKANSAS": "AR",
    "CALIFORNIA": "CA",
    "COLORADO": "CO",
    "CONNECTICUT": "CT",
    "DELAWARE": "DE",
    "DISTRICT OF COLUMBIA": "DC",
    "FLORIDA": "FL",
    "GEORGIA": "GA",
    "HAWAII": "HI",
    "IDAHO": "ID",
    "ILLINOIS": "IL",
    "INDIANA": "IN",
    "IOWA": "IA",
    "KANSAS": "KS",
    "KENTUCKY": "KY",
    "LOUISIANA": "LA",
    "MAINE": "ME",
    "MARYLAND": "MD",
    "MASSACHUSETTS": "MA",
    "MICHIGAN": "MI",
    "MINNESOTA": "MN",
    "MISSISSIPPI": "MS",
    "MISSOURI": "MO",
    "MONTANA": "MT",
    "NEBRASKA": "NE",
    "NEVADA": "NV",
    "NEW HAMPSHIRE": "NH",
    "NEW JERSEY": "NJ",
    "NEW MEXICO": "NM",
    "NEW YORK": "NY",
    "NORTH CAROLINA": "NC",
    "NORTH DAKOTA": "ND",
    "OHIO": "OH",
    "OKLAHOMA": "OK",
    "OREGON": "OR",
    "PENNSYLVANIA": "PA",
    "RHODE ISLAND": "RI",
    "SOUTH CAROLINA": "SC",
    "SOUTH DAKOTA": "SD",
    "TENNESSEE": "TN",
    "TEXAS": "TX",
    "UNITED STATES": "X1",
    "UTAH": "UT",
    "VERMONT": "VT",
    "VIRGINIA": "VA",
    "WASHINGTON": "WA",
    "WEST VIRGINIA": "WV",
    "WISCONSIN": "WI",
    "WYOMING": "WY",
    "ALBERTA CANADA": "A0",
    "BRITISH COLUMBIA CANADA": "A1",
    "MANITOBA CANADA": "A2",
    "NEW BRUNSWICK CANADA": "A3",
    "NEWFOUNDLAND CANADA": "A4",
    "NOVA SCOTIA CANADA": "A5",
    "ONTARIO CANADA": "A6",
    "PRINCE EDWARD ISLAND CANADA": "A7",
    "QUEBEC CANADA": "A8",
    "QUEBEC": "A8",
    "SASKATCHEWAN CANADA": "A9",
    "YUKON CANADA": "B0",
    "CANADA": "Z4",
    "AFGHANISTAN": "B2",
    "ALAND ISLANDS": "Y6",
    "ALBANIA": "B3",
    "ALGERIA": "B4",
    "AMERICAN SAMOA": "B5",
    "ANDORRA": "B6",
    "ANGOLA": "B7",
    "ANGUILLA": "1A",
    "ANTARCTICA": "B8",
    "ANTIGUA AND BARBUDA": "B9",
    "ARGENTINA": "C1",
    "ARMENIA": "1B",
    "ARUBA": "1C",
    "AUSTRALIA": "C3",
    "AUSTRIA": "C4",
    "AZERBAIJAN": "1D",
    "BAHAMAS": "C5",
    "BAHRAIN": "C6",
    "BANGLADESH": "C7",
    "BARBADOS": "C8",
    "BELARUS": "1F",
    "BELGIUM": "C9",
    "BELIZE": "D1",
    "BENIN": "G6",
    "BERMUDA": "D0",
    "BHUTAN": "D2",
    "BOLIVIA": "D3",
    "BOSNIA AND HERZEGOVINA": "1E",
    "BOTSWANA": "B1",
    "BOUVET ISLAND": "D4",
    "BRAZIL": "D5",
    "BRITISH INDIAN OCEAN TERRITORY": "D6",
    "BRUNEI DARUSSALAM": "D9",
    "BULGARIA": "E0",
    "BURKINA FASO": "X2",
    "BURUNDI": "E2",
    "CAMBODIA": "E3",
    "CAMEROON": "E4",
    "CANADA": "Z4",
    "CAPE VERDE": "E8",
    "CAYMAN ISLANDS": "E9",
    "CENTRAL AFRICAN REPUBLIC": "F0",
    "CHAD": "F2",
    "CHILE": "F3",
    "CHINA": "F4",
    "CHRISTMAS ISLAND": "F6",
    "COCOS (KEELING) ISLANDS": "F7",
    "COLOMBIA": "F8",
    "COMOROS": "F9",
    "CONGO": "G0",
    "CONGO THE DEMOCRATIC REPUBLIC OF THE": "Y3",
    "COOK ISLANDS": "G1",
    "COSTA RICA": "G2",
    "COTE D'IVOIRE": "L7",
    "CROATIA": "1M",
    "CUBA": "G3",
    "CYPRUS": "G4",
    "CZECH REPUBLIC": "2N",
    "DENMARK": "G7",
    "DJIBOUTI": "1G",
    "DOMINICA": "G9",
    "DOMINICAN REPUBLIC": "G8",
    "ECUADOR": "H1",
    "EGYPT": "H2",
    "EL SALVADOR": "H3",
    "EQUATORIAL GUINEA": "H4",
    "ERITREA": "1J",
    "ESTONIA": "1H",
    "ETHIOPIA": "H5",
    "FALKLAND ISLANDS": "H7",
    "FAROE ISLANDS": "H6",
    "FIJI": "H8",
    "FINLAND": "H9",
    "FRANCE": "I0",
    "FRENCH GUIANA": "I3",
    "FRENCH POLYNESIA": "I4",
    "FRENCH SOUTHERN TERRITORIES": "2C",
    "GABON": "I5",
    "GAMBIA": "I6",
    "GEORGIA": "2Q",
    "GERMANY": "2M",
    "GHANA": "J0",
    "GIBRALTAR": "J1",
    "GREECE": "J3",
    "GREENLAND": "J4",
    "GRENADA": "J5",
    "GUADELOUPE": "J6",
    "GUAM": "GU",
    "GUATEMALA": "J8",
    "GUERNSEY": "Y7",
    "GUINEA": "J9",
    "GUINEA BISSAU": "S0",
    "GUYANA": "K0",
    "HAITI": "K1",
    "HEARD ISLAND AND MCDONALD ISLANDS": "K4",
    "HOLY SEE (VATICAN CITY STATE)": "X4",
    "HONDURAS": "K2",
    "HONG KONG": "K3",
    "HUNGARY": "K5",
    "ICELAND": "K6",
    "INDIA": "K7",
    "INDONESIA": "K8",
    "IRAN ISLAMIC REPUBLIC OF": "K9",
    "IRAQ": "L0",
    "IRELAND": "L2",
    "ISLE OF MAN": "Y8",
    "ISRAEL": "L3",
    "ITALY": "L6",
    "JAMAICA": "L8",
    "JAPAN": "M0",
    "JERSEY": "Y9",
    "JORDAN": "M2",
    "KAZAKSTAN": "1P",
    "KENYA": "M3",
    "KIRIBATI": "J2",
    "KOREA DEMOCRATIC PEOPLE'S REPUBLIC OF": "M4",
    "KOREA REPUBLIC OF": "M5",
    "KUWAIT": "M6",
    "KYRGYZSTAN": "1N",
    "LAO PEOPLE'S DEMOCRATIC REPUBLIC": "M7",
    "LATVIA": "1R",
    "LEBANON": "M8",
    "LESOTHO": "M9",
    "LIBERIA": "N0",
    "LIBYAN ARAB JAMAHIRIYA": "N1",
    "LIECHTENSTEIN": "N2",
    "LITHUANIA": "1Q",
    "LUXEMBOURG": "N4",
    "MACAU": "N5",
    "MACEDONIA THE FORMER YUGOSLAV REPUBLIC OF": "1U",
    "MADAGASCAR": "N6",
    "MALAWI": "N7",
    "MALAYSIA": "N8",
    "MALDIVES": "N9",
    "MALI": "O0",
    "MALTA": "O1",
    "MARSHALL ISLANDS": "1T",
    "MARTINIQUE": "O2",
    "MAURITANIA": "O3",
    "MAURITIUS": "O4",
    "MAYOTTE": "2P",
    "MEXICO": "O5",
    "MICRONESIA FEDERATED STATES OF": "1K",
    "MOLDOVA REPUBLIC OF": "1S",
    "MONACO": "O9",
    "MONGOLIA": "P0",
    "MONTENEGRO": "Z5",
    "MONTSERRAT": "P1",
    "MOROCCO": "P2",
    "MOZAMBIQUE": "P3",
    "MYANMAR": "E1",
    "NAMIBIA": "T6",
    "NAURU": "P5",
    "NEPAL": "P6",
    "NETHERLANDS": "P7",
    "NETHERLANDS ANTILLES": "P8",
    "NEW CALEDONIA": "1W",
    "NEW ZEALAND": "Q2",
    "NICARAGUA": "Q3",
    "NIGER": "Q4",
    "NIGERIA": "Q5",
    "NIUE": "Q6",
    "NORFOLK ISLAND": "Q7",
    "NORTHERN MARIANA ISLANDS": "1V",
    "NORWAY": "Q8",
    "OMAN": "P4",
    "PAKISTAN": "R0",
    "PALAU": "1Y",
    "PALESTINIAN TERRITORY OCCUPIED": "1X",
    "PALESTINIAN TERRITORY": "1X",
    "PANAMA": "R1",
    "PAPUA NEW GUINEA": "R2",
    "PARAGUAY": "R4",
    "PERU": "R5",
    "PHILIPPINES": "R6",
    "PITCAIRN": "R8",
    "POLAND": "R9",
    "PORTUGAL": "S1",
    "PUERTO RICO": "PR",
    "QATAR": "S3",
    "REUNION": "S4",
    "ROMANIA": "S5",
    "RUSSIAN FEDERATION": "1Z",
    "RWANDA": "S6",
    "SAINT BARTHELEMY": "Z0",
    "SAINT HELENA": "U8",
    "SAINT KITTS AND NEVIS": "U7",
    "SAINT LUCIA": "U9",
    "SAINT MARTIN": "Z1",
    "SAINT PIERRE AND MIQUELON": "V0",
    "SAINT VINCENT AND THE GRENADINES": "V1",
    "SAMOA": "Y0",
    "SAN MARINO": "S8",
    "SAO TOME AND PRINCIPE": "S9",
    "SAUDI ARABIA": "T0",
    "SENEGAL": "T1",
    "SERBIA": "Z2",
    "SEYCHELLES": "T2",
    "SIERRA LEONE": "T8",
    "SINGAPORE": "U0",
    "SLOVAKIA": "2B",
    "SLOVENIA": "2A",
    "SOLOMON ISLANDS": "D7",
    "SOMALIA": "U1",
    "SOUTH AFRICA": "T3",
    "SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS": "1L",
    "SPAIN": "U3",
    "SRI LANKA": "F1",
    "SUDAN": "V2",
    "SURINAME": "V3",
    "SVALBARD AND JAN MAYEN": "L9",
    "SWAZILAND": "V6",
    "SWEDEN": "V7",
    "SWITZERLAND": "V8",
    "SYRIAN ARAB REPUBLIC": "V9",
    "TAIWAN PROVINCE OF CHINA": "F5",
    "TAJIKISTAN": "2D",
    "TANZANIA UNITED REPUBLIC OF": "W0",
    "THAILAND": "W1",
    "TIMOR LESTE": "Z3",
    "TOGO": "W2",
    "TOKELAU": "W3",
    "TONGA": "W4",
    "TRINIDAD AND TOBAGO": "W5",
    "TUNISIA": "W6",
    "TURKEY": "W8",
    "TURKMENISTAN": "2E",
    "TURKS AND CAICOS ISLANDS": "W7",
    "TUVALU": "2G",
    "UGANDA": "W9",
    "UKRAINE": "2H",
    "UNITED ARAB EMIRATES": "C0",
    "UNITED KINGDOM": "X0",

    "UNITED STATES MINOR OUTLYING ISLANDS": "2J",
    "URUGUAY": "X3",
    "UZBEKISTAN": "2K",
    "VANUATU": "2L",
    "VENEZUELA": "X5",
    "VIET NAM": "Q1",
    "VIRGIN ISLANDS BRITISH": "D8",
    "BRITISH VIRGIN ISLANDS": "D8",
    "VIRGIN ISLANDS U.S.": "VI",
    "WALLIS AND FUTUNA": "X8",
    "WESTERN SAHARA": "U5",
    "YEMEN": "T7",
    "ZAMBIA": "Y4",
    "ZIMBABWE": "Y5",
    "UNKNOWN ": "XX",
    # Probably shouldn't be here
    "ENGLAND AND WALES": "X0",
}

countries = {
    "AFGHANISTAN": "AF",
    "\u00c5LAND ISLANDS": "AX",
    "ALBANIA": "AL",
    "ALGERIA": "DZ",
    "AMERICAN SAMOA": "AS",
    "ANDORRA": "AD",
    "ANGOLA": "AO",
    "ANGUILLA": "AI",
    "ANTARCTICA": "AQ",
    "ANTIGUA AND BARBUDA": "AG",
    "ARGENTINA": "AR",
    "ARMENIA": "AM",
    "ARUBA": "AW",
    "AUSTRALIA": "AU",
    "AUSTRIA": "AT",
    "AZERBAIJAN": "AZ",
    "BAHAMAS": "BS",
    "BAHRAIN": "BH",
    "BANGLADESH": "BD",
    "BARBADOS": "BB",
    "BELARUS": "BY",
    "BELGIUM": "BE",
    "BELIZE": "BZ",
    "BENIN": "BJ",
    "BERMUDA": "BM",
    "BHUTAN": "BT",
    "BOLIVIA PLURINATIONAL STATE OF": "BO",
    "BONAIRE SINT EUSTATIUS AND SABA": "BQ",
    "BOSNIA AND HERZEGOVINA": "BA",
    "BOTSWANA": "BW",
    "BOUVET ISLAND": "BV",
    "BRAZIL": "BR",
    "BRITISH INDIAN OCEAN TERRITORY": "IO",
    "BRUNEI DARUSSALAM": "BN",
    "BULGARIA": "BG",
    "BURKINA FASO": "BF",
    "BURUNDI": "BI",
    "CAMBODIA": "KH",
    "CAMEROON": "CM",
    "CANADA": "CA",
    "CAPE VERDE": "CV",
    "CAYMAN ISLANDS": "KY",
    "CENTRAL AFRICAN REPUBLIC": "CF",
    "CHAD": "TD",
    "CHILE": "CL",
    "CHINA": "CN",
    "CHRISTMAS ISLAND": "CX",
    "COCOS KEELING ISLANDS": "CC",
    "COLOMBIA": "CO",
    "COMOROS": "KM",
    "CONGO": "CG",
    "CONGO THE DEMOCRATIC REPUBLIC OF THE": "CD",
    "COOK ISLANDS": "CK",
    "COSTA RICA": "CR",
    "C\u00d4TE D IVOIRE": "CI",
    "CROATIA": "HR",
    "CUBA": "CU",
    "CURA\u00c7AO": "CW",
    "CYPRUS": "CY",
    "CZECH REPUBLIC": "CZ",
    "DENMARK": "DK",
    "DJIBOUTI": "DJ",
    "DOMINICA": "DM",
    "DOMINICAN REPUBLIC": "DO",
    "ECUADOR": "EC",
    "EGYPT": "EG",
    "EL SALVADOR": "SV",
    "EQUATORIAL GUINEA": "GQ",
    "ERITREA": "ER",
    "ESTONIA": "EE",
    "ETHIOPIA": "ET",
    "FALKLAND ISLANDS MALVINAS ": "FK",
    "FAROE ISLANDS": "FO",
    "FIJI": "FJ",
    "FINLAND": "FI",
    "FRANCE": "FR",
    "FRENCH GUIANA": "GF",
    "FRENCH POLYNESIA": "PF",
    "FRENCH SOUTHERN TERRITORIES": "TF",
    "GABON": "GA",
    "GAMBIA": "GM",
    "GEORGIA": "GE",
    "GERMANY": "DE",
    "GHANA": "GH",
    "GIBRALTAR": "GI",
    "GREECE": "GR",
    "GREENLAND": "GL",
    "GRENADA": "GD",
    "GUADELOUPE": "GP",
    "GUAM": "GU",
    "GUATEMALA": "GT",
    "GUERNSEY": "GG",
    "GUINEA": "GN",
    "GUINEA BISSAU": "GW",
    "GUYANA": "GY",
    "HAITI": "HT",
    "HEARD ISLAND AND MCDONALD ISLANDS": "HM",
    "HOLY SEE VATICAN CITY STATE ": "VA",
    "HONDURAS": "HN",
    "HONG KONG": "HK",
    "HUNGARY": "HU",
    "ICELAND": "IS",
    "INDIA": "IN",
    "INDONESIA": "ID",
    "IRAN ISLAMIC REPUBLIC OF": "IR",
    "IRAQ": "IQ",
    "IRELAND": "IE",
    "ISLE OF MAN": "IM",
    "ISRAEL": "IL",
    "ITALY": "IT",
    "JAMAICA": "JM",
    "JAPAN": "JP",
    "JERSEY": "JE",
    "JORDAN": "JO",
    "KAZAKHSTAN": "KZ",
    "KENYA": "KE",
    "KIRIBATI": "KI",
    "KOREA DEMOCRATIC PEOPLE S REPUBLIC OF": "KP",
    "KOREA REPUBLIC OF": "KR",
    "KUWAIT": "KW",
    "KYRGYZSTAN": "KG",
    "LAO PEOPLE S DEMOCRATIC REPUBLIC": "LA",
    "LATVIA": "LV",
    "LEBANON": "LB",
    "LESOTHO": "LS",
    "LIBERIA": "LR",
    "LIBYA": "LY",
    "LIECHTENSTEIN": "LI",
    "LITHUANIA": "LT",
    "LUXEMBOURG": "LU",
    "MACAO": "MO",
    "MACEDONIA THE FORMER YUGOSLAV REPUBLIC OF": "MK",
    "MADAGASCAR": "MG",
    "MALAWI": "MW",
    "MALAYSIA": "MY",
    "MALDIVES": "MV",
    "MALI": "ML",
    "MALTA": "MT",
    "MARSHALL ISLANDS": "MH",
    "MARTINIQUE": "MQ",
    "MAURITANIA": "MR",
    "MAURITIUS": "MU",
    "MAYOTTE": "YT",
    "MEXICO": "MX",
    "MICRONESIA FEDERATED STATES OF": "FM",
    "MOLDOVA REPUBLIC OF": "MD",
    "MONACO": "MC",
    "MONGOLIA": "MN",
    "MONTENEGRO": "ME",
    "MONTSERRAT": "MS",
    "MOROCCO": "MA",
    "MOZAMBIQUE": "MZ",
    "MYANMAR": "MM",
    "NAMIBIA": "NA",
    "NAURU": "NR",
    "NEPAL": "NP",
    "NETHERLANDS": "NL",
    "NEW CALEDONIA": "NC",
    "NEW ZEALAND": "NZ",
    "NICARAGUA": "NI",
    "NIGER": "NE",
    "NIGERIA": "NG",
    "NIUE": "NU",
    "NORFOLK ISLAND": "NF",
    "NORTHERN MARIANA ISLANDS": "MP",
    "NORWAY": "NO",
    "OMAN": "OM",
    "PAKISTAN": "PK",
    "PALAU": "PW",
    "PALESTINE STATE OF": "PS",
    "PANAMA": "PA",
    "PAPUA NEW GUINEA": "PG",
    "PARAGUAY": "PY",
    "PERU": "PE",
    "PHILIPPINES": "PH",
    "PITCAIRN": "PN",
    "POLAND": "PL",
    "PORTUGAL": "PT",
    "PUERTO RICO": "PR",
    "QATAR": "QA",
    "R\u00c9UNION": "RE",
    "ROMANIA": "RO",
    "RUSSIAN FEDERATION": "RU",
    "RWANDA": "RW",
    "SAINT BARTH\u00c9LEMY": "BL",
    "SAINT HELENA ASCENSION AND TRISTAN DA CUNHA": "SH",
    "SAINT KITTS AND NEVIS": "KN",
    "SAINT LUCIA": "LC",
    "SAINT MARTIN FRENCH PART ": "MF",
    "SAINT PIERRE AND MIQUELON": "PM",
    "SAINT VINCENT AND THE GRENADINES": "VC",
    "SAMOA": "WS",
    "SAN MARINO": "SM",
    "SAO TOME AND PRINCIPE": "ST",
    "SAUDI ARABIA": "SA",
    "SENEGAL": "SN",
    "SERBIA": "RS",
    "SEYCHELLES": "SC",
    "SIERRA LEONE": "SL",
    "SINGAPORE": "SG",
    "SINT MAARTEN DUTCH PART ": "SX",
    "SLOVAKIA": "SK",
    "SLOVENIA": "SI",
    "SOLOMON ISLANDS": "SB",
    "SOMALIA": "SO",
    "SOUTH AFRICA": "ZA",
    "SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS": "GS",
    "SOUTH SUDAN": "SS",
    "SPAIN": "ES",
    "SRI LANKA": "LK",
    "SUDAN": "SD",
    "SURINAME": "SR",
    "SVALBARD AND JAN MAYEN": "SJ",
    "SWAZILAND": "SZ",
    "SWEDEN": "SE",
    "SWITZERLAND": "CH",
    "SYRIAN ARAB REPUBLIC": "SY",
    "TAIWAN PROVINCE OF CHINA": "TW",
    "TAJIKISTAN": "TJ",
    "TANZANIA UNITED REPUBLIC OF": "TZ",
    "THAILAND": "TH",
    "TIMOR LESTE": "TL",
    "TOGO": "TG",
    "TOKELAU": "TK",
    "TONGA": "TO",
    "TRINIDAD AND TOBAGO": "TT",
    "TUNISIA": "TN",
    "TURKEY": "TR",
    "TURKMENISTAN": "TM",
    "TURKS AND CAICOS ISLANDS": "TC",
    "TUVALU": "TV",
    "UGANDA": "UG",
    "UKRAINE": "UA",
    "UNITED ARAB EMIRATES": "AE",
    "UNITED KINGDOM": "GB",
    "UNITED STATES": "US",
    "USA": "US",
    "UNITED STATES MINOR OUTLYING ISLANDS": "UM",
    "URUGUAY": "UY",
    "UZBEKISTAN": "UZ",
    "VANUATU": "VU",
    "VENEZUELA BOLIVARIAN REPUBLIC OF": "VE",
    "VIET NAM": "VN",
    "VIRGIN ISLANDS BRITISH": "VG",
    "VIRGIN ISLANDS U.S.": "VI",
    "WALLIS AND FUTUNA": "WF",
    "WESTERN SAHARA": "EH",
    "YEMEN": "YE",
    "ZAMBIA": "ZM",
    "ZIMBABWE": "ZW"
}

def parse_durwordsen(val):

    delta = datetime.timedelta()
    num = None

    val = number_parser.parse(val)

    val = val.replace("\xa0", " ")

    res = re.split(r'[ ,.:;-]+', val)

    for v in res:

        v = v.lower()

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
    value = re.split(r'[^a-zA-Z0-9]+', value)
    value = " ".join(value)
    try:
        value = datetime.datetime.strptime(value, "%B %d %Y").date()
        return Date(value)
    except:
        pass
    try:
        value = datetime.datetime.strptime(value, "%b %d %Y").date()
        return Date(value)
    except:
        pass
    try:
        value = datetime.datetime.strptime(value, "%B %d %y").date()
        return Date(value)
    except:
        pass
    try:
        value = datetime.datetime.strptime(value, "%b %d %y").date()
        return Date(value)
    except:
        pass
    raise RuntimeError(
        "Could not parse %s with datemonthedayyearen" % value
    )

def datemonthyearen(pre, value):
    value = value.strip()
    value = re.split(r'[^a-zA-Z0-9]+', value)
    value = " ".join(value)
    try:
        value = datetime.datetime.strptime(value, "%B %Y").date()
        return Date(value)
    except:
        pass
    try:
        value = datetime.datetime.strptime(value, "%b %Y").date()
        return Date(value)
    except:
        pass
    raise RuntimeError(
        "Could not parse %s with datemonthyearen" % value
    )

def datemonthdayen(pre, value):
    value = value.strip()
    try:
        value = datetime.datetime.strptime(value, "%B %d").date()
        return Date(value)
    except:
        pass
    try:
        value = datetime.datetime.strptime(value, "%b %d").date()
        return Date(value)
    except:
        pass
    raise RuntimeError(
        "Could not parse %s with datemonthedayen" % value
    )

def stateprovnameen(pre, value):
    value = value.strip()
    value = re.split(r'[^a-zA-Z0-9]+', value)
    value = " ".join(value)
    value = value.upper()
    if value in states:
        return String(states[value])
    else:
        raise RuntimeError("Don't know state %s" % value)

def edgarprovcountryen(pre, value):
    value = value.strip()
    value = re.split(r'[^a-zA-Z0-9]+', value)
    value = " ".join(value)
    value = value.upper()
    if value in state_country:
        return String(state_country[value])
    else:
        raise RuntimeError("Don't know state/province/country %s" % value)

def countrynameen(pre, value):
    value = value.strip()
    value = re.split(r'[^a-zA-Z0-9]+', value)
    value = " ".join(value)
    value = value.upper()
    if value in countries:
        return String(countries[value])
    else:
        raise RuntimeError("Don't know country %s" % value)

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

    # Is there a tidier way?
    value = value.replace(" ", "")

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

def durweek(pre, value):
    value = value.strip()
    value = int(value)

    # Weeks
    value = datetime.timedelta(days=value * 7)

    # This rounds off the seconds
    value = datetime.timedelta(days = value.days)

    return Duration(value)

def durday(pre, value):
    value = value.strip()
    value = int(value)
    value = datetime.timedelta(days=value)
    return Duration(value)

def durhour(pre, value):
    value = value.strip()
    value = int(value)
    value = datetime.timedelta(hours=value)
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

def dateyearmonthday(pre, value):
    value = value.strip()
    elts = re.split(r'[^0-9]+', value)
    value = datetime.date(int(elts[0]), int(elts[1]), int(elts[2]))
    return Date(value)

def datemonthdayyear(pre, value):
    value = value.strip()
    elts = re.split(r'[^0-9]+', value)
    value = datetime.date(int(elts[2]), int(elts[0]), int(elts[1]))
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
    value = value.lower()
    if value in { "nil", "none", "", "no", "null" }:
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

# FIXME: A typo in a form, probably
registry[ET.QName(XBRL_XFORM, "datemonthedayyearen")] = datemonthdayyearen
registry[ET.QName(XBRL_XFORM, "datemontheyearen")] = datemonthyearen

registry[ET.QName(XBRL_XFORM, "datemonthdayen")] = datemonthdayen
registry[ET.QName(XBRL_XFORM, "datemonthyearen")] = datemonthyearen
registry[ET.QName(XBRL_XFORM, "datedaymonthyearen")] = datedaymonthyearen
registry[ET.QName(XBRL_XFORM_0, "datedaymonthyearen")] = datedaymonthyearen
registry[ET.QName(SEC_XFORM, "stateprovnameen")] = stateprovnameen
registry[ET.QName(SEC_XFORM, "edgarprovcountryen")] = edgarprovcountryen
registry[ET.QName(SEC_XFORM, "countrynameen")] = countrynameen
registry[ET.QName(SEC_XFORM, "exchnameen")] = exchnameen
registry[ET.QName(SEC_XFORM, "entityfilercategoryen")] = entityfilercategoryen
registry[ET.QName(SEC_XFORM, "duryear")] = duryear
registry[ET.QName(SEC_XFORM, "durwordsen")] = durwordsen
registry[ET.QName(SEC_XFORM, "durmonth")] = durmonth
registry[ET.QName(SEC_XFORM, "durweek")] = durweek
registry[ET.QName(SEC_XFORM, "durday")] = durday
registry[ET.QName(SEC_XFORM, "durhour")] = durhour
registry[ET.QName(XBRL_XFORM, "datemonthday")] = datemonthday
registry[ET.QName(XBRL_XFORM, "datedaymonthyear")] = datedaymonthyear
registry[ET.QName(XBRL_XFORM, "dateyearmonthday")] = dateyearmonthday
registry[ET.QName(XBRL_XFORM_0, "datedaymonthyear")] = datedaymonthyear
registry[ET.QName(XBRL_XFORM, "datemonthdayyear")] = datemonthdayyear
registry[ET.QName(XBRL_XFORM_0, "datemonthdayyear")] = datemonthdayyear
registry[ET.QName(XBRL_XFORM, "booleanfalse")] = booleanfalse
registry[ET.QName(XBRL_XFORM, "booleantrue")] = booleantrue
registry[ET.QName(XBRL_XFORM_0, "booleanfalse")] = booleanfalse
registry[ET.QName(XBRL_XFORM_0, "booleantrue")] = booleantrue
registry[ET.QName(XBRL_XFORM, "nocontent")] = nocontent
registry[ET.QName(XBRL_XFORM_0, "nocontent")] = nocontent
registry[ET.QName(XBRL_XFORM, "numdotdecimal")] = numdotdecimal
registry[ET.QName(XBRL_XFORM_0, "numdotdecimal")] = numdotdecimal
registry[ET.QName(XBRL_XFORM, "numcommadecimal")] = numdotdecimal
registry[ET.QName(XBRL_XFORM_0, "numcommadecimal")] = numdotdecimal
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

