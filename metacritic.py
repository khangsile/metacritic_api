import urllib2, re, sys
from bs4 import BeautifulSoup

query = ["Gears of War", "game"]

def lookup(query, type):
  BASE_URL = "http://www.metacritic.com"
  search = "/search/%type/%query/results"

  if (type == None):
    type = "all"
  search = search.replace('%type', type)

  query = query.strip().replace(' ', '+')
  search = search.replace('%query', query) 
  try:
    page = urllib2.urlopen(BASE_URL + search)
  except urllib2.HTTPError, e:
    return MetaCritic(None, None, "http://www.metacritic.com/does/not/exist")
  
  soup = BeautifulSoup(page)
  
  soup = soup.find('li', 
    {'class': 'result first_result'})
    
  typeSoup = soup.find('div', {'class': 'result_type'})
  type = typeSoup.find('strong').renderContents()

  titleSoup = soup.find('h3', 
    {'class': 'product_title basic_stat'})  
  titleTag = titleSoup.find('a') 
  
  link = titleTag.get('href')
  title = titleTag.renderContents()

  return MetaCritic(title, type, BASE_URL+link)   

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

meta = lookup(query[0], query[1])

print meta.title
print meta.type
print meta.criticscore
print meta.userscore
print meta.releaseDate


