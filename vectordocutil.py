from IPython.display import display, HTML, Image
from itertools import islice
import numpy as np
import json
import gzip 
import array

def iter_products(fname):
  with gzip.open(fname, 'r') as g:
    for l in g:
      yield eval(l)

def iter_vectors(fname):
  with open(fname, 'rb') as f:
    while True:
      try:
        asin = f.read(10)
        a = array.array('f')
        a.fromfile(f, 4096)
        yield (asin.decode(), a.tolist())
      except EOFError:
        break

def iter_vectors_reduced(fname, dims=1024, samples=10000):
  sumarr = np.zeros(4096) * 1.0
  for (_, v) in islice(iter_vectors(fname), samples):
    sumarr -= np.array(v)
  ii = np.argsort(sumarr)[:dims]

  def f(fname):
    for (asin, vec) in iter_vectors(fname):
      yield (asin, np.array(vec)[ii].tolist())

  return f

def display_hits(res):
    print(f"Found {res['hits']['total']['value']} hits in {res['took']} ms. Showing top {len(res['hits']['hits'])}.")
    print("")
    for hit in res['hits']['hits']:
        s = hit['_source']
        print(f"Title   {s.get('title', None)}")
        if 'description' in s:
          desc = str(s.get('description', None))
          print(f"Desc    {desc[:80] + ('...' if len(desc) > 80 else '')}")
        if 'price' in s:
          print(f"Price   {s['price']}")
        print(f"ID      {s.get('asin', None)}")
        print(f"Score   {hit.get('_score', None)}")
        display(Image(s.get("imUrl"), width=128))
        print("")

def display_hits_horizontal(res):
    print(f"Found {res['hits']['total']['value']} hits in {res['took']} ms. Showing top {len(res['hits']['hits'])}.")
    html = "<table><tr>"
    for hit in res['hits']['hits']:
        s = hit['_source']
        html += f"<td><img src=\"{s.get('imUrl')}\" width=128 /><p>{s.get('asin')}, {hit.get('_score')}</p></td>"
    html += "</tr></table>"
    display(HTML(html))

# To paginate over a list
def listToChuncks(pagesize, listsource):
    return [listsource[i:i+pagesize] for i in range(0, len(listsource), pagesize)]


# To fetch record by id 
def getRecFromList(parentID, cdata):
    #print(parentID)
    for rec in cdata:
        if rec['id'] == parentID:
            return rec

# To flatten the tree ontology concepts tree structure blabla        
def flatten(rec, cdata):
    flatlist = []
    for element in rec['child_ids']:
        el = getRecFromList(element, cdata)
        #print(el)
        if type(el['child_ids']) == list and len(el['child_ids'])>0:
            flatlist += flatten(el, cdata)
        else:
            #print('---', rec['name'])
            value = el['name']
            if value not in flatlist:
                flatlist.append(value)#el['name']
    return flatlist
