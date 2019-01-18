import itertools
import xlrd
import xlwt
import re

abssimcutoff = 10
sharedwordscutoff = 30

def comparenumber(t1, t2):
    measures = ["hours", "days", "weeks"]
    if t1 == "N/A":
        if t2 == "N/A":
            return 2
        return 0
    if t2 == "N/A":
        return 0

    if len(t1) < 10 and len(t2) < 10:
        re1 = re.search(r'\d+', t1)
        re2 = re.search(r'\d+', t2)
        if re1 is not None:
            i1 = int(re1.group())
            if re2 is not None:
                i2 = int(re2.group())
                if i1 == i2:
                    return 2
                return 0
        if re2 is not None:
            return 0
    return 1




def longestsharedtext(w1, w2):
    w1 = w1.replace("§", "")
    w1 = w1.replace(".", "")
    w2 = w2.replace("§", "")
    w2 = w2.replace(".", "")
    if (len(w1) == 0):
        return ""
    words1  = w1.split()
    words2 = w2.split()

    len1 = len(words1)
    len2 = len(words2)
    max_len = 0
    reg_max = 0
    string_max = 0
    for i in range(len1):
        for j in range(len2):
            if (words1[i] == words2[j]):
                k = 0
                while (i + k < len1 and
                j + k < len2 and
                words1[i + k] == words2[j + k]):
                    k += 1
                if (max_len < k):
                    max_len = k
                    reg_max = i
                    string_max = j
        if (max_len == 0):
            return "*"
    #frontreg = longest_pattern(words1[:reg_max], words2[:string_max])
    #backreg = longest_pattern(words1[reg_max + max_len:], words2[string_max + max_len:])
    return " ".join(words1[reg_max: reg_max + max_len])
    if (len(w1) == 0):
        return ""
    words1  = w1.split()
    words2 = w2.split()

    len1 = len(words1)
    len2 = len(words2)
    max_len = 0
    reg_max = 0
    string_max = 0
    for i in range(len1):
        for j in range(len2):
            if (words1[i] == words2[j]):
                k = 0
                while (i + k < len1 and
                j + k < len2 and
                words1[i + k] == words2[j + k]):
                    k += 1
                if (max_len < k):
                    max_len = k
                    reg_max = i
                    string_max = j
        if (max_len == 0):
            return "*"
    #frontreg = longest_pattern(words1[:reg_max], words2[:string_max])
    #backreg = longest_pattern(words1[reg_max + max_len:], words2[string_max + max_len:])
    return " ".join(words1[reg_max: reg_max + max_len])

def longestsharedsection(w1, w2):
    w1 = w1.replace("§", "")
    words1 = w1.replace(".", "")
    w2 = w2.replace("§", "")
    words2  = w2.replace(".", "")
    if (len(w1) == 0):
        return ""

    len1 = len(words1)
    len2 = len(words2)
    max_len = 0
    reg_max = 0
    string_max = 0
    for i in range(len1):
        for j in range(len2):
            if (words1[i] == words2[j]):
                k = 0
                while (i + k < len1 and
                j + k < len2 and
                words1[i + k] == words2[j + k]):
                    k += 1
                if (max_len < k):
                    max_len = k
                    reg_max = i
                    string_max = j
        if (max_len == 0):
            return "*"
    #frontreg = longest_pattern(words1[:reg_max], words2[:string_max])
    #backreg = longest_pattern(words1[reg_max + max_len:], words2[string_max + max_len:])
    return (words1[reg_max: reg_max + max_len])

def comparesection(studa, studb):
    shared = longestsharedsection(studa, studb)
    print("seclen:" + str(len(shared)))
    print("st1:" + str(len(studa)))
    print("st2:" + str(len(studb)))
    if len(studa) - len(shared) < 10:
        if len(studb) - len(shared) < 10:
            return 2
        else:
            return 1
    if len(studb) - len(shared) < 10:
        return 1
    return 0

def comparetext(studa, studb):
    shared = longestsharedtext(studa, studb)
    print("textlen:" + str(len(shared)))
    print("st1:" + str(len(studa)))
    print("st2:" + str(len(studb)))
    if len(studa) - len(shared) < 10:
        if len(studb) - len(shared) < 10:
            return 2
        else:
            return 1
    if len(studb) - len(shared) < 10:
        return 1
    return 0



rb = xlrd.open_workbook('StateLawsUpdated.xlsx')
outxl = xlwt.Workbook()
outsheet = outxl.add_sheet('compared')

students = ["Maia", "Hyojin"]
wbindices = {"Hyojin":6, "Maia":3}
sheetsd = {}
for st in students:
    sheetsd[st] = rb.sheet_by_index(wbindices[st])

sheet1 = sheetsd[students[0]]
sheet2 = sheetsd[students[1]]
questions = []
qdict = {}
for rownum in range(max(sheet1.nrows, sheet2.nrows)):
    if rownum == 0:
        colnum = 1
        row = sheet1.row_values(rownum)
        for c in row:
            if c != "State" and c != "Geography":
                questions.append(c)
                if c[0] != qdict:
                    if c[1].isdigit():
                        qdict[c[0:2]] = {"match":True, "st1sec":"", "st2sec":"", "st1text":"", "st2text":""}
                    else:
                        qdict[c[0]] = {"match":True, "st1sec":"", "st2sec":"", "st1text":"", "st2text":""}
        for k in qdict.keys():
            outsheet.write(rownum, colnum, "Q " + str(k) + " match")
            colnum += 1
            outsheet.write(rownum, colnum, "Q " + str(k) + " " + students[0])
            colnum += 1
            outsheet.write(rownum, colnum, "Q " + str(k)  + " " + students[1])
            colnum += 1



    elif rownum < sheet1.nrows:
        row_rb1 = sheet1.row_values(rownum)
        row_rb2 = sheet2.row_values(rownum)

        state = row_rb1[0]
        muni = row_rb1[1]
        if muni == "State":
            outfname = state + "_match.txt"
        else:
            outfname = muni + "_match.txt"


        print("For " + str(muni) + ", " + str(state))
        lastkey = ""
        for colnum, (c1, c2) in enumerate(zip(row_rb1, row_rb2)):
            question = questions[colnum - 2]
            qkey = question[0]
            qpart = question[1]
            if qpart.isdigit():
                qkey = question[0:2]
                qpart = question[2]
            #if qpart == "a":
            if False:
                try:
                    if type(c1) == float:
                        i1 = c1
                        if type(c2) == float:
                            i2 = c2
                        else:
                            i2 = int(re.compile("(\d+)").match(c2).group(1))
                    else:
                        i1 = int(re.compile("(\d+)").match(c1).group(1))
                    qdict[qkey]["match"] = (i1 == i2)
                except:
                    qdict[qkey]["match"] =  False
                    print("there was no number")

            if qpart == "b" and False:
                #print("b" + str(longestshared(str(c1), str(c2))))
                qdict[qkey]["match"] = comparesection(str(c1), str(c2))
                qdict[qkey]["st1text"] = str(c1)
                qdict[qkey]["st2text"] = str(c2)

            if qpart == "c" and False:
                #print("c" + str(longestshared(str(c1), str(c2))))
                qdict[qkey]["match"] = comparetext(str(c1), str(c2))
                qdict[qkey]["st1text"] = str(c1)
                qdict[qkey]["st2text"] = str(c2)

            if qpart == "e":
                stc1 = str(c1)
                stc2 = str(c2)
                if stc1 is None:
                    stc1 = ""
                if stc2 is None:
                    stc2 = ""
                qdict[qkey]["match"] = comparenumber(stc1, stc2)
                qdict[qkey]["st1text"] = stc1
                qdict[qkey]["st2text"] = stc2


        colnum = 1
        outsheet.write(rownum, 0, muni + ", " + state)
        for k, v in qdict.items():
            if v["match"] == 2:
                outsheet.write(rownum, colnum, "Match")
                colnum += 1
                outsheet.write(rownum, colnum, str(v["st1text"]))
                colnum += 1
                outsheet.write(rownum, colnum, str(v["st2text"]))
                colnum += 1

            if v["match"] == 1:
                outsheet.write(rownum, colnum, "Open-Ended")
                colnum += 1
                outsheet.write(rownum, colnum, str(v["st1text"]))
                colnum += 1
                outsheet.write(rownum, colnum, str(v["st2text"]))
                colnum += 1

            if v["match"] == 0:
                outsheet.write(rownum, colnum, "Mismatch")
                colnum += 1
                outsheet.write(rownum, colnum, str(v["st1text"]))
                colnum += 1
                outsheet.write(rownum, colnum, str(v["st2text"]))
                colnum += 1
    outxl.save('StateLawCompare.xls')
