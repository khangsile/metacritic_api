import urllib2, re, sys, threading, time, thread, requests
from bs4 import BeautifulSoup

BASE_URL = "http://www.metacritic.com"

class MetaCriticInfo(object):
  def __init__(self):
    self.title = None;
    self.type = None;
    self.page = None;
    self.criticscore = None;
    self.userscore = None;
    self.releaseDate = None;
    self.summary = None;

  def __init__(self, title, type, url):
    if title == None:
      self.title = "Not Found"
    else:
      self.title = title
    
    if type == None:
      self.type = "Not Found"
    else:
      self.type = type
    
    self.page = None
    self.criticscore = None
    self.userscore = None
    self.releaseDate = None
    self.summary = None

    self.page = self.__getPage(url)

    #threaded functions below - none interleave

    csThread = threading.Thread(target = self.__getCriticScore)
    #csThread.start()

    usThread = threading.Thread(target = self.__getUserScore)
    #usThread.start()

    rdThread = threading.Thread(target = self.__getReleaseDate)
    #rdThread.start()

    sumThread = threading.Thread(target = self.__getSummary)
    #sumThread.start()

    #for thread in threading.enumerate():
    #  if thread is not threading.currentThread():
    #    thread.join()
    
    csThread.start()
    usThread.start()
    rdThread.start()
    sumThread.start()

    #self.__getCriticScore()
    #self.__getUserScore()
    #self.__getReleaseDate()
    #self.__getSummary()

  def __getPage(self, url):
    
    try:      
      page = urllib2.urlopen(url+"/details")
      #page = requests.get(url+"/details")
      #page = page.text
      page = BeautifulSoup(page)
    except urllib2.HTTPError, e:
      page = "404"
      
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

  def __getCriticScore(self):
    req = self.page
  
    if req == "404":
      return "Page Does Not Exist"

    soup = req

    criticinfo = soup.find("div",
      {"class": "metascore_wrap feature_metascore"})

    percent = self.__getScore(criticinfo)
    
    if percent == 0:
      return "N/A"

    self.criticscore = percent
  
  def __getUserScore(self):
    req = self.page

    if req == "404":
      return "Page Does Not Exist"

    soup = req
    
    usersinfo = soup.find("div", 
      {"class" : "userscore_wrap feature_userscore"})

    percent = self.__getScore(usersinfo)
  
    if percent == 0:
      return "N/A"

    self.userscore = percent

  def __getReleaseDate(self):
    req = self.page

    if req == "404":
      return "Page Does Not Exist"
    
    soup = req
        
    releaseData = soup.find("li", 
      {"class" : "summary_detail release_data"})

    date = releaseData.find("span", { "class": "data"}).renderContents()

    self.releaseDate = date

  def __getSummary(self):
    req = self.page

    if req == "404":
      return "Page Does Not Exist"

    soup = req

    summaryData = soup.find("div", 
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

    self.summary = summary

class TVCriticInfo(MetaCriticInfo):
  def __init__(self, title, type, url):
    super(TVCriticInfo, self).__init__(title, type, url)
    self.season = self.__getSeason()

  def __getSeason(self):
    soup = self.page
    
    season = soup.find("div", 
      {"class":"product_title"}).find("a").renderContents()

    return season

class TVSeriesInfo(object):
  def __init__(self, firstTitle, firstType, firstLink):
    self.series = [];
    self.lock = threading.RLock()

    self.series = self.__createSeries(firstTitle, firstType, firstLink)
    

  def __updateSeries(self, seasonTitle, seasonType=None, seasonLink=None):
    if seasonType and seasonLink:
      season = TVCriticInfo(seasonTitle, seasonType, seasonLink)
    else:
      season = seasonTitle

    with self.lock:
      self.series.append(season)

  def __createSeries(self, seasonTitle, seasonType, seasonLink):
    firstSeason = TVCriticInfo(seasonTitle, seasonType, seasonLink)
    self.series.append(firstSeason)

    soup = firstSeason.page

    soup = soup.find('li', {'class': 'summary_detail product_seasons'})

    seasonData = soup.find('span', {'class': 'data'})

    seasonLinks = seasonData.find_all('a')

    for link in seasonLinks:
      link = BASE_URL+link['href']
      mythread = threading.Thread(target = self.__updateSeries,
        args = (seasonTitle, seasonType, link))
      mythread.start()
    
    for thread in threading.enumerate():
      if thread is not threading.currentThread():
        thread.join()
        
    return self.__sortSeries()

  def __sortSeries(self):
    return sorted(self.series, key = lambda season: season.season)
      
