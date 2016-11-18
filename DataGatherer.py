import xml.etree.ElementTree as ET
import json
tree = ET.parse('coms.xml')
root = tree.getroot()
#app = Flask(__name__)
filename = "doc.json"

class DataGatherer:
    def __init__(self, index):
        self.index = index
        self.tree = ET.parse('coms.xml')
        self.root = self.tree.getroot()

    def getName(self):
        name = "COMS"+(root[0][self.index][5].text)
        return (name)

    def getDescription(self):
        return (root[0][self.index][18].text)
    
def run():
    dg = DataGatherer(0)
    print(dg.getDescription())
    print(dg.getName())
if __name__ == '__main__':
    run()

