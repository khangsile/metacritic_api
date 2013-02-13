import urllib2, re, sys, time
from metacritic import MetaCriticInfo, TVCriticInfo, TVSeriesInfo
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
      
  return page.read()

#might just convert this to a list of dicts, then call it getResults
def __getFirstResult(query, type):
  page = search(query, type)

  soup = BeautifulSoup(page)
  
  soup = soup.find('li', 
    {'class': 'result first_result'})
  
  metacritic = {}
  metacritic['type'] = __getType(soup)
  link = __getLink(soup)
  metacritic['link'] = BASE_URL+link
  metacritic['title'] = __getTitle(soup)

  return metacritic   

def searchFirstResult(query, type):
  if type == None or type.strip() == '':
    type = 'all'
  
  metacritic = __getFirstResult(query, type)

  type = metacritic['type']
  link = metacritic['link']
  title = metacritic['title']

  if type == 'tv':
    return TVCriticInfo(title, type, link)

  return MetaCriticInfo(title, type, link)

def searchTVSeries(query):

  series = __getFirstResult(query, 'tv')
  
  series = TVSeriesInfo(series['title'], series['type'], series['link'])
  
  return sorted(series.series, key = lambda season: season.season)

  
