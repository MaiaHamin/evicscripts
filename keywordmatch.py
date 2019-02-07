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
states = ["AL", "FL", "LA", "MD", "NV", "SC", "TX"]
# data from Jon Mayer?
allfilenames = [
["AlabamaProperty.txt", "AlabamaPropertyA.txt"],
["FLLaws.txt", "FLLaws2.txt", "FLResTen.txt", "FLEject.txt", "FL3.txt"],
["LAEvicting.txt", "LASaleEviction.txt"],
["MarylandLandlordsTenants.txt"],
["NVLaws.txt", "NVLaws2.txt"],
["SCEjectment.txt", "SCLandlordTenGen.txt", "SCResLandlordTen.txt", "SCLeaseholdEstates.txt"],
["TexasProperty.txt", "TexasTwo.txt"]]
prefixes = [
"Ala.Code 1975 §",
"West’s F.S.A. §",
"LSA-C.C.P.",
"MD Code, Real Property, §",
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
    for key in keywords:
        for k in key.split():
            split_keys.append(k)
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
                words = w_tokenize(line)
                seen_words = []
                for word in words:
                    if word in split_keys:
                        text = line
                        sec = last_sec
                        if line[0] == "(":
                            sec += " " + line[1]
                            text = line[4:]
                        matches[sec] = text
                        if word not in seen_words:
                            if word in count_dict:
                                count_dict[word] += 1
                            else:
                                count_dict[word] = 1
                            seen_words.append(word)
    return matches, count_dict, line_count

def rankmatches(keywords, count_dict, line_count, matches, top_n, g_n):
    wrst_bst_keys = []
    for (sec, text) in matches.items():
        num_matches = 0.
        words = w_tokenize(text)
        length = float(len(words))
        if (length > 20):
            prevwords = []
            for word in words:
                prevwords.insert(0, word)
                prevwords = prevwords[:g_n]
                n_perms = []
                for i in range(min(len(prevwords), g_n)):
                    n_perms.append(" ".join(prevwords[:i]))
                for n_gram in n_perms:
                    if n_gram in keywords:
                        num_matches += (1. / np.log(length)) * np.log (line_count / count_dict[word]) * len(n_gram)
            wrst_bst_keys.append((sec, num_matches))
            wrst_bst_keys.sort(key=lambda k: k[1], reverse=True)
            wrst_bst_keys = wrst_bst_keys[:min(len(wrst_bst_keys), top_n)]

    return wrst_bst_keys

if __name__ == "__main__":
    questions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    startrow = 0
    for state in states:
        startcol = 3
        state_ind = startrow
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
            ranked = rankmatches(keywords, count_dict, line_count, matches, 5, 4)
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
