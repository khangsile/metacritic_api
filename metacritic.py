import urllib2, re, sys, pycurl, time
from bs4 import BeautifulSoup
from StringIO import StringIO

query = ["Mad Men", "tv"]

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

def searchFirst(query, type):
  BASE_URL = "http://www.metacritic.com"
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
      
  soup = BeautifulSoup(page)
  
  soup = soup.find('li', 
    {'class': 'result first_result'})
  
  metacritic = []
  metacritic['type'] = __getType(soup)
  link = __getLink(soup)
  metacritic['link'] = BASE_URL+link
  metacritic['title'] = __getTitle(soup)

  return metacritic   

def searchFirstResult(query, type):
  if type == None:
    type = "all"
  
  metacritic = searchFirst(query, type)

  type = metacritic['type']
  link = metacritic['link']
  title = metacritic['title']

  return MetaCritic(title, type, link)

def searchTVSeries(query):

  firstSeason = searchFirstResult(query, 'tv')

  soup = BeautifulSoup(season1.page)

  seasonsSoup = soup.find("li", "class": {"summary_detail product_seasons"})
  if not seasonsSoup:
    return season1

class MetaCritic:

  def __init__(self, title, type, url):
    if title == None:
      self.title = "Not Found"
    else:
      self.title = title
    
    if type == None:
      self.type = "Not Found"
    else:
      self.type = type
    
    self.page = self.__getPage(url)
    self.criticscore = self.__getCriticScore()
    self.userscore = self.__getUserScore()
    self.releaseDate = self.__getReleaseDate()
    self.summary = self.__getSummary()

  def __getPage(self, url):
    try:
      page = urllib2.urlopen(url)
      page = page.read()
    except urllib2.HTTPError, e:
      page = "404"
      
    return page

  def __getScore(self, soup):
    scoreSection = soup.find('span')

    score = scoreSection.renderContents()
  
    if score.strip() == "No score yet":
      return 0;
    else:
      score = float(score)

    rangeSection = scoreSection.findNextSibling('span').renderContents()
    range = re.search("\d+", rangeSection).group()
    range = float(range)

    percent = (score / range) * 100
    percent = int(percent)

    return percent

  def __getCriticScore(self):
    req = self.page
  
    if req == '404':
      return "Page Does Not Exist"

    soup = BeautifulSoup(req)

    criticinfo = soup.find("div",
      {"class": "metascore_wrap highlight_metascore"})

    percent = self.__getScore(criticinfo)
  
    return percent
  
  def __getUserScore(self):
    req = self.page
    
    if req == '404':
      return "Page Does Not Exist"

    soup = BeautifulSoup(req)
    
    usersinfo = soup.find("div", 
      {"class" : "userscore_wrap feature_userscore"})

    percent = self.__getScore(usersinfo)
  
    return percent

  def __getReleaseDate(self):
    req = self.page

    if req == '404':
      return "Page Does Not Exist"
    
    soup = BeautifulSoup(req)

    releaseData = soup.find("li", {"class" : "summary_detail release_data"});
    date = releaseData.find("span", { "class": "data"}).renderContents()

    return date

  def __getSummary(self):
    req = self.page

    if req == '404':
      return "Page Does Not Exist"

    soup = BeautifulSoup(req)

    summaryData = soup.find("li", 
      {"class" : "summary_detail product_summary"})

    blurbCollapsed = summaryData.find("span", 
      {"class": "blurb blurb_collapsed"})

    if blurbCollapsed:
      blurbCollapsed = blurbCollapsed.renderContents()

    blurbExpanded = summaryData.find("span",
      {"class": "blurb blurb_expanded"})

    if blurbExpanded:
      blurbExpanded = blurbExpanded.renderContents()

    if blurbExpanded and blurbCollapsed:
      summary = blurbCollapsed + blurbExpanded
    else:
      summary = summaryData.find("span", {"class": "data"})
      if summary:
        summary = summary.renderContents().strip()

    return summary

class TVCritic(MetaCritic):
  def __init__(self, title, type, url):
    super(TVCritic, self).__init__(title, type, url)
    self.season = __getSeason()

  def __getSeason(self):
    soup = BeautifulSoup(self.page)
    
    season = soup.find('div', {'class':'product_title'}).find('a').renderContents()

    return season

not_found = 0;
found = 0;

meta = searchFirstResult(query[0], query[1])
  
print meta.title
print meta.type
print meta.summary
print meta.criticscore
print meta.userscore


