import re


def fix_rev_zeros(ref):
    def replace_in_rev(match):
        return match.group(0).replace("O", "0").replace("o", "0")

    return re.sub(r'REV[0-9O]+', replace_in_rev, ref, flags=re.IGNORECASE)


def extract_ref(text):
    pattern = r'\d{3,4}/[A-Z]{2,3}/[A-Z]+/[A-Z]+/[A-Z]+/\d+/\d+/REV\d+'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return fix_rev_zeros(match.group(0))
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for i, line in enumerate(lines):
        if "SUBMITTAL" in line.upper() and "REF" in line.upper():
            inline = re.search(r'[\w]+/[\w/]+', line)
            if inline and inline.group(0).count('/') >= 5:
                return fix_rev_zeros(inline.group(0))
            if i + 1 < len(lines):
                nxt = lines[i + 1]
                if '/' in nxt and nxt.count('/') >= 5:
                    return fix_rev_zeros(nxt)
    return None
