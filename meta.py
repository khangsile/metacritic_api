import metasearch
import time
import sys

if len(sys.argv) <= 1:
  sys.exit("You're an idiot. You have no input")

query = sys.argv[1]
search = sys.argv[2]
type = None

if search == 'ps':
  if len(sys.argv) > 3:
    type = sys.argv[3]
  print metasearch.jsearchFirstResult(query, type)
if search == 'tvs':
  start = time.time()
  print metasearch.jsearchTVSeries(query)
  end = time.time()
  print end - start


