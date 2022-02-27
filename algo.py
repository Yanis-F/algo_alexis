import csv

class DataManager: 
    def readcsv(self,fichiercsv):
        datamoche=None
        with open(fichiercsv, newline='') as csvfile:
            reader = csv.reader(csvfile)
            datamoche=list(reader)
        propriétés=datamoche.pop(0)
        self.linecount=len(datamoche)
        self.datajoli={}   
        for propriété in propriétés:
            self.datajoli[propriété]=[]
        for idx1, propriété in enumerate(propriétés):
            for idx2, ligne in enumerate(datamoche):
                if ligne[idx1]=='x': self.datajoli[propriété].append(idx2+1)

    def getdata(self,nbpropriétés):
        return dict((propriété,self.datajoli[propriété]) for propriété in list(self.datajoli.keys())[:nbpropriétés])

    def getlinecount(self):
        return(self.linecount)
    
    def getpropertycount(self):
        return(len(self.datajoli.keys()))

def créeunlien(propriétéjoli,force=False):
    global debug_msgcount

    restantes=list(set(datajoli[propriétéjoli]) - set(déjàprises))
    if (force==True and restantes) or len(restantes)==1:
        solution[propriétéjoli]=min(restantes)
        déjàprises.append(min(restantes))
        print(f"{debug_msgcount} - creating link between {propriétéjoli} and {min(restantes)}. Forced : {force}")
        debug_msgcount += 1
        return(True)
    else: return(False)

def créeunliendeforce():
    for propriétéjoli in datajoli:
        if propriétéjoli in solution.keys(): continue
        if créeunlien(propriétéjoli,True): 
            return True
    return False

def issolutionvalid(solution,nbpropriétés,nblignes):
    return(len(solution)==nblignes)

datamanager=DataManager()
datamanager.readcsv("test_manuel_2.3.csv")
nbpropriétés=datamanager.getlinecount()
datajoli=None
debug_msgcount = 0

while True:
    déjàprises=[]
    solution={}
    datajoli=datamanager.getdata(nbpropriétés)
    while not issolutionvalid(solution,nbpropriétés,datamanager.getlinecount()):
        for propriétéjoli in datajoli:
            if propriétéjoli in solution.keys(): continue
            if créeunlien(propriétéjoli):
                break
        else: 
            if créeunliendeforce()==False: break            
    if not issolutionvalid(solution,nbpropriétés,datamanager.getlinecount()) and nbpropriétés<datamanager.getpropertycount():
        nbpropriétés+=1
        continue
    solution = dict(sorted(solution.items()))
    print(solution)
    break