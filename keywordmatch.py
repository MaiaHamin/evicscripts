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
    with open('StateLawKeywords.csv', "rt") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        count = 1
        for row in list(reader):
            if (count in questions):
                keywords = []
                for k in row[1:]:
                    if (k != ""):
                        keywords.append(k)
                keyword_dict[count] = keywords
            count += 1
    return keyword_dict



def getmatches(keywords, lawfilenames, pref):
    count_dict = {}
    split_keys = []
    matches = {}
    print(lawfilenames)
    print(pref)
    for lawfile in lawfilenames:
        with open (lawfile, 'r') as f:
            line_count = 0
            last_sec = ""
            for line in f:
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
                for word in keywords:
                    count = line.count(word)
                    if count != 0:
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
        for text in fulltext.split("\n"):
            num_matches = 0.
            length = float(len(text))
            if (length > 15):
                for word in keywords:
                    count = text.count(word)
                    if (count != 0):
                        num_matches += (float(count) * float(len(word))/ np.log(length)) * np.log (line_count / count_dict[word])
                wrst_bst_keys.append((sec, text, num_matches))
                wrst_bst_keys.sort(key=lambda k: k[2], reverse=True)
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
                outr = ranked[0][0]
                outm = matches[ranked[0][0]]
            else:
                outr = ""
                outm = ""
            outsheet.write(startrow + 1, startcol, outr)
            startcol += 1
            outsheet.write(startrow + 1, startcol, outm)
            startcol += 4
        startrow += 1
    outxl.save('Generated.xls')


def questionanswer(state, qnum):
    state_ind = states.index(state)
    laws = allfilenames[state_ind]
    lawfilenames = []
    for law in laws:
        lawfilenames.append("./" + state + "/" + law)
    prefix = prefixes[state_ind]
    keyword_dict = get_keywords([int(qnum)])
    print(keyword_dict)
    keywords = keyword_dict[int(qnum)]
    print(keywords)
    matches, count_dict, line_count = getmatches(keywords, lawfilenames, prefix)
    ranked = rankmatches(keywords, count_dict, line_count, matches, 3)
    for match in ranked:
        print(str(match[0]) + ": " + str(match[2]))
        print(match[1])

        print("- - - - - - - - - - - - - -")


if __name__ == "__main__":
    if sys.argv[2] == "all":
        sheetfill(sys.argv[1])
    else:
        questionanswer(sys.argv[1], sys.argv[2])
