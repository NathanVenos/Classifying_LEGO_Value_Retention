"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
LEGO HELPER
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import requests
import time
import bs4 as bs
import numpy as np


BASE_URL = 'https://brickset.com'
BROWSE_URL = 'https://brickset.com/browse/sets'


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
BRICKSET FUNCTIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


# manager function to get all pages of a year
def get_year(year_tx):

    print(f'year: {year_tx}')
    page_no = 0
    pages_all = False
    url_ls = []

    while (pages_all == False):
        
        # stop the loop when the page returns empty

        page_no += 1
        url_page_ls = get_year_paginated(year_tx, page_no)

        if len(url_page_ls) == 0:
            pages_all = True
            print(f'last page: {page_no -1}')

        else:
            url_ls += url_page_ls            

    return url_ls


# endpoint for getting all set urls of parameter year
def get_year_paginated(year_tx, page_no):

    if page_no % 10 == 0:
        print(f'page no: {page_no}')   

    # get the full page html

    if page_no == 1:
        endpoint_url = f'{BASE_URL}/sets/year-{year_tx}'
    else:
        endpoint_url = f'{BASE_URL}/sets/year-{year_tx}/page-{page_no}'

    try:
        response = requests.get(endpoint_url)
        time.sleep(.5)
        # raise an exception based on status code
        response.raise_for_status()
    except Exception as err:
        print(f'Endpoint: {endpoint_url}') 
        print(f'Error: {err}') 
        raise err

    page_sp = bs.BeautifulSoup(response.text, 'html.parser')

    # loop through articles to get urls
    
    url_ls = []
    article_sp = page_sp.find_all('article')
    #print(f'articles found: {len(article_sp)}')

    if len(article_sp) == 0:
        return []

    for artc in article_sp:
        div_meta_sp = artc.find_all('div', {'class': 'meta'})[0]
        h1_sp = div_meta_sp.find_all('h1')[0]
        link_sp = h1_sp.find_all('a')[0]
        text_ls = link_sp.text.split(':')

        # some sets (books, gear) don't have a set-no

        if len(text_ls) == 2:
            set_dx = {
                'set_no': text_ls[0].strip(),
                'name': text_ls[1].strip(),
                'url': link_sp['href'],
            }
        else:
            set_dx = {
                'set_no': '0000',
                'name': text_ls[0].strip(),
                'url': link_sp['href'],
            }

        url_ls.append(set_dx)

    return url_ls


# get all fields for the parameter set
def get_set_data(set_url):

    # get the full page html

    endpoint_url = f'{BASE_URL}{set_url}'

    try:
        response = requests.get(endpoint_url)
        time.sleep(.5)
        # raise an exception based on status code
        response.raise_for_status()
    except Exception as err:
        print(f'Endpoint: {endpoint_url}') 
        print(f'Error: {err}') 
        raise err

    page_sp = bs.BeautifulSoup(response.text, 'html.parser')

    # get the data fields

    set_dx = {
        'set_no': None,
        'name': None,
        'url': set_url, 
        'set_type': None,
        'theme_group': None,
        'theme': None,
        'subtheme': None,
        'year': None,
        'tags': None,
        'piece_cnt': None,
        'minifig_cnt': 0,
        'inventory_url': None,
        'minifig_url': None, 
        'store_price': None,
        'current_price': None,
        'packaging': None,
        'notes': None,
        'rating_value': None,
        'rating_votes': None,
    }

    try:
        section_sp = page_sp.find_all('section', {'class': 'featurebox'})[0]
        section_dl_sp = page_sp.find_all('dl')[0].children
    except Exception as ex:
        return {}

    #print(f'section children: {len(list(section_dl_sp))}')    # this consumes the iterator
    #print(type(section_dl_sp))

    while (True):
        # loop stops when iterator throws error at the end of list
        try:
            # not sure why blank spaces are in iterator as NavigableString
            navstring_skip = next(section_dl_sp)
            field_name_sp = next(section_dl_sp)
            navstring_skip = next(section_dl_sp)
            field_value_sp = next(section_dl_sp)
            #print(field_name_sp.text)
            #print(field_value_sp.text)
        except StopIteration:
            break
        except Exception as ex:
            print(f'Field Error: {endpoint_url}')
            raise ex

        field_name = field_name_sp.text

        if field_name == 'Set number':
            set_dx['set_no'] = field_value_sp.text

        elif field_name == 'Name':
            set_dx['name'] = field_value_sp.text

        elif field_name == 'Set type':
            set_dx['set_type'] = field_value_sp.text

        elif field_name == 'Theme group':
            set_dx['theme_group'] = field_value_sp.text

        elif field_name == 'Theme':
            set_dx['theme'] = field_value_sp.text

        elif field_name == 'Subtheme':
            set_dx['subtheme'] = field_value_sp.text

        elif field_name == 'Year released':
            set_dx['year'] = field_value_sp.text

        elif field_name == 'Tags':
            tags_ls = []
            tags_sp = field_value_sp.find_all('a')
            for tag_a in tags_sp:
                tags_ls.append(tag_a.text.strip())
            set_dx['tags'] = ', '.join(tags_ls) 

        elif field_name == 'Pieces':
            #print(field_value_sp)
            set_dx['piece_cnt'] = field_value_sp.text
            link_sp = field_value_sp.find_all('a')
            if link_sp:
                set_dx['inventory_url'] = link_sp[0]['href']
        
        elif field_name == 'Minifigs':
            set_dx['minifig_cnt'] = field_value_sp.text
            link_sp = field_value_sp.find_all('a')
            if link_sp:
                set_dx['minifig_url'] = link_sp[0]['href']

        elif field_name == 'RRP':
            set_dx['store_price'] = field_value_sp.text.replace(' / ', ', ')

        elif field_name == 'Current value':
            set_dx['current_price'] = field_value_sp.text.replace('\n', '').replace('~', '').replace('U', ', U')

        elif field_name == 'Packaging':
            set_dx['packaging'] = field_value_sp.text

        elif field_name == 'Notes':
            set_dx['notes'] = field_value_sp.text

        elif field_name == 'Rating':
            value_tx = field_value_sp.text[5:].replace('reviews', '').replace('from', ',').replace(' ', '')
            value_ls = value_tx.split(',')
            if len(value_ls) == 2:
                set_dx['rating_value'] = value_ls[0]
                set_dx['rating_votes'] = value_ls[1]
            elif field_value_sp.text.strip() == 'Not yet reviewed':
                pass
            else:
                print(f'rating error: {field_value_sp.text}')

    return set_dx


# clean the store-price so it is a float in dollars
def clean_price(price):
    # skip when price doesn't have a value
    if isinstance(price, float):
        #print(f'float found {price}')
        return np.nan

    price_ls = price.split(',')
    fprice = None
    
    for prc in price_ls:
        if '$' in prc:
            fprice = float(prc.strip()[1:])
    
    if fprice:
        return fprice
    else:
        return np.nan


# clean the current-price so it is a float in dollars
def get_price_used(price):
    return get_current_price(price, 'used')

def get_price_new(price):
    return get_current_price(price, 'new')

def get_current_price(price, price_type):
    
    # this data is never NaN

    price_ls = price.split(',')
    
    if price_type == 'used':
        fprice = price_ls[1].replace('Used: $', '')

    else:
        fprice = price_ls[0].replace('New: $', '')

    try:
        nprice = int(fprice)
    except:
        nprice = None

    return nprice


# clean the ratings votes
def clean_votes(votes_tx):
    # skip when price doesn't have a value
    if isinstance(votes_tx, float):
        #print(f'float found {price}')
        return np.nan

    votes_cl = votes_tx.replace('review', '')
    return float(votes_cl)


# get a count of the entries in the list of lists
def count_in_lists(list_ls):
    
    # get counts of each tag

    counts_dx = {}

    for lst in list_ls:
        entry_ls = lst.split(', ')

        for ntr in entry_ls:

            if ntr not in counts_dx:
                counts_dx[ntr] = 1
            else:
                counts_dx[ntr] += 1

    # tranform to structure good for dataframe

    counts_ls = []

    for key, val in counts_dx.items():
        new_dx = {
            'tag': key,
            'count': val,
        }
        counts_ls.append(new_dx)

    return counts_ls


def get_main_tag(tag_ls):
    return None




"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
GENERAL FUNCTIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


# map themes to category 
def get_category(theme):

    if theme in ['Town', 'Studios', 'Island Xtreme Stunts']:
        return 'Town'

    if theme in ['City', 'World City']:
        return 'City'

    if theme in ['Space']:
        return 'Space'

    if theme in ['Castle']:
        return 'Castle'

    if theme in ['Pirates', 'Adventurers', 'Western']:
        return 'Historic'

    if theme in ['Ninjago', 'Legends of Chima', 'Nexo Knights', 'Exo-Force', 'The LEGO Movie', 'Alpha Team', 'The LEGO Ninjago Movie', 'Aquazone',
                'Speed Champions', 'Atlantis', 'Power Miners', 'Rock Raiders', 'Ultra Agents', 'Agents', 'Monster Fighters']:
        return 'Lego-Brand'

    if theme in ['Star Wars', 'Harry Potter', 'The Hobbit', 'Jurassic World', 'Indiana Jones', 'The Lord of the Rings', 'Toy Story', 
                'Pirates of the Caribbean']:
        return 'Licensed-Movie'

    if theme in ['Disney', 'Marvel Super Heroes', 'DC Comics Super Heroes', 'The LEGO Batman Movie', 'Teenage Mutant Ninja Turtles', 
                'Batman', 'SpongeBob SquarePants']:
        return 'Licensed-Other'

    if theme in ['Trains', 'Sports', 'Juniors', 'Creator Expert', 'Minecraft', 
                ]:
        return 'Exclude'

    if theme in ['Creator', 'Mixels', 'BrickHeadz', 'Racers', 'Fabuland', 'Architecture', 'Elves', 'Cars', 'Jack Stone', 'Unikitty', '4 Juniors',
                'Galidor', 'Model Team', 'DC Super Hero Girls']:
        return 'Exclude-No-Minifigs'        

    return 'None'


# map colors to super-color group
def get_super_color(color_tx):

    if color_tx in ['White']:
        return 'White'

    if color_tx in ['Tan', 'Dark Tan', 'Medium Dark Flesh', 'Light Flesh', 'Dark Flesh', ]:
        return 'Tan'

    if color_tx in ['Yellow', 'Light Yellow', 'Bright Light Yellow', 
                    'Pearl Gold', 'Chrome Gold',    # gold is very rare
                    'Orange', 'Dark Orange', 'Bright Light Orange', 'Medium Orange', 'Earth Orange']:    # orange is quite rare
        return 'Yellow'
 
    if color_tx in ['Red', 'Dark Red', 
                    'Pink', 'Dark Pink', 'Bright Pink', 'Magenta']:       # pink is very rare
        return 'Red'

    if color_tx in ['Green', 'Lime', 'Dark Green', 'Olive Green', 'Sand Green', 'Dark Turquoise', 'Medium Lime', 
                    'Medium Green', 'Light Green', 
                    'Bright Green', 'Yellowish Green']:
        return 'Green'

    if color_tx in ['Reddish Brown', 'Brown', 'Dark Brown', 'Fabuland Brown']:
        return 'Brown'

    if color_tx in ['Blue', 'Dark Blue', 'Dark Azure', 'Medium Blue', 'Medium Azure', 'Maersk Blue', 'Sand Blue',
                    'Royal Blue', 'Aqua', 'Blue-Violet', 'Light Blue', 'Chrome Blue', 'Bright Light Blue', 
                    'Dark Purple', 'Medium Lavender', 'Sand Purple', 'Purple', 'Lavender']:    # purple is very rare 
        return 'Blue'

    if color_tx in ['Light Bluish Gray', 'Light Gray', 'Dark Bluish Gray', 'Dark Gray', 'Pearl Dark Gray', 
                    'Flat Silver', 'Chrome Silver', 'Pearl Light Gray', 'Metallic Silver']:
        return 'Gray'

    if color_tx in ['Black']:
        return 'Black'

    if color_tx in ['Trans-Neon Orange', 'Trans-Neon Green', 'Trans-Dark Blue', 'Trans-Clear', 'Trans-Red', 
                    'Trans-Dark Pink', 'Trans-Pink', 'Trans-Yellow', 'Trans-Very Lt Blue', 'Glitter Trans-Dark Pink',
                    'Trans-Orange', 'Trans-Purple', 'Trans-Medium Blue', 'Trans-Bright Green', 
                    'Trans-Light Blue', 'Trans-Black', 'Trans-Green', ]:
        return 'Transparent'

    return None


def get_aftermarket(set_rw):

    store = set_rw['price_store']
    used = set_rw['price_used']

    if not store or not used:
        return np.NaN

    return used - store







