import zipfile

from collections import defaultdict
from io          import BytesIO
from lxml.html       import fromstring

from lib.Config import Configuration as conf
from lib.Source import Source

class ReferenceIDs(Source):
  def __init__(self):
    self.name = "refmap"
    _file, r = conf.getFeedData('ref', unpack=False)
    zipobj   = zipfile.ZipFile(BytesIO(_file.read()))
    self.cves = defaultdict(dict)

    for filename in zipobj.namelist():
      with zipobj.open(filename) as infile:
        page = fromstring(infile.read().decode("utf-8"))
        vendor = page.xpath("//table[1]//tr[1]//td[2]")
        if vendor: vendor = vendor[0].text.lower()
        rows = page.xpath("//table[2]//tr//td")
        # CVE - Source ID
        IDs = [[rows[i].text, [x.text for x in rows[i+1].iterchildren()]] for i in range(0, len(rows), 2)]
        for e in IDs:
          vendorID = e[0] if not e[0].startswith(vendor.upper()+':') else e[0][len(vendor)+1:]
          for cve in e[1]:
            if vendor not in self.cves[cve]:           self.cves[cve][vendor] = []
            if vendorID not in self.cves[cve][vendor]: self.cves[cve][vendor].append(vendorID)
