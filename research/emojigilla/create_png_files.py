# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib2, csv, urllib
from sefaria.model import *
from sefaria.utils.hebrew import strip_cantillation
import re, codecs

def make_soup(url):
    req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
    con = urllib2.urlopen(req)
    html = con.read()
    return BeautifulSoup(html, "html")

def get_image(url):
    soup = make_soup(url)
    return soup.find("div", class_="vendor-image").img["src"]

def lookup_shoresh(w, ref):
    # in both - cant
    # only second - cant
    # only first - nikud
    #remove all non-Hebrew non-nikud characters (including cantillation and sof-pasuk)
    w = strip_cantillation(w, strip_vowels=False)
    w = re.sub(ur"[A-Za-z׃׀־]", u"", w)
    lexicon = "BDB Augmented Strong"
    wf = WordForm().load({"form": w, "refs": re.compile("^" + ref + "$")})
    if wf:
        return map(lambda x: x["headword"], filter(lambda x: x["lexicon"] == lexicon, wf.lookups))


with codecs.open("EmojiGilla Dictionary.csv", 'rb') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',')
    for line in csv_reader:
        hebrew_word = line[0].strip()
        emoji_link = line[2].strip()
        image = get_image(emoji_link)
        perek = line[3].strip()
        pasuk = line[4].strip()
        ref = "Esther {}:{}".format(perek, pasuk)
        shoresh = lookup_shoresh(hebrew_word, ref)
        if shoresh:
            urllib.urlretrieve(image, "./emojis/" + shoresh[0] + ".png")
        else:
            print(hebrew_word)
