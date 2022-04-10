import copy
import csv
import tkinter as tk
from tkinter import filedialog


class Sheet: 
    # line number of the first line as it appear in the actual spreadsheet
    g_print_lines_offset: int = 0
    g_real_line_count: int = 0

    def readcsv(self,csv_filepath):
        rawdata=None
        with open(csv_filepath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            rawdata = list(reader)

        self.property_names = [str.strip(name) for name in rawdata.pop(0)]
        self.property_names[0] = self.property_names[0][1:] # corrects that weird ass bug about first property name
        self.lines = []

        Sheet.g_print_lines_offset = 2 # With the properties row, the first real row is number 2
        while not any(rawdata[0]):
            Sheet.g_print_lines_offset += 1
            rawdata.pop(0)

        for raw_line in rawdata:
            self.lines.append([])
            for property in range(len(raw_line)):
                if raw_line[property] == 'x':
                    self.lines[-1].append(property)
        
        # remove any trailing empty lines
        while not any(self.lines[-1]):
            self.lines.pop()
        
        Sheet.g_real_line_count = self.get_line_count()

        print(f"print offset: {Sheet.g_print_lines_offset}, real line count: {Sheet.g_real_line_count}") 
        
    # Gets the list of properties the given `line` verifies
    def get_properties(self, line):
        return self.lines[line]

    # Gets the list of lines verifying the given `properties`
    def get_lines(self, property):
        return [i for i, properties in enumerate(self.lines) if property in properties]

    def get_line_count(self):
        return len(self.lines)

    def get_property_count(self):
        return len(self.property_names)

    def get_property_name(self, property):
        return self.property_names[property]

    def get_lines_with(self, property):
        return [idx for idx, line in enumerate(self.lines) if property in line]

    def get_sheet_up_to_line(self, max_line):
        newsheet = Sheet()
        newsheet.property_names = self.property_names
        newsheet.lines = self.lines[:max_line]
        return newsheet

def get_number_printed_size(number: int):
    return len(str(number))

class Solution:
    def __init__(self, sheet: Sheet):
        self.sheet = sheet
        self.properties = [None] * self.sheet.get_property_count()

    def get_line_of(self, property):
        return self.properties[property]
    
    def get_property_of(self, line):
        try:
            return self.properties.index(line)
        except ValueError:
            return None

    def get_first_free_property(self, after=None):
        try:
            if after is None: after = -1
            return self.properties.index(None, after+1)
        except ValueError:
            return None

    def set_line_property(self, line, property):
        old_property = self.get_property_of(line)
        if old_property is not None:
            self.properties[old_property] = None
        self.properties[property] = line

    def print(self, max_line=None):
        if max_line == Sheet.g_real_line_count:
            max_line = None

        sheet = self.sheet if max_line is None else self.sheet.get_sheet_up_to_line(max_line)

        print(f"Solution with {'all lines' if max_line is None else f'the first {max_line} lines'}")


        line_count_max_len = get_number_printed_size(sheet.get_line_count() + Sheet.g_print_lines_offset)

        # Property names
        header_line = ""
        header_line += " " * line_count_max_len
        header_line += "   " # for the " - "
        for property in range(sheet.get_property_count()):
            header_line += "|" + sheet.get_property_name(property)
        print(header_line)

        for line in range(sheet.get_line_count()):
            line_str = ""
            line_str += " " * (line_count_max_len - get_number_printed_size((line + Sheet.g_print_lines_offset) if (line + Sheet.g_print_lines_offset) > 0 else 1))
            line_str += str(line + Sheet.g_print_lines_offset)
            line_str += " - "

            for property in range(sheet.get_property_count()):
                line_str += "|"

                if self.properties[property] == line:
                    line_str += "X" * len(sheet.get_property_name(property))
                else:
                    line_str += "." * len(sheet.get_property_name(property))

            print(line_str)

        # Properties skip display
        skipped_after = sheet.get_property_count() - 1
        while self.get_line_of(skipped_after) is None:
            skipped_after -= 1

        skipped_str = "I had to skip "
        did_skip_intermediate = False
        for property in range(skipped_after):
            if self.get_line_of(property) is None:
                if did_skip_intermediate:
                    skipped_str += ", "
                did_skip_intermediate = True
                skipped_str += self.sheet.get_property_name(property)

        if skipped_after < sheet.get_property_count():
            if did_skip_intermediate:
                skipped_str += " and"
            skipped_str += " everything after "
            skipped_str += sheet.get_property_name(skipped_after)
        elif not did_skip_intermediate:
                skipped_str += "no properties, every single one got used"
            
        print(skipped_str)
            

def get_solution_targetting(target_property: int, sheet: Sheet, current_solution: Solution, ignoring_lines=[]):
    matching_lines = [line for line in sheet.get_lines_with(target_property) if line not in ignoring_lines]

    # we reverse to try latest line first, as it is always empty
    for line in reversed(matching_lines):
        replaced_property = current_solution.get_property_of(line)

        new_solution = copy.deepcopy(current_solution)
        new_solution.set_line_property(line, target_property)
        
        if replaced_property is not None:
            new_solution = get_solution_targetting(replaced_property, sheet, new_solution, ignoring_lines + [line])

        if new_solution is not None:
            return new_solution
    
    return None


# Get the best solution for given sheet
def get_best_solution_for(sheet: Sheet, current_solution: Solution):
    target_property = None
    new_solution = None
    
    while new_solution is None:
        target_property = current_solution.get_first_free_property(after=target_property)

        if target_property is None:
            return current_solution

        new_solution = get_solution_targetting(target_property, sheet, copy.deepcopy(current_solution))

    return new_solution
            

### MAIN #### 

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()

sheet = Sheet()
sheet.readcsv(file_path)


solution = Solution(sheet)


for max_line in range(1, sheet.get_line_count() + 1):
    solution = get_best_solution_for(sheet.get_sheet_up_to_line(max_line), solution)
    solution.print(max_line)


input("Press any key to exit...")
