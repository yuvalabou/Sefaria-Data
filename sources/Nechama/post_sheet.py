# -*- coding: utf-8 -*-
"""
Post a sheet form the local enviornment to a remote enviornment, using an API Key.
"""
import django
django.setup()
import urllib2
import requests

from sefaria.system.database import db
from sefaria.sheets import get_sheet
from sources.functions import post_sheet, http_request
from sources.local_settings import *

GET_SERVER = "http://nechama.sandbox.sefaria.org"
# GET_SERVER = "http://qanechama.sandbox.sefaria.org"
# GET_SERVER = "http://localhost:8000"

POST_SERVER = "http://nechama.sandbox.sefaria.org"
# POST_SERVER = "http://qnechama.sandbox.sefaria.org"
# POST_SERVER = "http://localhost:8000

get_server = GET_SERVER
post_server = POST_SERVER


def change_sheet(this_sheet, del_tags=[], add_tags=[]):
    # deal with tags
    for tag in this_sheet[u'tags']:
        if isinstance(tag, int) or tag.isdigit():
            # todo: deal with the pdf link
            this_sheet['summary'] = this_sheet['summary'] + u" http://www.nechama.org.il/pdf/{}.pdf".format(tag)
            if "int_tag" in del_tags:
                this_sheet[u'tags'].remove(tag)
        if (tag in del_tags):
            this_sheet[u'tags'].remove(tag)
    this_sheet[u'tags'].extend(add_tags)
    # deal with owner todo: make this work also throw the api post
    this_sheet["owner"] = 51461
    return this_sheet


# create this mapping on the POST_SERVER via map_ssn_url.py on the correct db
map_ssn_url = {
    1: 152692, 2: 151103, 3: 151180, 4: 151181, 5: 152693, 6: 152694, 7: 151184, 8: 151185, 9: 151186, 10: 152695, 11: 151186, 12: 151189, 13: 151190, 14: 151191, 15: 151192, 16: 151193, 17: 151194, 18: 152696, 19: 151196, 20: 151197, 21: 151187, 22: 151199, 23: 151200, 24: 151201, 25: 151202, 26: 151203, 27: 152663, 28: 151205, 29: 152697, 30: 152698, 31: 151188, 32: 151209, 33: 151210, 34: 152699, 35: 151212, 36: 152700, 37: 152701, 38: 152702, 39: 151216, 40: 151217, 41: 151189, 42: 151219, 43: 151220, 44: 152703, 45: 151222, 46: 151223, 47: 152704, 48: 152705, 49: 151226, 50: 152706, 51: 151190, 52: 151229, 53: 151230, 54: 151231, 55: 151232, 56: 152707, 57: 152708, 58: 151235, 59: 151236, 60: 152148, 61: 151191, 62: 151239, 63: 152709, 64: 151241, 65: 151242, 67: 151243, 68: 151244, 70: 151245, 71: 151192, 72: 152710, 73: 151248, 74: 151249, 75: 151250, 76: 151251, 77: 151252, 78: 151253, 79: 151254, 80: 151255, 81: 151193, 82: 151257, 83: 151258, 84: 151259, 85: 151260, 86: 152711, 87: 152712, 88: 151263, 89: 152713, 90: 151265, 91: 152714, 92: 151196, 93: 151268, 94: 151269, 95: 152715, 96: 151271, 97: 151272, 98: 151273, 99: 151274, 100: 152716, 101: 151276, 102: 151197, 103: 152717, 104: 152718, 105: 151280, 106: 152719, 107: 152720, 108: 151283, 109: 152721, 110: 151285, 111: 152722, 112: 151198, 113: 151288, 114: 152723, 115: 152662, 116: 151291, 117: 152724, 118: 152725, 119: 151294, 120: 151295, 121: 151296, 122: 151199, 123: 152726, 124: 151299, 125: 152727, 126: 151301, 127: 152728, 128: 151303, 129: 151304, 130: 151305, 131: 151306, 132: 151200, 133: 151308, 134: 152729, 135: 152730, 136: 151311, 137: 151312, 138: 151313, 139: 152731, 140: 151315, 141: 151316, 142: 151201, 143: 152732, 144: 152733, 145: 152734, 146: 152735, 147: 151322, 148: 151323, 149: 152736, 150: 151325, 151: 152737, 152: 151202, 153: 151328, 154: 151329, 155: 151330, 156: 151331, 157: 151332, 158: 151333, 159: 151334, 160: 151335, 161: 152738, 162: 151203, 164: 151338, 165: 152739, 166: 151340, 167: 151341, 168: 151342, 169: 151108, 170: 152740, 171: 151345, 172: 151204, 173: 152741, 174: 151348, 175: 152742, 176: 152743, 177: 152744, 178: 151352, 179: 152745, 180: 151354, 181: 152746, 182: 151205, 183: 151357, 184: 152747, 185: 152748, 186: 152749, 187: 151361, 188: 151362, 189: 151363, 190: 152750, 191: 152751, 192: 151206, 193: 151367, 194: 152752, 195: 151369, 196: 151370, 197: 152753, 198: 152754, 199: 151373, 200: 152755, 201: 152756, 202: 151207, 203: 151377, 204: 151378, 206: 151379, 207: 151380, 208: 151381, 209: 152757, 210: 151383, 211: 151384, 212: 152758, 213: 152759, 214: 151387, 215: 152760, 216: 151389, 217: 151390, 218: 152761, 219: 151392, 220: 151393, 221: 152762, 222: 151209, 223: 152763, 224: 151397, 225: 151398, 226: 151399, 227: 151400, 228: 151401, 229: 151402, 230: 151403, 231: 151404, 232: 152764, 233: 151406, 234: 151407, 235: 151408, 236: 152765, 237: 151410, 238: 152766, 239: 151412, 240: 151413, 241: 151414, 242: 151211, 243: 151416, 244: 151417, 245: 151418, 246: 152767, 247: 151420, 248: 151421, 249: 151422, 250: 152768, 251: 152769, 252: 151212, 253: 151426, 254: 151427, 255: 152770, 256: 151429, 257: 152771, 258: 152772, 259: 153142, 260: 151433, 261: 151434, 262: 151213, 263: 151436, 264: 151437, 265: 151438, 266: 151439, 267: 151440, 268: 151441, 269: 151442, 270: 151443, 271: 152773, 272: 151214, 273: 152774, 274: 151447, 275: 151448, 276: 151449, 277: 151450, 278: 151746, 279: 151452, 280: 151453, 281: 151454, 282: 151215, 283: 152775, 284: 151457, 285: 151458, 286: 151459, 287: 152776, 288: 152777, 289: 151462, 290: 151463, 291: 151464, 292: 151216, 293: 151466, 294: 151467, 295: 152778, 296: 151469, 297: 151470, 298: 151471, 299: 151472, 300: 151473, 301: 152779, 302: 152780, 303: 151476, 304: 151477, 305: 151478, 306: 151479, 307: 151480, 308: 151481, 309: 151482, 310: 151483, 311: 151484, 312: 151218, 313: 152781, 314: 151487, 315: 151488, 316: 151489, 317: 152782, 318: 151491, 319: 151492, 320: 151493, 321: 151494, 322: 152783, 323: 151496, 324: 151497, 325: 152784, 326: 151499, 327: 151500, 328: 151501, 329: 151502, 330: 151503, 331: 152785, 332: 151220, 333: 151506, 334: 151507, 335: 152786, 336: 151509, 337: 151510, 338: 151511, 339: 152787, 340: 152788, 341: 151514, 342: 151221, 343: 151516, 344: 151517, 345: 151518, 346: 151519, 347: 152789, 348: 151521, 349: 151522, 350: 151523, 351: 152790, 352: 152791, 353: 152792, 354: 151527, 355: 151528, 356: 152793, 357: 151530, 358: 151531, 359: 151532, 360: 151533, 361: 152794, 362: 151223, 363: 151536, 364: 151537, 365: 152795, 366: 151539, 367: 151540, 368: 151541, 369: 151542, 370: 151543, 371: 152796, 372: 152797, 373: 151546, 374: 151547, 375: 151548, 376: 152798, 377: 151550, 378: 151551, 379: 151552, 380: 151553, 381: 151554, 382: 151225, 383: 151556, 384: 151557, 385: 151558, 386: 151559, 387: 152799, 388: 151561, 389: 151562, 390: 151563, 391: 152800, 392: 151226, 393: 151566, 394: 152801, 395: 151568, 396: 151569, 397: 151570, 398: 152802, 399: 151572, 400: 151573, 401: 151574, 402: 151227, 403: 151576, 404: 151577, 405: 151578, 406: 151579, 407: 151580, 408: 151581, 409: 151582, 410: 151583, 411: 151584, 412: 151228, 413: 151586, 414: 152803, 415: 151588, 416: 151589, 417: 151590, 418: 151591, 419: 151592, 420: 152804, 421: 151594, 422: 151229, 423: 152805, 424: 151597, 425: 152806, 426: 151599, 427: 151600, 428: 152807, 429: 151602, 430: 152808, 431: 151604, 432: 151230, 433: 152809, 434: 151607, 435: 151608, 436: 152810, 437: 151610, 438: 151611, 439: 151612, 440: 151613, 441: 151614, 442: 151231, 443: 151616, 444: 151617, 445: 151618, 446: 151619, 447: 152811, 448: 151621, 449: 151622, 450: 151623, 451: 152812, 452: 152813, 453: 152814, 454: 151627, 455: 152815, 456: 152816, 457: 152817, 458: 151631, 459: 152818, 460: 152819, 461: 152820, 462: 152821, 463: 152822, 464: 151637, 465: 151638, 466: 152823, 467: 151640, 468: 152824, 469: 152825, 470: 152826, 471: 152827, 472: 152828, 473: 151646, 474: 152829, 475: 151648, 476: 152830, 477: 152831, 478: 152832, 479: 152833, 480: 151653, 481: 152834, 482: 152835, 483: 152836, 484: 151657, 485: 152837, 486: 152838, 487: 152839, 488: 152840, 489: 151662, 490: 152841, 491: 152842, 492: 151236, 493: 151666, 494: 152843, 495: 152844, 496: 152845, 497: 152846, 498: 152847, 499: 152848, 500: 152849, 501: 152850, 502: 152851, 503: 152852, 504: 152853, 505: 152854, 506: 152855, 507: 152856, 508: 152857, 509: 151682, 510: 152858, 511: 152859, 512: 152860, 513: 151686, 514: 151687, 515: 152861, 516: 152862, 517: 151690, 518: 151691, 519: 152863, 520: 151693, 521: 151694, 522: 152864, 523: 151696, 524: 152865, 525: 152866, 526: 152867, 527: 152868, 528: 152869, 529: 151702, 530: 151703, 531: 151704, 532: 152870, 533: 151706, 534: 152871, 535: 152872, 536: 151709, 537: 151710, 538: 151711, 539: 152873, 540: 152874, 541: 152875, 542: 152876, 543: 152877, 544: 151717, 545: 151718, 546: 152878, 547: 152879, 548: 151721, 549: 151722, 550: 152880, 551: 152881, 552: 151242, 553: 151726, 554: 151727, 555: 151729, 556: 152882, 557: 152883, 558: 151732, 559: 152884, 560: 152885, 561: 151735, 562: 151243, 563: 151738, 564: 151739, 565: 151740, 566: 152886, 567: 152887, 568: 152888, 569: 151744, 570: 151745, 571: 151747, 572: 152889, 573: 151749, 574: 151750, 575: 152890, 576: 152891, 577: 151753, 579: 152892, 580: 151755, 581: 152893, 582: 151245, 583: 152894, 584: 152895, 585: 152896, 586: 152897, 587: 152898, 588: 152899, 589: 152900, 590: 151765, 591: 152901, 592: 152902, 593: 152903, 594: 152904, 595: 152905, 596: 151771, 597: 152906, 598: 151773, 599: 152907, 600: 152908, 601: 152909, 602: 152910, 603: 152911, 604: 151779, 605: 151780, 606: 152912, 607: 151782, 608: 151783, 609: 152913, 610: 151785, 611: 151786, 612: 152914, 613: 151788, 614: 151789, 615: 151790, 616: 151791, 617: 152915, 618: 151793, 619: 151794, 620: 152916, 621: 152917, 622: 152918, 623: 152919, 624: 152920, 625: 151800, 626: 151801, 628: 152921, 629: 151803, 630: 151804, 631: 151805, 632: 152922, 633: 152923, 634: 152924, 635: 152925, 636: 151810, 637: 152926, 638: 152927, 639: 152928, 640: 151814, 641: 151815, 642: 152929, 643: 151817, 644: 152930, 645: 152931, 646: 152932, 647: 152933, 648: 152934, 649: 152935, 650: 152936, 651: 152937, 652: 152938, 653: 152939, 654: 152940, 655: 152941, 656: 152942, 657: 152943, 658: 151832, 659: 152944, 660: 152945, 661: 152946, 662: 151253, 663: 151837, 664: 152947, 665: 151839, 666: 152948, 667: 151841, 668: 152949, 669: 151843, 670: 151844, 671: 152951, 672: 151254, 673: 152952, 674: 151848, 675: 152953, 676: 151850, 677: 152954, 678: 151852, 679: 152955, 680: 151854, 681: 152956, 682: 152957, 683: 152958, 684: 152959, 685: 151859, 686: 151860, 687: 152960, 688: 152961, 689: 151863, 690: 152962, 691: 152963, 692: 152964, 693: 152965, 694: 152966, 695: 151869, 696: 152967, 697: 152968, 698: 152969, 699: 152970, 700: 152971, 701: 152972, 702: 151257, 703: 152973, 704: 152974, 705: 151879, 706: 152975, 707: 151881, 708: 151882, 709: 151883, 710: 151884, 711: 152976, 712: 152977, 713: 152978, 714: 152979, 715: 152980, 716: 152981, 717: 152982, 718: 152983, 719: 151893, 720: 152984, 721: 152985, 722: 151259, 723: 151897, 724: 151898, 725: 151899, 726: 152986, 727: 152987, 728: 151902, 729: 152988, 730: 152989, 731: 152990, 732: 152991, 733: 152992, 734: 152993, 735: 152994, 736: 151910, 737: 152995, 738: 151912, 739: 152996, 740: 152997, 741: 152998, 742: 151261, 743: 152999, 744: 151918, 745: 153000, 746: 151920, 747: 153001, 748: 153002, 749: 153003, 750: 151924, 751: 153004, 752: 153005, 753: 153006, 754: 153007, 755: 151929, 756: 153008, 757: 151931, 758: 153009, 759: 153010, 760: 153011, 761: 151935, 762: 153012, 763: 153013, 764: 153014, 765: 153015, 766: 153016, 767: 153017, 768: 153018, 769: 151943, 770: 153019, 771: 151945, 772: 153020, 773: 153021, 774: 153022, 775: 151949, 776: 153023, 777: 151951, 778: 153024, 779: 153025, 780: 153026, 781: 153027, 782: 151265, 783: 151957, 784: 153028, 785: 151959, 786: 151960, 787: 153029, 788: 153030, 789: 153031, 790: 153032, 791: 151965, 792: 153033, 793: 151967, 794: 153034, 795: 153035, 796: 151970, 797: 153036, 798: 151972, 799: 151973, 800: 153037, 801: 153038, 802: 153039, 803: 153040, 804: 151978, 805: 151979, 806: 153041, 807: 153042, 808: 151982, 809: 153043, 810: 151984, 811: 151985, 812: 153044, 813: 151987, 814: 151988, 815: 153045, 816: 151990, 817: 153046, 818: 153047, 819: 151993, 820: 153048, 821: 153049, 822: 153050, 823: 153051, 824: 151998, 825: 153052, 826: 153053, 827: 153054, 828: 152002, 829: 153055, 830: 153056, 831: 152005, 832: 153057, 833: 153058, 834: 153059, 835: 152009, 836: 152010, 837: 152011, 838: 152012, 839: 153060, 840: 153061, 841: 153062, 842: 153063, 843: 153064, 844: 153065, 845: 152019, 846: 153066, 847: 153067, 848: 152022, 849: 152023, 850: 153068, 851: 152025, 852: 151272, 853: 153069, 854: 153070, 855: 152029, 856: 153071, 857: 152031, 858: 152032, 859: 153072, 860: 152034, 861: 152035, 862: 153073, 863: 152037, 864: 153074, 865: 153075, 866: 152040, 867: 152041, 868: 153076, 869: 152043, 870: 153077, 871: 153078, 872: 153079, 873: 153080, 874: 152048, 875: 153081, 876: 152050, 877: 153082, 878: 152052, 879: 153083, 880: 153084, 881: 153085, 882: 151275, 883: 153086, 884: 152058, 885: 153087, 886: 153088, 887: 153089, 888: 153090, 889: 153091, 890: 152064, 891: 152065, 892: 153092, 893: 153093, 894: 152068, 895: 153094, 896: 153095, 897: 152071, 898: 152072, 899: 152073, 900: 153096, 901: 152075, 902: 153097, 903: 153098, 904: 152078, 905: 153099, 906: 152080, 907: 153100, 908: 152082, 909: 152083, 910: 152084, 911: 153101, 912: 151278, 913: 152087, 914: 153102, 915: 152089, 916: 153103, 917: 152091, 918: 153104, 919: 153105, 920: 153106, 921: 152095, 922: 153107, 923: 152097, 924: 153108, 925: 153109, 926: 152100, 927: 153110, 928: 153111, 929: 153112, 930: 153113, 931: 153114, 932: 153115, 933: 153116, 934: 153117, 935: 153118, 936: 153119, 937: 152111, 938: 152112, 939: 153120, 940: 152114, 941: 153121, 942: 151281, 943: 152117, 944: 152118, 945: 153122, 946: 152120, 947: 152121, 948: 153123, 949: 152123, 950: 153124, 951: 153125, 952: 151282, 953: 152127, 954: 153126, 955: 152129, 956: 152149, 957: 153127, 958: 153128, 959: 152152, 960: 153129, 961: 153130, 962: 153131, 963: 152156, 964: 153132, 965: 152158, 966: 153133, 967: 153134, 968: 152161, 969: 153135, 970: 152163, 971: 152164, 972: 151284, 973: 153136, 974: 152167, 975: 153137, 976: 153139, 977: 152170, 978: 152171, 979: 152172, 980: 152173, 981: 152174, 982: 151285, 983: 152176, 984: 152177, 985: 152178, 986: 152179, 988: 152180, 989: 152181, 990: 152182, 991: 152183, 992: 151286, 993: 152185, 994: 152186, 995: 152187, 996: 152188, 997: 152189, 998: 152190, 999: 152191, 1000: 152192, 1001: 152193, 1002: 152674, 1003: 152195, 1004: 152196, 1005: 152197, 1006: 152198, 1007: 152199, 1008: 152200, 1009: 152201, 1010: 152202, 1011: 152203, 1012: 151288, 1013: 152205, 1014: 152206, 1015: 152207, 1016: 152208, 1017: 152209, 1018: 152210, 1019: 152211, 1020: 152212, 1021: 152213, 1022: 151289, 1023: 152215, 1024: 152216, 1025: 152217, 1026: 152218, 1027: 152219, 1028: 152220, 1029: 152221, 1030: 152222, 1031: 152223, 1032: 151344, 1033: 152225, 1034: 152226, 1035: 152227, 1036: 152228, 1037: 152229, 1038: 152230, 1039: 152231, 1040: 152232, 1041: 152233, 1042: 151291, 1043: 152235, 1044: 152236, 1045: 152237, 1046: 152238, 1047: 152239, 1048: 152240, 1049: 152241, 1050: 152242, 1051: 152243, 1052: 151292, 1053: 152245, 1054: 152246, 1055: 152247, 1056: 152248, 1057: 152249, 1058: 152250, 1059: 152251, 1060: 152252, 1061: 152253, 1062: 151293, 1063: 152255, 1064: 152256, 1065: 152257, 1066: 152258, 1067: 152259, 1068: 152260, 1069: 152261, 1070: 152262, 1071: 152263, 1072: 151294, 1073: 152265, 1074: 152266, 1075: 151178, 1076: 152267, 1077: 152268, 1078: 152269, 1079: 152270, 1080: 152271, 1081: 152272, 1082: 151295, 1083: 152274, 1084: 152275, 1085: 152276, 1086: 152277, 1087: 152278, 1088: 152279, 1089: 152280, 1090: 152281, 1091: 152282, 1092: 151296, 1093: 152284, 1094: 152285, 1095: 152286, 1096: 152287, 1097: 152288, 1098: 152289, 1099: 152290, 1100: 152291, 1101: 152292, 1102: 151297, 1103: 152294, 1104: 152295, 1105: 152296, 1106: 152297, 1107: 152298, 1108: 152299, 1109: 152300, 1110: 152301, 1111: 152302, 1112: 151298, 1113: 152304, 1114: 152305, 1115: 152306, 1116: 152307, 1117: 152308, 1118: 152309, 1119: 152310, 1120: 152311, 1121: 152312, 1122: 151299, 1123: 152314, 1124: 152315, 1125: 152316, 1126: 152317, 1127: 152318, 1128: 152319, 1129: 152320, 1130: 152321, 1131: 152322, 1132: 151300, 1133: 152324, 1134: 152325, 1135: 152326, 1136: 152327, 1137: 152328, 1138: 152329, 1139: 152330, 1140: 152331, 1141: 152332, 1142: 151301, 1143: 152334, 1144: 151347, 1145: 152336, 1146: 152337, 1147: 152338, 1148: 152339, 1149: 152340, 1150: 152341, 1151: 152342, 1152: 151302, 1153: 152344, 1154: 152345, 1155: 152346, 1156: 152347, 1157: 152348, 1158: 152349, 1159: 152350, 1160: 152351, 1161: 152352, 1162: 151303, 1163: 151180, 1164: 152354, 1165: 152355, 1166: 152356, 1167: 152357, 1168: 152358, 1169: 152359, 1170: 152360, 1171: 152361, 1172: 151304, 1173: 152363, 1174: 152364, 1175: 152365, 1176: 152366, 1177: 152367, 1178: 152368, 1179: 152369, 1180: 152370, 1181: 152371, 1182: 151305, 1183: 152373, 1184: 152374, 1185: 152375, 1186: 152376, 1187: 152377, 1188: 152378, 1189: 152379, 1190: 152380, 1191: 152381, 1192: 151306, 1193: 152383, 1194: 152384, 1195: 152385, 1196: 152386, 1197: 152387, 1198: 152388, 1199: 152389, 1200: 152390, 1201: 152391, 1202: 151307, 1203: 152393, 1204: 152394, 1205: 152395, 1206: 152396, 1207: 152397, 1208: 152398, 1209: 152399, 1210: 152400, 1211: 152401, 1212: 151308, 1213: 152403, 1214: 152404, 1215: 152405, 1216: 152406, 1217: 152407, 1218: 152408, 1219: 152409, 1220: 152410, 1221: 152411, 1222: 151309, 1223: 152413, 1224: 152414, 1225: 152415, 1226: 152416, 1227: 152417, 1228: 152418, 1229: 152419, 1230: 152420, 1231: 152421, 1232: 151310, 1233: 152423, 1234: 152424, 1235: 152425, 1236: 152426, 1237: 152427, 1238: 152428, 1239: 152429, 1240: 152430, 1241: 152431, 1243: 152432, 1244: 152433, 1245: 152434, 1246: 152435, 1247: 152436, 1248: 152437, 1249: 152438, 1250: 152439, 1251: 152440, 1252: 151311, 1253: 152442, 1254: 152443, 1255: 152444, 1256: 152445, 1257: 152446, 1258: 152447, 1259: 152448, 1260: 152449, 1261: 152450, 1262: 151312, 1263: 152452, 1264: 152453, 1265: 152454, 1266: 152455, 1267: 152456, 1268: 152457, 1269: 152458, 1270: 152459, 1271: 152460, 1272: 151313, 1273: 152462, 1274: 152463, 1275: 152464, 1276: 152465, 1277: 152466, 1278: 152467, 1279: 152468, 1280: 152469, 1281: 152470, 1282: 151314, 1283: 152472, 1284: 152473, 1285: 152474, 1286: 152475, 1287: 152476, 1288: 152477, 1289: 152478, 1290: 152479, 1291: 152480, 1292: 151315, 1293: 152482, 1294: 152483, 1295: 152484, 1296: 152485, 1297: 152486, 1298: 152487, 1299: 152488, 1300: 152489, 1301: 152490, 1302: 151316, 1303: 152492, 1304: 152493, 1305: 152494, 1306: 152495, 1307: 152496, 1308: 152497, 1309: 152498, 1310: 152499, 1311: 152500, 1312: 151317, 1313: 152502, 1314: 152503, 1315: 152504, 1316: 152505, 1317: 152506, 1318: 152507, 1319: 152508, 1320: 151179, 1321: 152509, 1322: 151318, 1323: 152511, 1324: 152512, 1325: 152513, 1326: 152514, 1327: 152515, 1328: 152516, 1329: 152517, 1330: 152518, 1331: 152519, 1332: 151319, 1333: 152521, 1334: 152522, 1335: 152523, 1336: 152524, 1337: 152525, 1338: 152526, 1339: 152527, 1340: 152528, 1341: 152529, 1342: 151320, 1343: 152531, 1344: 152532, 1345: 152533, 1346: 152534, 1348: 152535, 1349: 152536, 1350: 152537, 1351: 151346, 1352: 151321, 1353: 152540, 1354: 152541, 1355: 152542, 1356: 152543, 1357: 152544, 1358: 152545, 1359: 152546, 1360: 152547, 1361: 152548, 1362: 151322, 1363: 152550, 1364: 152551, 1365: 152552, 1366: 152553, 1367: 152554, 1368: 152555, 1369: 152556, 1370: 152557, 1371: 152558, 1372: 151323, 1373: 152560, 1374: 152561, 1375: 152562, 1376: 152563, 1377: 152564, 1378: 152565, 1379: 152566, 1380: 152567, 1381: 152568, 1382: 151324, 1383: 152570, 1384: 152571, 1385: 152572, 1386: 152573, 1387: 152574, 1388: 152575, 1389: 152576, 1390: 152577, 1391: 152578, 1392: 151325, 1393: 152580, 1394: 152581, 1395: 152582, 1396: 152583, 1397: 152584, 1398: 152585, 1399: 152586, 1400: 152587, 1401: 152588, 1402: 151326, 1403: 152688, 1404: 152669, 1405: 152592, 1406: 152593, 1407: 152594, 1408: 152595, 1409: 152596, 1410: 152597, 1411: 152598, 1412: 151327, 1413: 152600, 1414: 152601, 1415: 152602, 1416: 152603, 1417: 152604, 1418: 152605, 1419: 152606, 1420: 152607, 1421: 152608, 1422: 151328, 1423: 152610, 1424: 152611, 1425: 152612, 1426: 152613, 1427: 152614, 1428: 152615, 1429: 152616, 1430: 152617, 1431: 152618, 1432: 151329, 1433: 152620, 1434: 152621, 1435: 152622, 1436: 152623, 1437: 152624, 1438: 152625, 1439: 152626, 1440: 152660, 1441: 152628, 1442: 151330, 1443: 152630, 1444: 152631, 1445: 152632, 1446: 152633, 1447: 152634, 1448: 152635, 1449: 152636, 1450: 152637, 1451: 152638, 1452: 151331, 1455: 152640, 1456: 152641, 1457: 152642, 1458: 152643, 1459: 152644, 1461: 152645, 1464: 152646, 1465: 152647, 1466: 152648, 1467: 152649, 1468: 152650, 1469: 152651, 1472: 151332, 1473: 152653, 1474: 152654, 1478: 152655}
ssn_sheets = [661]

post_sheet_id = map_ssn_url[ssn_sheets[0]]  # the latest sheet with that ssn number we want to repost over
get_sheet_id = 151835  # can also be from a ssn mapping from the correct server the fixed sheet that was created (sometimes from the old sheet itself), need to knkow it

url = get_server + "/api/sheets/{}".format(get_sheet_id)
got = http_request(url, body={"apikey": API_KEY}, method="GET")

changed = change_sheet(got, add_tags=[])  # add_tags=['RePost']
del changed['_id']
changed['id'] = post_sheet_id
post_sheet(changed, server=POST_SERVER)

## post them over themself (for the sheet to sheet linking process)

# sheets = [map_ssn_url[x] for x in ssn_sheets]
# for ssn in sheets_ssn:
#     got = get_sheet(sheet[u'id'])
#     url = SEFARIA_SERVER + "/api/sheets/{}".format(sheet_id)
#     got = http_request(url, body={"apikey": API_KEY}, method="GET")
#     changed = change_sheet(got, add_tags=[])
#     changed['id'] = post_ssn_map[ssn]
#     del changed['_id']
#     post_sheet(changed, server=SEFARIA_SERVER)
# pass