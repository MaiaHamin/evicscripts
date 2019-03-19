#-*- encoding: utf-8 -*-
import csv
import nltk
import re
import os
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
states = ["AK", "AL", "AR", "AZ", "CA", "CO", "DC", "DE", "FL", "IA", "ID", "IL", "IN", 
"KS", "LA", "MA", "MD", "ME", "MI", "MO", "MS", "MT", "ND", "NJ", "NM", "NV", "NY", "OH", 
"OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "VT", "WA", "WI", "WV", "WY"]

allfilenames=[]
for s in states:
	statefiles=[]
	for filename in os.listdir("/Volumes/eviction/Intern Dropbox/Landlord_Tenant_Project/Text/"+s):
		if filename.endswith(".txt"):
			statefiles.append(filename)
	allfilenames.append(statefiles)

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