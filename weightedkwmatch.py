#-*- encoding: utf-8 -*-

import csv
import nltk
import re
import os
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
ps = PorterStemmer()
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
stop_words = set(stopwords.words('english'))
import numpy as np
import sys
import xlwt
from collections import Counter


# Add new states
states = ["AK", "AL", "AR", "AZ", "CA", "CO", "DC", "DE", "FL", "IA", "ID", "IL", "IN",
"KS", "LA", "MA", "MD", "ME", "MI", "MO", "MS", "MT", "ND", "NJ", "NM", "NV", "NY", "OH",
"OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "VT", "WA", "WI", "WV", "WY"]

use_stem = True

outxl = xlwt.Workbook()
outsheet = outxl.add_sheet('compared')

prefixes = [
"AS §",
"Ala.Code 1975 §",
"A.C.A. §",
"A.R.S. §",
"West's Ann.Cal.Civ.Code §",
"C.R.S.A. §",
"DC ST §",
"25 Del.C. §",
"West’s F.S.A. §",
"I.C.A. §",
"I.C. §",
"765 ILCS",
"IC",
"K.S.A.",
"LSA-C.C.P.",
"M.G.L.A. 183 §",
"MD Code, Real Property, §",
"14 M.R.S.A. §",
"M.C.L.A.",
"V.A.M.S.",
"Miss. Code Ann. §",
"MCA",
"NDCC",
"N.J.S.A.",
"N. M. S. A. 1978, §",
"N.R.S.",
"McKinney's Real Property Law §",
"R.C. §",
"60 Okl.St.Ann. §",
"O.R.S. §",
"68 P.S. §",
"Gen.Laws 1956, §",
"Code 1976 §",
"SDCL §",
"T. C. A. §",
"V.T.C.A., Property Code §",
"27 V.S.A. §",
"West's RCWA",
"W.S.A.",
"W. Va. Code, §",
"W.S.1977 §"
]
# filepath? /Volumes/eviction/Intern Dropbox/Landlord_Tenant_Project/Text/

def getallstatesfiles():
    all_files = []
    for s in states:
        state_files = getonestatesfiles(s)
        all_files.append(state_files)
    return allfilenames

# Looks for all of the files in the directory named "s" where s is a two-letter
# state abbreviation. State files are stored in a directory "Text" in the
# directory above the evicscript directory where this file lives.
def getonestatesfiles(s):
    state_files = []
    print(os.path.join(os.getcwd(), "..", "Text", s))
    if os.path.isdir(os.path.join(os.getcwd(), "..", "Text", s)):
        for filename in os.listdir(os.path.join(os.getcwd(), "..", "Text", s)):
            if filename.endswith(".txt"):
                state_files.append(os.path.join(os.getcwd(), "..", "Text", s, filename))
    if len(state_files) == 0:
        print("WARNING:")
    print(str(len(state_files)) + " files found for " + s + ".")
    return state_files

def w_tokenize(s):
    return nltk.word_tokenize(s)

# Loops through every row of the csv. For every row, the first column describes
# the question, and all of the following columns hold keyword-weight pairs
# in the format "key*weight". This separates them, stores the keyword as the
# key to the weight in a dictionary, and then stores each of the dictionary
# of key-weight pairs for each question into a dictionary of all questions

def get_keywords():
    keyword_dict = {}
    with open('WeightedKeywords.csv', "rt") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        qnum = 1
        for row in list(reader):
            keywords = {}
            for kw_pair_s in row[1:]:
                if (kw_pair_s != ""):
                    kw_pair = kw_pair_s.split("*")
                    if len(kw_pair) > 1:
                        k = kw_pair[0]
                        weight = kw_pair[1]
                        if use_stem:
                            k_s = ""
                            k_word_list = k.split()
                            for k_word in k_word_list:
                                k_word_stem = ps.stem(k_word)
                                k_s += k_word_stem + " "
                            k = k_s[:-1]
                        keywords[k] = weight
            keyword_dict[qnum] = keywords
            qnum += 1

    if len(keyword_dict) == 0:
        print("WARNING: No keywords found.")
    return keyword_dict

def getmatches(keywords, lawfilenames, pref):
    count_dict = {}
    split_keys = []
    matches = {}
    line_count = 0
    for lawfile in lawfilenames:
        with open (lawfile, 'r') as f:
            line_count = 0
            last_sec = ""
            for line in f:
                line_count += 1
                if line[0:len(pref)] == pref:
                    last_sec = line[len(pref):]
                sec = last_sec
                if line[0] == "(":
                    sec += " " + line[1]
                    line = line[4:]
                if (len(line) > 1 and line[1] == "."):
                    sec += " " + line[0]
                    line = line[4:]
                low_line = line.lower()
                if use_stem:
                    wds = []
                    for word in low_line.split():
                        if len(word) > 3:
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

# Ranks the matches by finding the sentence with the highest concentration
# of keywords, where each occurence is weighted by the value specified in the
# keyword file.
def rankmatches(keywords, count_dict, line_count, matches, top_n):
    wrst_bst_keys = []
    for (sec, fulltext) in matches.items():
        bestscore = 0
        bestsent = ""
        for sent in fulltext.split("."):
            num_matches = 0.
            length = float(len(sent))
            stemline = sent
            if use_stem:
                wds = []
                for word in sent.split():
                    if len(word) > 3:
                        word = ps.stem(word)
                    wds.append(word.lower())
            stemline = " ".join(wds)
            if (length > 15):
                for word in keywords.keys():
                    count = stemline.count(word)
                    if (count != 0) and word in count_dict:
                        num_matches += float(keywords[word]) * (float(count) * float(len(word))/ np.log(length)) * np.log (line_count / count_dict[word])
            if num_matches > bestscore:
                bestsent = sent
                bestscore = num_matches
        wrst_bst_keys.append((bestscore, sec.replace("\n", " "), bestsent, fulltext))
        wrst_bst_keys.sort(key=lambda k: k[0], reverse=True)
        wrst_bst_keys = wrst_bst_keys[:min(len(wrst_bst_keys), top_n)]

    return wrst_bst_keys

# Fills in an excel spreadsheet with all best-choice matches for a single state.
def sheetfill(state):
    questions = [i for i in range(1, 17)]
    startrow = 0
    startcol = 3
    state_files = getonestatesfiles(state)
    state_ind = states.index(state)
    prefix = prefixes[state_ind]

    keyword_dict = get_keywords()

    for q in questions:
        keywords = keyword_dict[q]
        matches, count_dict, line_count = getmatches(keywords, state_files, prefix)
        ranked = rankmatches(keywords, count_dict, line_count, matches, 1)
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
    outxl.save(os.path.join(os.getcwd(), "..", "Spreadsheets", state + ".xls"))

# Answers a specific question with the nmatches best-match statutes
def questionanswer(state, qnum, nmatches):
    state_files = getonestatesfiles(state)
    state_ind = states.index(state)
    prefix = prefixes[state_ind]
    keyword_dict = get_keywords()
    print("Using keywords: ")
    keywords = keyword_dict[int(qnum)]
    print(keywords.keys())
    matches, count_dict, line_count = getmatches(keywords, state_files, prefix)
    ranked = rankmatches(keywords, count_dict, line_count, matches, nmatches)
    for match in ranked:
        print(str(match[1]) + " (with score " + str(match[0]) + ")")
        outstr = match[3].replace(match[2], " ||| " + match[2] + " ||| ")
        print(outstr)

        print("- - - - - - - - - - - - - -")

# Helper function for getting valid parameters from user input
def validanswer(question, again_prompt, is_invalid):
    answer = input(question)
    res, inv = is_invalid(answer)
    while (inv):
        print(again_prompt)
        answer = input(question)
        res, inv = is_invalid(answer)
    return res

# Main execution
if __name__ == "__main__":
    if len(sys.argv) == 1:

        state = validanswer("Two-letter state abbreviation:",
        "Unrecognized state abbreviation.",
        lambda x : (x, False) if (x in states) else (None, True))

        question = validanswer("Question number (0 for spreadsheet fill):",
        "Invalid question number.",
        lambda x : (int(x), False) if (int(x) >= 0 and int(x) <= 16) else (None, True))

        if question == 0:
            sheetfill(state)

        else:
            nmatches = validanswer("Number of matches:",
            "Invalid number of matches.",
            lambda x : (int(x), False) if (int(x) >= 0 and int(x) <= 10) else (None, True))

            questionanswer(state, question, nmatches)


    else:
        questionanswer(sys.argv[1], sys.argv[2], 3)
