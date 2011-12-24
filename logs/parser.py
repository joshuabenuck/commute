import sys

filename = sys.argv[1]
file = open(filename)
numbers = {}
fixes = {}
for line in file.xreadlines():
    parts = line.split("\t")
    length = len(parts)
    if length == 2: continue
    if length != 8 and length != 9 and length != 10: print length, line.replace("\t", "|")
    time = parts[0][1:]; lat = parts[1][3:]; lon = parts[2][3:]
    alt = parts[3][1:]; speed = parts[4][1:]; course = parts[5][1:]
    fix = parts[6][1:]; num = parts[7][1:]
    fix = ord(fix)
    if len(num) == 0: num = 0
    num = ord(num)

