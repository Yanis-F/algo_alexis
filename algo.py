import copy
import csv
import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog
from typing import List


TICKED_BUT_NO_GROUP_STRING = "-"

@dataclass(frozen=True)
class Cell:
    property: int
    line: int

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
        if not self.property_names[0].isalpha(): self.property_names[0] = self.property_names[0][1:] # corrects that weird ass bug about first property name
        self.lines = []
        self.groups = {}
        self.grouppedwith = {}

        Sheet.g_print_lines_offset = 2 # With the properties row, the first real row is number 2
        while not any(rawdata[0]):
            Sheet.g_print_lines_offset += 1
            rawdata.pop(0)

        for lineidx, raw_line in enumerate(rawdata):
            self.lines.append([])
            for property in range(len(raw_line)):
                cell_content = raw_line[property]
                if cell_content:
                    self.lines[-1].append(property)

                    if cell_content != TICKED_BUT_NO_GROUP_STRING:
                        if cell_content not in self.groups:
                            self.groups[cell_content] = []
                        self.groups[cell_content].append(Cell(property, lineidx))
        
        # safety check
        for group_name, group_cells in self.groups.items():
            if len(group_cells) == 1:
                print(f"Warning: Only one cell in group '{group_name}'. This doesn't add any constaint and will always be valid")

        # remove any trailing empty lines
        while not any(self.lines[-1]):
            self.lines.pop()
        
        Sheet.g_real_line_count = self.get_line_count()

        for line in range(self.get_line_count()):
            for prop in range(self.get_property_count()):
                self.grouppedwith[Cell(prop, line)] = [Cell(prop, line)]
        
        for grouped_cells in self.groups.values():
            for cell in grouped_cells:
                self.grouppedwith[cell] = group_cells


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

    def get_group_name_of(self, cell: Cell):
        for group_name, all_group_cells in self.groups.items():
            for groupcell in all_group_cells:
                if cell == groupcell:
                    return group_name
        return None

    def get_group_cells(self, cell: Cell) -> List[Cell]:
        return self.grouppedwith[cell]

    def get_sheet_up_to_line(self, max_line_count):
        newsheet = Sheet()
        newsheet.property_names = self.property_names
        newsheet.lines = copy.deepcopy(self.lines[:max_line_count])

        newsheet.grouppedwith = {}
        newsheet.groups = {}

        for line in range(self.get_line_count()):
            for prop in range(self.get_property_count()):
                newsheet.grouppedwith[Cell(prop, line)] = [Cell(prop, line)]

        for group_name, group_cells in self.groups.items():
            if not all(line < max_line_count  for line in [cell.line for cell in group_cells]):
                for c in group_cells:
                    if c.line < max_line_count:
                        newsheet.lines[c.line].remove(c.property)
                continue # The group will never be satisfied, we delete and forget it

            newsheet.groups[group_name] = group_cells
            for c in group_cells:
                newsheet.grouppedwith[c] = group_cells

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

    def get_free_properties(self):
        for property, line in enumerate(self.properties):
            if line is None:
                yield property

    def set_property_line(self, property, line):
        old_property = self.get_property_of(line)
        if old_property is not None:
            self.properties[old_property] = None
        self.properties[property] = line

    def is_ticked(self, cell: Cell) -> bool:
        return self.properties[cell.property] == cell.line

    def tick_all(self, cells: List[Cell]):
        if __debug__:
            for c in cells:
                assert self.get_line_of(c.property) is None

        for c in cells:
            self.set_property_line(c.property, c.line)

    def untick_all(self, cells: List[Cell]):
        if __debug__:
            for c in cells:
                assert self.is_ticked(c)

        for c in cells:
            self.set_property_line(c.property, None)



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
        while skipped_after > 0 and self.get_line_of(skipped_after) is None:
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
                skipped_str += " and "
            skipped_str += "everything after "
            skipped_str += sheet.get_property_name(skipped_after)
        elif not did_skip_intermediate:
                skipped_str += "no properties, every single one got used"
            
        print(skipped_str)
            

def get_solution_adding_property(target_property: int, sheet: Sheet, solution: Solution, ignoring_lines=[]):
    # solution.print(sheet.get_line_count())
    # print(f"Target property: {str(target_property)}, ignoring lines: [{','.join([str(line) for line in ignoring_lines])}]")

    matching_lines = [line for line in sheet.get_lines_with(target_property) if line not in ignoring_lines]

    # we reverse to try latest line first, as it is always empty
    for line in reversed(matching_lines):
        stacked_deletion = []

        new_cell_group = sheet.get_group_cells(Cell(target_property, line))

        for cell in new_cell_group:
            ln = solution.get_line_of(cell.property)
            if ln is not None:
                stacked_deletion.append(Cell(cell.property, ln))

        solution.untick_all(stacked_deletion)  ####################### PUSH DELETION
        solution.tick_all(new_cell_group) ############################ PUSH ADDITION

        added_lines = [c.line for c in new_cell_group]
        
        if all([get_solution_adding_property(new_target_property, sheet, solution, ignoring_lines + added_lines) for new_target_property in [c.property for c in stacked_deletion]]):
            return True

        solution.untick_all(new_cell_group) ########################## POP ADDITION
        solution.tick_all(stacked_deletion) ########################## POP DELETION

    return False


# Get the best solution for given sheet
def get_best_solution_for(sheet: Sheet, solution: Solution):
    for free_property in solution.get_free_properties():
        if get_solution_adding_property(free_property, sheet, solution):
            return
            

### MAIN #### 

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()

sheet = Sheet()
sheet.readcsv(file_path)


solution = Solution(sheet)


for max_line in range(1, sheet.get_line_count() + 1):
    get_best_solution_for(sheet.get_sheet_up_to_line(max_line), solution)
    solution.print(max_line)


input("Press any key to exit...")
