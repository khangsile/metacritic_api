metacritic_api
==============

Python API for Metacritic.com

Currently, the API can grab scores for any category. Some functions:

searchFirstResult: searches for the query and grabs the first result off the list 
-by searching first, the query is a little slower due to the extra HTTP request and parsing through an extra page,
 but this also allows people to incorrectly type titles and still get (most likely) the response they were looking for.

searchTVSeries: searches for the query and grabs the entire TV series. Returns a list of TVCriticInfo instances.
-uses searchFirstResult and from Season 1 grabs the rest of the TV series through links. 

I tried to abstract this as much as possible so that if anyone else wanted to make additions it would be easier. Currently, 
scores are pulled from the details page rather than the front page. That's an easy fix if someone thinks it would be better 
use the front page rather than the details page. 

Some classes:

MetaCriticInfo: base class that is initialized with arguments title, type, link (to page)
 - upon initialization, the class loads the page using the link and grabs extra data (criticscore, userscore, releaseDate,
 summary)
 - all scores are averaged to the 100 scale - this doesn't really affect the criticscore, but the userscore is multiplied
 by a factor of ten to place it even with the criticscore.

TVCriticInfo: derived class of MetaCriticInfo
 - initialization grabs extra data - really just the season title (Name: Season 1, Name: Season 2, etc.)

TVSeriesInfo: 
 - class that holds a list of TVCriticInfo(s) 
 - initialized by title, type, link (to page) - the link to the page is automatically directed to the first season
 - from the first season we can grab links to all of the other seasons and append each season to the list, I did this
 using threading to speed up the initialization. It's only slightly faster I think. Because I use threading, the 
 initialization sorts the series according to season title.

To Do:
 - maybe add a little more multithreading
 - definitely speed up
 - return output as JSON rather than python objects
