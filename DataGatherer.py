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
        with open(filename) as data_file:
            self.data = json.load(data_file)
        
    def getProfessor(self):
        return self.data['courses'][self.index]['Instructor1Name']

    def getName(self):
        return self.data['courses'][self.index]['name']

    def getDescription(self):
        return (root[0][self.index][18].text)
    def getUnits(self):
        return (root[0][self.index][22].text)
    
def run():
    dg = DataGatherer(0)
    print(dg.getDescription())
    print(dg.getName())
    print(dg.getUnits())
if __name__ == '__main__':
    run()

