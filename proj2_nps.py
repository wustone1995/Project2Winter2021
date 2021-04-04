#################################
##### Name: Yuanfeng Wu
##### Uniqname: yuanfenw
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
import os
from secrets import API_KEY

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category='no category', name='no name', address='no address', zipcode='no zipcode', phone='no phone'):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone 
    
    def info(self):
        ''' returns a string of the national site's information

        Parameters
        ----------
        None

        Returns
        -------
        str: string
            The format is <name> (<category>): <address> <zip> 
        '''
        str = f'{self.name} ({self.category}): {self.address} {self.zipcode}'
        return str


def build_state_url_dict(cache_file=False):
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    cache_file: JSON
        the cache file of the retrived data (states and their url)

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    if cache_file is False:
        dict = {}
        base_url = 'https://www.nps.gov'
        index_url = '/index.htm'
        url = base_url + index_url
        response = requests.get(url)
        print('Fetching')
        soup = BeautifulSoup(response.text, 'html.parser')
        states_list = soup.find('ul', class_='dropdown-menu SearchBar-keywordSearch').find_all('li')
        for state in states_list:
            state_name = state.find('a').text.lower()
            state_url = state.find('a')['href']
            dict[state_name] = base_url + state_url
        if os.path.exists('cache.json'):
            with open('cache.json', 'r') as f:
                cache = json.load(fp=f)
                f.close()
        else:
            cache = {}
        cache['state_url_dict'] = dict
        with open('cache.json', 'w') as f:
            json.dump(cache, f)
            f.close()
    else:
        print('Using Cache')
        with open('cache.json', 'r') as f:
            cache = json.load(fp=f)
            f.close()
        dict = cache['state_url_dict']
    return dict
       

def get_site_instance(site_url, cache_file=False):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    cache_file: JSON
        the cache file of the retrived data (sites information)
    
    Returns
    -------
    instance
        a national site instance
    '''
    if cache_file is False:
        response = requests.get(site_url)
        if os.path.exists('cache.json'):
            with open('cache.json', 'r') as f:
                cache = json.load(fp=f)
                f.close()
        else:
            cache = {}
        cache[site_url] = response.text
        with open('cache.json', 'w') as f:
            json.dump(cache, f)
            f.close()
        print('Fetching')
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        print('Using Cache')
        with open('cache.json', 'r') as f:
            cache = json.load(fp=f)
            f.close()
        soup = BeautifulSoup(cache[site_url], 'html.parser')
    title_container = soup.find('div', class_='Hero-titleContainer clearfix')
    site_name = title_container.find('a').text
    site_desiganation = title_container.find('div', class_='Hero-designationContainer')
    site_category = site_desiganation.find('span', class_='Hero-designation')
    if (site_category is None) or (site_category.text == ''):
        site_category = 'no category'
    else:
        site_category = site_category.text.strip()
    site_address = soup.find('span', itemprop='addressLocality')
    site_city = soup.find('span', class_='region')
    if (site_address is None) or (site_city is None):
        site_address = 'no address'
    else:
        site_address = site_address.text.strip() + ', ' + site_city.text.strip()
    site_zipcode = soup.find('span', class_='postal-code')
    if (site_zipcode is None) or (site_zipcode.text == ''):
        site_zipcode = 'no zipcode'
    else:
        site_zipcode = site_zipcode.text.strip()
    site_phone = soup.find('span', itemprop='telephone').text.strip()
    instance = NationalSite(site_category, site_name, site_address, site_zipcode, site_phone)
    return instance 
    


def get_sites_for_state(state_url, cache_file=False):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    base_url = 'https://www.nps.gov'
    if cache_file is False:
        list = []
        response = requests.get(state_url)
        if os.path.exists('cache.json'):
            with open('cache.json', 'r') as f:
                cache = json.load(fp=f)
                f.close()
        else:
            cache = {}
        cache[state_url] = response.text
        with open('cache.json', 'w') as f:
            json.dump(cache, f)
            f.close()
        print('Fetching')
        soup = BeautifulSoup(response.text, 'html.parser')
        sites_list = soup.find('ul', id='list_parks').find_all('li', recursive=False)
        for site in sites_list:
            s_url = site.find('h3').find('a')['href']
            site_url = base_url + s_url
            instance = get_site_instance(site_url)
            list.append(instance)
    else:
        list = []
        print('Using Cache')
        with open('cache.json', 'r') as f:
            cache = json.load(fp=f)
            f.close()
        soup = BeautifulSoup(cache[state_url], 'html.parser')
        sites_list = soup.find('ul', id='list_parks').find_all('li', recursive=False)
        for site in sites_list:
            s_url = site.find('h3').find('a')['href']
            site_url = base_url + s_url
            instance = get_site_instance(site_url, cache_file=True)
            list.append(instance)
    return list

def get_nearby_places(site_object, cache_file=False):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    if cache_file is False:
        print('Fetching')
        base_url = 'http://www.mapquestapi.com/search/v2/radius'
        para_dict = {'key': API_KEY, 'origin': site_object.zipcode,
                    'radius': '10', 'maxMatches': '10', 
                    'ambiguities': 'ignore', 'outFormat': 'json'}
        response = requests.get(base_url, para_dict)
        if os.path.exists('cache.json'):
            with open('cache.json', 'r') as f:
                cache = json.load(fp=f)
                f.close()
        else:
            cache = {}
        cache[site_object.name] = response.text
        with open('cache.json', 'w') as f:
            json.dump(cache, f)
            f.close()
        Results_Dictionary = json.loads(response.text)
    else:
        print('Using Cache')
        with open('cache.json', 'r') as f:
            cache = json.load(fp=f)
            f.close() 
        Results_Dictionary = json.loads(cache[site_object.name])
    Results_Dictionary = Results_Dictionary
    return Results_Dictionary

def print_nearby_places(list, cache_file=False):
    '''Obtain (up to 10) nearby places or back to the upper level
    
    Parameters
    ----------
    list: list
        a list of national site instances
    
    Returns
    -------
    flag: integer
        an interger represent the current situation
    '''
    flag = 0
    str = input('Choose the number for detail search or "exit" or "back": ')
    if str == 'exit':
        flag = 1
        return flag
    elif str == 'back':
        flag = 2
        return flag
    elif int(str)<=0 or int(str)>len(list):
        print('[Error] Invalid input.')
        flag = 3
        return flag
    else:
        site_obj = list[int(str)-1]
        if site_obj.zipcode == 'no zipcode':
            print("[Error] This site has no zipcode to search.")
            flag = 3
            return flag
        Results_Dictionary = get_nearby_places(site_obj, cache_file=cache_file)
        Results_Dictionary = Results_Dictionary['searchResults']
        nearby_places_list = []
        l = min(len(Results_Dictionary), 10)
        print('*'*50)
        print(f'Places near {site_obj.name}')
        print('*'*50)
        for i in range(l):
            temp = Results_Dictionary[i]['fields']
            if temp['name'].strip() != '':
                place_name = temp['name'].strip()
            else:
                place_name = 'no name'
            if temp['group_sic_code_name'].strip() != '':
                place_category = temp['group_sic_code_name']
            else:
                place_category = 'no category'
            if temp['address'].strip() != '':
                place_address = temp['address']
            else:
                place_address = 'no address'
            if temp['city'].strip() != '':
                place_city = temp['city']
            else:
                place_city = 'no city'
            print(f'- {place_name} ({place_category}): {place_address}, {place_city}')
        flag = 3
        return flag

def main():
    '''Main part of the program to scrape and search for information.

    User input "1" or "2" to choose fetching or using the cache
    User inputs the state name, it returns the national sites' informaiton
    User can quit at any time by enter "exit"

    Parameters
    ----------
    None
    
    Returns
    -------
    None
    '''
    exit_flag = 0
    while True:
        s = input('Enter "1" for fetching, "2" for using the cache or "exit":')
        if s == '1':
            state_url_dic = build_state_url_dict()
            while True:
                str = input('Enter a state name (e.g. Michigan or michigan) or "exit": ')
                if str == 'exit':
                    exit_flag = 1
                    break
                else:
                    state = str.lower()
                    if state in state_url_dic:
                        state_url = state_url_dic[state]
                        list = get_sites_for_state(state_url)
                        count = 1
                        print('*'*50)
                        print(f'List of national sites in {state}')
                        print('*'*50)
                        for site in list:
                            print(f'[{count}] {site.info()}')
                            count += 1
                        while True:
                            flag = print_nearby_places(list)
                            if flag == 1:
                                exit_flag = 1
                                break
                            elif flag == 2:
                                break
                        if exit_flag == 1:
                            break
                    else:
                        print('[Error] Enter proper state name.')
            if exit_flag == 1:
                break
        elif s == '2':
            state_url_dic = build_state_url_dict(cache_file=True)
            while True:
                str = input('Enter a state name (e.g. Michigan or michigan) or "exit": ')
                if str == 'exit':
                    exit_flag = 1
                    break
                else:
                    state = str.lower()
                    if state in state_url_dic:
                        state_url = state_url_dic[state]
                        list = get_sites_for_state(state_url, cache_file=True)
                        count = 1
                        print('*'*50)
                        print(f'List of national sites in {state}')
                        print('*'*50)
                        for site in list:
                            print(f'[{count}] {site.info()}')
                            count += 1
                        while True:
                            flag = print_nearby_places(list, cache_file=True)
                            if flag == 1:
                                exit_flag = 1
                                break
                            elif flag == 2:
                                break
                        if exit_flag == 1:
                            break
                    else:
                        print('[Error] Enter proper state name.')
            if exit_flag == 1:
                break
        elif s == 'exit':
            break
        else:
            print('[Error] Please check your input.')

if __name__ == "__main__":
    main()
    