import csv
import nltk
import re
from nltk.stem.wordnet import WordNetLemmatizer
lmtzr = WordNetLemmatizer()
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

def get_keywords(questions):
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
                            keywords[temp[0]] = temp[1]
                keyword_dict[count] = keywords
            count += 1
    return keyword_dict



def getmatches(keywords, lawfilenames, pref):
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
                line = line.lower()
                addto = False
                line_count += 1
                #print("linebeg: " + line[0:len(pref)])
                if line[0:len(pref)] == pref:
                    #print("lineend " + line[len(pref)])
                    last_sec = line[len(pref):]
                seen_words = []
                text = line
                sec = last_sec
                if line[0] == "(":
                    sec += " " + line[1]
                    text = line[4:]
                wds = []
                for word in line.split():
                    lemword = lmtzr.lemmatize(word)
                    wds.append(lemword)
                counted = Counter(wds)
                for word in keywords.keys():
                    if word in counted:
                        addto = True
                        if word in count_dict:
                            count_dict[word] += 1
                        else:
                            count_dict[word] = 1
                if addto:
                    if sec in matches:
                        matches[sec] += "\n" + text
                    else:
                        matches[sec] = text

    return matches, count_dict, line_count

def rankmatches(keywords, count_dict, line_count, matches, top_n):
    wrst_bst_keys = []
    for (sec, fulltext) in matches.items():
        for text in fulltext.split("."):
            num_matches = 0.
            length = float(len(text))
            if (length > 15):
                for word in keywords.keys():
                    count = text.count(word)
                    if (count != 0) and word in count_dict:
                        num_matches += float(keywords[word]) * (float(count) * float(len(word))/ np.log(length)) * np.log (line_count / count_dict[word])
                wrst_bst_keys.append((num_matches, sec.replace("\n", " "), text, fulltext))
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
    state_ind = states.index(state)
    laws = allfilenames[state_ind]
    lawfilenames = []
    for law in laws:
        lawfilenames.append("./" + state + "/" + law)
    prefix = prefixes[state_ind]
    keyword_dict = get_keywords([int(qnum)])
    print("Using keywords: ")
    keywords = keyword_dict[int(qnum)]
    print(keywords.keys())
    matches, count_dict, line_count = getmatches(keywords, lawfilenames, prefix)
    ranked = rankmatches(keywords, count_dict, line_count, matches, nmatches)
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
                        if mode < 10 and mode > 0:
                            invalidq = False
                        else:
                            print("Sorry, that's not a valid number of matches.")
                    except e:
                        print("Sorry, that's not a valid number of matches.")

                questionanswer(state, mode, nmatches)

    else:
        questionanswer(sys.argv[1], sys.argv[2], 3)
