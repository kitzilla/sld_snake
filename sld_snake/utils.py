import datetime
from itertools import product
import math
import re



def stringify(obj):
    if type(obj) == None.__class__:
        return ''

    if type(obj) == datetime.date:
        return obj.isoformat()

    if type(obj) == datetime.datetime:
        ret = obj.isoformat()
        # Truncate microseconds to milliseconds
        match = re.match(r'^(.+?\.\d{6})(|[+-](\d+))$', ret)
        if match:
            ret = match.group(1)[:-3] + match.group(2)
        return ret

    if type(obj) == bool:
        return str(obj).lower()

    if type(obj) == float:
        if math.isnan(obj):
            return 'NaN'
        if math.isinf(obj):
            if obj > 0:
                return 'Infinity'
            else:
                return '-Infinity'

    return str(obj)


def parseBool(obj):
    if obj is True or obj == 'true' or obj == '1' or obj == 1:
        return True
    if obj is False or obj == 'false' or obj == '0' or obj == 0:
        return False
    raise ValueError(f'{repr(obj)} cannot be converted to bool')


def parseDouble(obj):
    if type(obj) in [int, float]:
        return float(obj)

    if obj is None:
        return float('nan')

    if type(obj) == str:
        obj = obj.strip()
        if re.match(r'^[+-]?nan$', obj, re.I):
            if re.match(r'^[+-]?NaN$', obj):
                return float('nan')
            raise ValueError(f'Cannot parse {repr(obj)} as number')
        
        if obj.lower() == 'inf':
            raise ValueError(f'Cannot parse {repr(obj)} as number')
        
        match = re.match(r'^([+-]|)Infinity$', obj)
        if match:
            return float(match.group(1) + 'inf')

        try:
            return float(obj)
        except ValueError:
            raise ValueError(f'Cannot parse {repr(obj)} as number')

    raise TypeError(f'Cannot parse {repr(obj)} as number')


def parseDate(obj):
    if type(obj) == datetime.datetime:
        return obj

    if type(obj) == datetime.date:
        return datetime.datetime(year=obj.year, month=obj.month, day=obj.day)
        
    elif type(obj) == str:
        time_str = obj
        if re.match(r'.+?[+-]\d{2}:\d{2}$', time_str):
            # datetime.strftime does not accept colon in timezone (https://bugs.python.org/issue15873) 
            # whilst GeoServer requires it and datetime.isoformat() includes it
            time_str = time_str[:-3] + time_str[-2:]
        elif re.match(r'.+?T.+?[+-]\d{2}$', time_str):
            # datetime.strftime does not accept hour-only notation for timezones
            # whilst GeoServer accepts it
            time_str += '00'

        date_formats = ['%Y-%m-%d', '']
        time_formats = ['%H:%M:%S', '%H:%M:%S.%f', '']
        tz_formats = [ '', 'Z', '%z']
        
        for fmt_d, fmt_t, fmt_z in product(date_formats, time_formats, tz_formats):
            format = fmt_d
            format += 'T' if fmt_d != '' and fmt_t != '' else ''
            if fmt_t != '':
                format += fmt_t
                if fmt_z != '':
                    format += fmt_z
            try:
                dt = datetime.datetime.strptime(time_str, format)
            except ValueError:
                pass
            else:
                return dt
        raise ValueError(f'{repr(time_str)} cannot be parsed to datetime object')

    else:
        raise TypeError(f'{repr(time_str)} cannot be parsed to datetime object')
