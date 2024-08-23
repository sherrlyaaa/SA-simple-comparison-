import os
import copy
from shapely.geometry import LineString
import time

class Word:
    def __init__(self):
        self.start_coord = ()
        self.end_coord = ()
        self.orientation = 0
        self.length = 0
        self.value = ''

def load_crossword_puzzle(filename):
    crossword = []
    with open(filename, 'r') as cfile:
        puzzle = cfile.readlines()
    for line in puzzle:
        replaced = line.replace("\t", "").replace("\n", "").replace(" ", "")
        crossword.append(list(replaced))
    return crossword

def load_dictionary(filename):
    dictionary = []
    with open(filename, 'r') as dfile:
        wordslist = dfile.readlines()
    for word in wordslist:
        replaced = word.replace("\n", "")
        dictionary.append(replaced)
    return dictionary

def find_horizontal_words(crossword):
    horizontal_words = []
    for row in range(len(crossword)):
        column = 0
        while column < len(crossword[row]):
            if crossword[row][column] == '0':
                word = Word()
                word.start_coord = (row, column)
                while column < len(crossword[row]) and crossword[row][column] == '0':
                    word.length += 1
                    column += 1
                word.end_coord = (row, column - 1)
                if word.length > 1:
                    word.orientation = 0
                    horizontal_words.append(word)
            column += 1
    return horizontal_words

def find_vertical_words(crossword):
    vertical_words = []
    for column in range(len(crossword[0])):
        row = 0
        while row < len(crossword):
            if crossword[row][column] == '0':
                word = Word()
                word.start_coord = (row, column)
                while row < len(crossword) and crossword[row][column] == '0':
                    word.length += 1
                    row += 1
                word.end_coord = (row - 1, column)
                if word.length > 1:
                    word.orientation = 1
                    vertical_words.append(word)
            row += 1
    return vertical_words

def backtracking(assigned_variable_list, not_assigned_variable_list, dict):
    if len(not_assigned_variable_list) == 0:
        return assigned_variable_list

    var = not_assigned_variable_list[0]
    possible_val = get_possible_values(var, assigned_variable_list, dict)

    for val in possible_val:
        check_var = copy.deepcopy(var)
        check_var.value = val
        if check_constraint(check_var, assigned_variable_list):
            var.value = val
            result = backtracking(assigned_variable_list + [var], not_assigned_variable_list[1:], dict)
            if result is not None:
                return result
            var.value = ''

    return None

def get_possible_values(var, assigned_variable_list, dict):
    possibles_values = [val for val in dict if len(val) == var.length]
    assigned_values = [word.value for word in assigned_variable_list]
    return [val for val in possibles_values if val not in assigned_values]

def check_constraint(var, assigned_variable_list):
    for word in assigned_variable_list:
        if var.orientation != word.orientation:
            intersection = check_intersections(var, word)
            if intersection:
                intersection = intersection[0]
                var_idx = int(intersection[1] - var.start_coord[1]) if var.orientation == 0 else int(intersection[0] - var.start_coord[0])
                word_idx = int(intersection[0] - word.start_coord[0]) if word.orientation == 1 else int(intersection[1] - word.start_coord[1])
                if var.value[var_idx] != word.value[word_idx]:
                    return False
    return True

def check_intersections(w1, w2):
    line1 = LineString([w1.start_coord, w1.end_coord])
    line2 = LineString([w2.start_coord, w2.end_coord])

    intersection_point = line1.intersection(line2)
    if not intersection_point.is_empty:
        return [intersection_point.coords[0]] 
    return []

def insert_word_to_puzzle(crossword, word, coord, orientation):
    pos_count = 0
    for char in word:
        if orientation == 0:
            crossword[coord[0]][coord[1] + pos_count] = char
        else:
            crossword[coord[0] + pos_count][coord[1]] = char
        pos_count += 1
    return crossword

start_time = time.time()
current_dir = os.path.dirname(os.path.abspath(__file__))
cw_puzzle = load_crossword_puzzle(os.path.join(current_dir, "10kosong.txt"))
dict_words = load_dictionary(os.path.join(current_dir, "words.txt"))
horizontal_words = find_horizontal_words(cw_puzzle)
vertical_words = find_vertical_words(cw_puzzle)
total_words = horizontal_words + vertical_words
assign_var_list = []
suggested_solution = backtracking(assign_var_list, total_words, dict_words)
print("---------- Crossword ---------")
for line in cw_puzzle:
    print(line)
print("------------------------------")

print("---------- Solution ----------")

if suggested_solution is None:
    print("No solution found")
else:
    for word in suggested_solution:
        cw_puzzle = insert_word_to_puzzle(cw_puzzle, word.value, word.start_coord, word.orientation)

    for line in cw_puzzle:
        print(line)

print("------------------------------")
end_time = time.time()
print(f"running time: {end_time-start_time}")
