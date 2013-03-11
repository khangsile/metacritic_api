import urllib2
import re
import sys 
import threading
import thread 
from bs4 import BeautifulSoup

BASE_URL = "http://www.metacritic.com"

class MetaCritic(object):
  def __init__(self, info=None):
    if not info:
      self.title = None
      self.type = None
      self.criticscore = None
      self.userscore = None
      self.releaseDate = None
      self.summary = None
    else:
      self.title = info.title
      self.type = info.type
      self.criticscore = info.criticscore
      self.userscore = info.userscore
      self.releaseDate = info.releaseDate
      self.summary = info.summary

class TVCritic(MetaCritic):
  def __init__(self, info=None):
    if not info:
      self.season = None
    else:
      self.season = info.season
      super(TVCritic, self).__init__(info)

class TVSeries(object):
  def __init__(self, info=None):
    self.seasons = []
    if info:
      for season in info.series:
        self.seasons.append(TVCritic(season))
      self.title = info.title

class MetaCriticInfo(object):
  
  def __init__(self, type, url):
    
    if type != None:
      self.type = type
    else:
      self.type = None
    
    self.page = None
    self.criticscore = None
    self.userscore = None
    self.releaseDate = None
    self.summary = None

    self.page = self.__getPage(url)
    
    if (url):
      #threaded functions below - none interleave
      tiThread = threading.Thread(target = self.__getTitle)
      csThread = threading.Thread(target = self.__getCriticScore)
      usThread = threading.Thread(target = self.__getUserScore)
      rdThread = threading.Thread(target = self.__getReleaseDate)
      sumThread = threading.Thread(target = self.__getSummary)

      tiThread.start()
      csThread.start()
      usThread.start()
      rdThread.start()
      sumThread.start()

      tiThraed.join()
      csThread.join()
      usThread.join()
      rdThread.join()
      sumThread.join()

  def __getPage(self, url):
   
    success = False
    while not success:
      try:      
        page = urllib2.urlopen(url+"/details")
        page = BeautifulSoup(page)
        success = True
      except urllib2.HTTPError, e:
        page = "404"
        success = False

    return page

  def __getScore(self, soup):
    scoreSection = soup.find("span")

    score = scoreSection.renderContents()
  
    if score.strip() == "No score yet":
      return 0;
    else:
      score = float(score)

    rangeSection = scoreSection.findNextSibling("span").renderContents()
    range = re.search("\d+", rangeSection).group()
    range = float(range)

    percent = (score / range) * 100
    percent = int(percent)

    return percent

  def __getTitle(self):
    soup = self.page

    if soup == "404":
      return 

    title = soup.find(
      "div",
      {"class":"product_title"}).find("a").renderContents()

    self.title = title
    
  def __getCriticScore(self):
    req = self.page
  
    if req == "404":
      return 

    soup = req

    criticinfo = soup.find(
      "div",
      {"class": "metascore_wrap feature_metascore"})

    percent = self.__getScore(criticinfo)
    
    if percent == 0:
      return "N/A"

    self.criticscore = percent
  
  def __getUserScore(self):
    req = self.page

    if req == "404":
      return

    soup = req
    
    usersinfo = soup.find(
      "div", 
      {"class" : "userscore_wrap feature_userscore"})

    percent = self.__getScore(usersinfo)
  
    if percent == 0:
      return "N/A"

    self.userscore = percent

  def __getReleaseDate(self):
    req = self.page

    if req == "404":
      return 
    
    soup = req
        
    releaseData = soup.find(
      "li", 
      {"class" : "summary_detail release_data"})

    date = releaseData.find("span", { "class": "data"}).renderContents()

    self.releaseDate = date

  def __getSummary(self):
    req = self.page

    if req == "404":
      return 

    soup = req

    summaryData = soup.find(
      "div", 
      {"class" : "summary_detail product_summary"})

    blurbCollapsed = summaryData.find(
      "span", 
      {"class": "blurb blurb_collapsed"})

    if blurbCollapsed:
      blurbCollapsed = blurbCollapsed.renderContents()

    blurbExpanded = summaryData.find(
      "span",
      {"class": "blurb blurb_expanded"})

    if blurbExpanded:
      blurbExpanded = blurbExpanded.renderContents()

    if blurbExpanded and blurbCollapsed:
      summary = blurbCollapsed + blurbExpanded
    else:
      summary = summaryData.find("span", {"class": "data"})
      if summary:
        summary = summary.renderContents().strip()

    self.summary = summary

class TVCriticInfo(MetaCriticInfo):
  def __init__(self, type, url):
    super(TVCriticInfo, self).__init__(type, url)
    self.__getSeason()

  def __getSeason(self):
    
    self.season = re.search("Season (\d+)", self.title).group(1)
    self.season = int(self.season)

class TVSeriesInfo(object):
  def __init__(self, firstType, firstLink):
    self.series = [];
    self.title = "Mad Men";
    self.lock = threading.RLock()

    self.series = self.__createSeries(firstType, firstLink)
    

  def __updateSeries(self, season, seasonLink=None):
    if season and seasonLink:
      season = TVCriticInfo(season, seasonLink)
    else:
      season = seasonTitle

    with self.lock:
      self.series.append(season)

  def __createSeries(self, seasonType, seasonLink):
    firstSeason = TVCriticInfo(seasonType, seasonLink)
    self.series.append(firstSeason)

    soup = firstSeason.page

    soup = soup.find('li', {'class': 'summary_detail product_seasons'})

    seasonData = soup.find('span', {'class': 'data'})

    seasonLinks = seasonData.find_all('a')

    self.__getTitle(firstSeason.title)

    for link in seasonLinks:
      link = BASE_URL+link['href']
      mythread = threading.Thread(target = self.__updateSeries,
        args = (seasonType, link))
      mythread.start()
    
    for thread in threading.enumerate():
      if thread is not threading.currentThread():
        thread.join()
        
    return self.__sortSeries()

  def __getTitle(self, firstSeasonTitle):
    title = re.search('([\w\s\:]*): Season', firstSeasonTitle).group(1)

    self.title = title

  def __sortSeries(self):
    return sorted(self.series, key = lambda season: season.season)
      
