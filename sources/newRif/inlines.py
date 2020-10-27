import json
import re
import django
django.setup()
from rif_utils import tags_map, path, commentaries, main_mefaresh, maor_godel
from tags_fix_and_check import tags_by_criteria, gem_to_num
from sefaria.utils.talmud import section_to_daf
from data_utilities.util import getGematria
from sefaria.model import *
from sefaria.system.exceptions import InputError

def find_tag_in_bach(masechet, comment):
    letter_tag = tags_map[masechet]['bach_letter'] + r'\(.\)'
    tag = re.findall(letter_tag, comment)
    if tag:
        return gem_to_num(getGematria(tag[0]))
    else:
        print(f'no tag in bach {masechet}: {comment}')

def bach_order(masechet, tags, page):
    old = 0
    gap = 0
    orders = []
    with open(path+f'/commentaries/json/bach_{masechet}.json') as fp:
        data = json.load(fp)
    tags_list = list(tags)
    if (masechet, page) in [('Eruvin', 1), ('Kiddushin', 35)]: #in these page maor and milchemt tags numbered before sg tags
        tags_list = sorted(tags_list, key=lambda x: '6' if x[0]=='3' else x)
    elif (masechet, page) in [('Yevamot', 48)]:
        tags_list = sorted(tags_list, key=lambda x: '6' if x[0]=='4' else x)
    for tag in tags_list:
        new = gem_to_num(getGematria(tags[tag]['original']))
        if old + 1 == new + gap:
            pass
        elif old == new + gap:
            try:
                if find_tag_in_bach(masechet, data[page][old]) == old: #notice first of old is 1 and the data index from 0
                    gap += 1 #bach has double letter, else there're two refs to the same bach
            except IndexError:
                pass #2 refs to the last comment
        elif old + 1 < new + gap:
            for n in range(44):
                try:
                    if find_tag_in_bach(masechet, data[page][old+n]) == new:
                        gap = old + n + 1 - new
                        break
                except IndexError:
                    print(f'not finding comment with gimatric number {new} in bach {masechet} p. {page}. tag: {tag}')
                    break
        elif old - 21 == new + gap:
            gap += 22
        elif masechet == 'Menachot' and new == 1 and old == 2:
            gap = 22
        else:
            print(f'{new} comes after {old} in {masechet} p. {page}')
        old = new + gap
        orders.append(old)
    return orders

for masechet in tags_map:
    if masechet == 'Nedarim': continue
    print(masechet)
    links = []
    with open(path+'/tags/rif_{}.json'.format(masechet)) as fp:
        rif = json.load(fp)
    with open(path+'/tags/mefaresh_{}.json'.format(masechet)) as fp:
        Mmefaresh = json.load(fp)
    with open(path+f'/tags/sg_{masechet}.json') as fp:
        sg = json.load(fp)
    with open(path+f'/tags/maor_{masechet}.json') as fp:
        maor = json.load(fp)
    with open(path+f'/tags/milchemet_{masechet}.json') as fp:
        milchemet = json.load(fp)
    for mefaresh in [1,3,5,7,8,9]:
        c_title = commentaries[str(mefaresh)]['c_title']
        if mefaresh == 9:
            try:
                with open(path+f'/commentaries/json/ravad_{masechet}.json') as fp:
                    ravad = json.load(fp)
            except FileNotFoundError:
                continue
        if mefaresh == 3 and masechet in ['Bava Batra']: #temp
            continue
        print(c_title)

        for page in range(len(rif)):
            tags = tags_by_criteria(masechet, key=lambda x: int(x[1:4])==page, value=lambda x: x['referred text']==mefaresh)
            if mefaresh == 3:
                orders = bach_order(masechet, tags, page)
            for tag in tags:
                if tag[0] == '1':
                    data = rif
                    btext = 'Rif'
                elif tag[0] == '2':
                    data = Mmefaresh
                    btext = main_mefaresh(masechet) + ' on Rif'
                elif tag[0] == '3':
                    data = sg
                    btext = 'Shiltei HaGiborim on Rif'
                elif tag[0] == '4':
                    data = maor
                    btext = f'HaMaor {maor_godel(masechet)[0]} on'
                elif tag[0] == '5':
                    data = milchemet
                    btext = 'Milchemet Hashem on'
                else:
                    print('problem with first digit', tag)
                    continue

                section = int(tag[4:6])
                label = re.sub(r'[^א-ת]', '', tags[tag]['original'])
                order = gem_to_num(getGematria(label))
                if mefaresh == 9:
                    with_tag = []
                    for n, par in enumerate(ravad[page]):
                        if par.startswith(label+'] '):
                            with_tag.append(n)
                    if len(with_tag) == 1:
                        order = with_tag[0] + 1
                        ravad[page][order-1] = ravad[page][order-1].replace(label+'] ', '')
                    else:
                        print(f'tag {tag} with {len(with_tag)} relevant tags in ravad')
                        continue

                if mefaresh == 3: #bach has double letters
                    order = orders.pop(0)

                if int(tag[4:]) > 8999:
                    if page < len(data) and data[page] and tag in data[page][-1]:
                        section = len(data[page]) - 1
                    else:
                        n = 1
                        while n <= page:
                            if data[page-n] and tag in data[page-n][-1]:
                                section = len(data[page-n]) - 1
                                bpage = page - n
                                break
                            n += 1
                    if n > page:
                        print('tag isnt in the expected place', tag)
                        continue
                elif tag in data[page][section]:
                    bpage = page
                else:
                    for n in range(1, 4):#when the tag belongs to continous dh from prev. page. max known is 3
                        if tag in data[page-n][-1]:
                            bpage = page - n
                            section = len(data[bpage]) - 1
                            break
                        if n == 3:
                            print('tag isnt in the expected place', tag)

                data[bpage][section] = data[bpage][section].replace(f'${tag}', f'<i data-commentator="{c_title}" data-label="{label}" data-order="{order}"></i>', 1)
                data[bpage][section] = re.sub('(</i>) +', r'\1', data[bpage][section])
                ref = f'{c_title} {masechet} {section_to_daf(page+1)}:{order}'
                try:
                    if Ref(ref).text('he').text: #did post before
                        links.append({'refs': [f'{btext} {masechet} {section_to_daf(bpage+1)}:{section+1}', ref],
                        'type': 'commentary',
                        'inline_reference': {'data-commentator': c_title, 'data-order': order, 'data-label': label},
                        'generated_by': 'rif inline commentaries'})
                    else:
                        print(f'{tag} ref to null {ref}')
                except InputError: #when running before post
                    links.append({'refs': [f'{btext} {masechet} {section_to_daf(bpage+1)}:{section+1}', ref],
                    'type': 'commentary',
                    'inline_reference': {'data-commentator': c_title, 'data-order': order, 'data-label': label},
                    'generated_by': 'rif inline commentaries'})

        if mefaresh == 9:
            with open(path+'/tags/topost/ravad_{}.json'.format(masechet), 'w') as fp:
                json.dump(ravad, fp)

    with open(path+'/tags/topost/rif_{}.json'.format(masechet), 'w') as fp:
        json.dump(rif, fp)
    with open(path+'/tags/topost/mefaresh_{}.json'.format(masechet), 'w') as fp:
        json.dump(Mmefaresh, fp)
    with open(path+'/tags/topost/SG_{}.json'.format(masechet), 'w') as fp:
        json.dump(sg, fp)
    with open(path+'/tags/topost/inline_links_{}.json'.format(masechet), 'w') as fp:
        json.dump(links, fp)
    with open(path+'/tags/topost/maor_{}.json'.format(masechet), 'w') as fp:
        json.dump(maor, fp)
    with open(path+'/tags/topost/milchemet_{}.json'.format(masechet), 'w') as fp:
        json.dump(milchemet, fp)
