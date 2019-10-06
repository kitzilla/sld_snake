import re

def flatten_xml(string):
    return re.sub(r'>\s+<', '><', string.strip())


