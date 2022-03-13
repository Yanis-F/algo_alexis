from calendar import c
import csv

class DataManager: 
    def readcsv(self,fichiercsv):
        rawdata=None
        with open(fichiercsv, newline='') as csvfile:
            reader = csv.reader(csvfile)
            rawdata=list(reader)

        self.properties = rawdata.pop(0)
        self.linecount=len(rawdata)
        self.data = [[] for _ in range(len(self.properties))]

        for property_idx in range(len(self.properties)):
            for line_idx, line in enumerate(rawdata):
                if line[property_idx] == 'x':
                    self.data[property_idx].append(line_idx + 1)

    def getdata(self):
        return self.data

    def getlinecount(self):
        return self.linecount
    

class Event:
    def __init__(self):
        self.property_idx = None
        self.line_idx = None
        self.affected_properties = []

class Graph:
    def __init__(self, data):
        self.data = data
        self.solution = [None] * len(self.data)
        self.link_stack = []

    def push_link(self, property_idx, line_idx):
        assert(self.solution[property_idx] == None)

        event = Event()
        event.property_idx = property_idx
        event.line_idx = line_idx
        event.affected_properties = []

        for idx in range(len(self.data)):
            if line_idx in self.data[idx]:
                self.data[idx].remove(line_idx)
                event.affected_properties.append(idx)

        self.link_stack.append(event)
        self.solution[property_idx] = line_idx

    def pop_link(self):
        event = self.link_stack.pop()

        self.solution[event.property_idx] = None

        for property_idx in event.affected_properties:
            self.data[property_idx].append(event.line_idx)
            self.data[property_idx].sort()

    def get_possible_lines_for(self, property_idx):
        return self.data[property_idx]
        

MAXIMUM_SKIP_ALLOWED = 5

def print_solution(solution):
    print("SOLUTION FOUND")
    print("")
    for property_idx, line in enumerate(solution):
        print(f"\t{datamanager.properties[property_idx]} - {line}")

    print("")
    print("")
    print("")

solution = []
solution_score = None

def register_solution(new_solution):
    global solution
    global solution_score

    score = new_solution.count(lambda x: x != None)
    
    if (solution_score == None or score > solution_score):
        solution = new_solution.copy()
        solution_score = score

    elif (solution_score == score):
        for i in range(len(solution)):
            if solution[i] == None and new_solution[i] != None:
                solution = new_solution.copy()
                solution_score = score
                break
            if new_solution[i] == None:
                return
    else:
        print(f"found not as good solution, score is only {score}")
    
    print(f"Found new solution that uses {score} lines !") # <-- prints score = 0


def explore_graph_rec(graph, property_idx, current_skip_count):
    if (property_idx == len(graph.data)):
        register_solution(graph.solution)
        return

    all_possible_connections = graph.get_possible_lines_for(property_idx)

    if not all_possible_connections and current_skip_count < MAXIMUM_SKIP_ALLOWED:
        explore_graph_rec(graph, property_idx + 1, current_skip_count + 1)

    for possible_connection in all_possible_connections:
        graph.push_link(property_idx, possible_connection)
        explore_graph_rec(graph, property_idx + 1, current_skip_count)
        graph.pop_link()



### MAIN #### 


datamanager = DataManager()
datamanager.readcsv('test_manuel_2.3.csv')

graph = Graph(datamanager.data)
while (solution == []):
    print(f"Starting exploration with {MAXIMUM_SKIP_ALLOWED} skips allowed")
    explore_graph_rec(graph, 0, 0)
    MAXIMUM_SKIP_ALLOWED += 1
print_solution(solution)