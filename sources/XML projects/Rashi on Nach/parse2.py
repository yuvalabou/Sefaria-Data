# -*- coding: utf-8 -*-

__author__ = 'stevenkaplan'
from sources.functions import *
from sefaria.model import *
from data_utilities.XML_to_JaggedArray import XML_to_JaggedArray
from sefaria.helper.schema import *
import bleach

SERVER = "http://draft.sefaria.org"

def reorder_modify(text):
    return bleach.clean(text, strip=True)


def get_dict_of_names(file):
    import csv
    reader = csv.reader(open(file))
    dict = {}
    for row in reader:
        dict[row[0]] = row[1]
    return dict




def change_priority(dict_of_names):
    pass




if __name__ == "__main__":
    #add_term("Preface", u"פתח דבר", "pseudo_toc_categories", "http://localhost:8000")
    #create_schema("Responsa to Chaplains", u"משהו", ["Halakhah"])
    post_info = {}
    post_info["language"] = "en"
    post_info["server"] = SERVER
    allowed_tags = ["book", "intro", "part", "chapter", "p", "ftnote", "title", "ol", "footnotes", "appendix", "h1"]
    allowed_attributes = ["id"]
    p = re.compile("\d+a?\.")

    post_info["versionTitle"] = "Maimonides' Mishneh Torah, edited by Philip Birnbaum, New York, 1967"
    post_info["versionSource"] = "http://primo.nli.org.il/primo_library/libweb/action/dlDisplay.do?vid=NLI&docId=NNL_ALEPH002108864"
    title = "Mishneh Torah"
    file_name = "Judges/Metsudah-Shoftim.xml"


    parser = XML_to_JaggedArray(title, file_name, allowed_tags, allowed_attributes, post_info, change_name=True, image_dir="./images",
                                titled=True, print_bool=True)
    parser.set_funcs(reorder_test=lambda x: x.tag == "h1", reorder_modify=reorder_modify)
    parser.run()

