import urllib2, re, sys, time, json
from metacritic import *
from bs4 import BeautifulSoup

BASE_URL = "http://www.metacritic.com"

def __getType(soup):
  typeSoup = soup.find('div', {'class': 'result_type'})
  type = typeSoup.find('strong').renderContents()

  return type

def __getTitleInfo(soup):
  titleSoup = soup.find('h3', 
    {'class': 'product_title basic_stat'})

  if titleSoup != None:
    titleTag = titleSoup.find('a')
  else:
    titleTag = None

  return titleTag
  
def __getLink(soup):
  titleTag = __getTitleInfo(soup)
  
  if titleTag != None:
    link = titleTag.get('href')
  else:
    link = "/does/not/exist"

  return link

def __getTitle(soup):
  titleTag = __getTitleInfo(soup)

  if titleTag != None:
    title = titleTag.renderContents()
  else:
    title = None

  return title

def search(query, type):
  search = "/search/%type/%query/results"

  search = search.replace('%type', type)

  query = query.strip().replace(' ', '+')
  search = search.replace('%query', query) 
  
  success = False
  while success != True:
    try:
      page = urllib2.urlopen(BASE_URL+search)
      success = True
    except urllib2.HTTPError, e:
      success = False
      
  return page

#might just convert this to a list of dicts, then call it getResults
def __getFirstResult(query, type):
  page = search(query, type)

  soup = BeautifulSoup(page)
  
  soup = soup.find('li', 
    {'class': 'result first_result'})
  
  if not soup:
    return None

  metacritic = {}
  metacritic['type'] = __getType(soup)
  link = __getLink(soup)
  metacritic['link'] = BASE_URL+link

  return metacritic   

def searchFirstResult(query, type = None):
  if type == None or type.strip() == '':
    type = 'all'
  
  metacritic = __getFirstResult(query, type)
 
  if not metacritic:
    return None

  type = metacritic['type']
  link = metacritic['link']

  if type == 'TV Show':
    return TVCriticInfo(type, link)
  
  return MetaCriticInfo(type, link)

def searchTVSeries(query):

  series = __getFirstResult(query, 'tv')
  
  if not series:
    return None

  series = TVSeriesInfo(series['type'], series['link'])
  
  return series

class MyEncoder(json.JSONEncoder):
  def default(self, obj):
    
    return obj.__dict__

def jsearchFirstResult(query, type = None):
  if type == None or type.strip() == '':
    type = 'all'

  metacriticinfo = searchFirstResult(query, type)

  return json.dumps(MetaCritic(metacriticinfo), cls=MyEncoder)

def jsearchTVSeries(query):
  series = searchTVSeries(query)
  
  return json.dumps(TVSeries(series), cls=MyEncoder)
