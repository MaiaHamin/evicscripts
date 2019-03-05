import csv
import nltk
import re
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
ps = PorterStemmer()
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
import numpy as np
import sys
import xlwt
from collections import Counter

# Add new states
states = ["AL", "FL", "LA", "MD", "ME", "NV", "SC", "TX"]
# data from Jon Mayer?
allfilenames = [
["AlabamaProperty.txt", "AlabamaPropertyA.txt"],
["FLLaws.txt", "FLLaws2.txt", "FLResTen.txt", "FLEject.txt", "FL3.txt"],
["LAEvicting.txt", "LASaleEviction.txt"],
["MarylandLandlordsTenants.txt"],
["Rental.txt", "EntryandDetainer.txt"],
["NVLaws.txt", "NVLaws2.txt"],
["SCEjectment.txt", "SCLandlordTenGen.txt", "SCResLandlordTen.txt", "SCLeaseholdEstates.txt"],
["TexasProperty.txt", "TexasTwo.txt"]]
prefixes = [
"Ala.Code 1975 §",
"West’s F.S.A. §",
"LSA-C.C.P.",
"MD Code, Real Property, §",
"14 M.R.S.A. §",
"N.R.S.",
"Code 1976 §",
"V.T.C.A., Property Code §"]

outxl = xlwt.Workbook()
outsheet = outxl.add_sheet('compared')

def w_tokenize(s):
    return nltk.word_tokenize(s)

def get_keywords(questions, use_stem):
    keyword_dict = {}
    with open('WeightedKeywords.csv', "rt") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        count = 1
        for row in list(reader):
            if (count in questions):
                keywords = {}
                for k in row[1:]:
                    if (k != ""):
                        temp = k.split("*")
                        if len(temp) > 1:
                            kw = temp[0]
                            if use_stem:
                                kw = ps.stem(kw)
                            keywords[kw] = temp[1]
                keyword_dict[count] = keywords
            count += 1
    print(keyword_dict)
    return keyword_dict




def getmatches(keywords, lawfilenames, pref, use_stem):
    count_dict = {}
    split_keys = []
    matches = {}
    #print(lawfilenames)
    #print(pref)
    for lawfile in lawfilenames:
        with open (lawfile, 'r') as f:
            line_count = 0
            last_sec = ""
            for line in f:
                line_count += 1
                #print("linebeg: " + line[0:len(pref)])
                if line[0:len(pref)] == pref:
                    #print("lineend " + line[len(pref)])
                    last_sec = line[len(pref):]
                low_line = line.lower()
                sec = last_sec
                if line[0] == "(":
                    sec += " " + line[1]
                    line = line[4:]
                if (len(line) > 1 and line[1] == "."):
                    sec += " " + line[0]
                    line = line[4:]
                wds = []
                for word in low_line.split():
                    if use_stem:
                        word = ps.stem(word)
                    wds.append(word.lower())
                counted = Counter(wds)
                addto = False
                for word in keywords:
                    if word in counted:
                        addto = True
                        if word in count_dict:
                            count_dict[word] += 1
                        else:
                            count_dict[word] = 1
                if addto:
                    if sec in matches:
                        matches[sec] += "\n" + line
                    else:
                        matches[sec] = line

    return matches, count_dict, line_count

def rankmatches(keywords, count_dict, line_count, matches, top_n, use_stem):
    wrst_bst_keys = []
    for (sec, fulltext) in matches.items():
        bestscore = 0
        bestsent = ""
        for sent in fulltext.split("."):
            if use_stem:
                #words = sent.split()
                #for i in range(len(words)):
                sent = ps.stem(words[i])
                #words = " ".join(words)
            num_matches = 0.
            length = float(len(sent))
            if (length > 15):
                for word in keywords.keys():
                    count = sent.count(word)
                    if (count != 0) and word in count_dict:
                        num_matches += float(keywords[word]) * (float(count) * float(len(word))/ np.log(length)) * np.log (line_count / count_dict[word])
            if num_matches > bestscore:
                bestsent = sent
                bestscore = num_matches
        wrst_bst_keys.append((bestscore, sec.replace("\n", " "), bestsent, fulltext))
        wrst_bst_keys.sort(key=lambda k: k[0], reverse=True)
        wrst_bst_keys = wrst_bst_keys[:min(len(wrst_bst_keys), top_n)]

    return wrst_bst_keys

def sheetfill(qstates):
    questions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    startrow = 0
    if not isinstance(qstates, list):
        qstates = [qstates]
    for state in qstates:
        startcol = 3
        state_ind = states.index(state)
        laws = allfilenames[state_ind]
        lawfilenames = []
        for law in laws:
            lawfilenames.append("./" + state + "/" + law)
        prefix = prefixes[state_ind]
        print(prefix)
        print(lawfilenames)
        print(prefix)

        keyword_dict = get_keywords(questions)

        for q in questions:
            keywords = keyword_dict[q]
            print(keywords)
            matches, count_dict, line_count = getmatches(keywords, lawfilenames, prefix)
            ranked = rankmatches(keywords, count_dict, line_count, matches, 5)
            if len(ranked) > 0:
                outr = ranked[0][1]
                outm = ranked[0][3]
            else:
                outr = ""
                outm = ""
            outsheet.write(startrow + 1, startcol, outr)
            startcol += 1
            outsheet.write(startrow + 1, startcol, outm)
            startcol += 4
        startrow += 1
        outxl.save(state + '/Generated.xls')


def questionanswer(state, qnum, nmatches):
    use_stem = False
    state_ind = states.index(state)
    laws = allfilenames[state_ind]
    lawfilenames = []
    for law in laws:
        lawfilenames.append("./" + state + "/" + law)
    prefix = prefixes[state_ind]
    keyword_dict = get_keywords([int(qnum)], use_stem)
    print("Using keywords: ")
    keywords = keyword_dict[int(qnum)]
    print(keywords.keys())
    matches, count_dict, line_count = getmatches(keywords, lawfilenames, prefix, use_stem)
    ranked = rankmatches(keywords, count_dict, line_count, matches, nmatches, use_stem)
    for match in ranked:
        print(str(match[1]) + " (with score " + str(match[0]) + ")")
        outstr = match[3].replace(match[2], " ||| " + match[2] + " ||| ")
        print(outstr)

        print("- - - - - - - - - - - - - -")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        invalidq = True
        while invalidq:
            mode = input("Enter question number (type 'all' for spreadsheet fill).")
            if mode == "all":
                sheetfill(state)
                invalidq = False
            else:
                try:
                    mode = int(mode)
                    if mode < 16 and mode > 0:
                        invalidq = False
                    else:
                        print("Sorry, that's not a valid question number")
                except e:
                    print("Sorry, that's not a valid question number")

                invalidState = True
                while invalidState:
                    state = input("Enter the two-letter state abbreviation.")
                    if state in states:
                        invalidState = False
                    else:
                        print("Sorry, we don't have that state's files available yet.")


                invalidq = True
                while invalidq:
                    nmatches = input("How many matches do you want to view?")
                    try:
                        nmatches = int(nmatches)
                        if nmatches < 10 and nmatches > 0:
                            invalidq = False
                        else:
                            print("Sorry, that's not a valid number of matches.")
                    except e:
                        print("Sorry, that's not a valid number of matches.")

                questionanswer(state, mode, nmatches)

    else:
        questionanswer(sys.argv[1], sys.argv[2], 3)
