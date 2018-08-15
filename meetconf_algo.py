# coding: utf-8

import csv
import os
from collections import OrderedDict
from itertools import permutations, product
from collections import defaultdict
import math

TOTAL_NUM_BLOCKS = 3

'''
Return a copy of a list with where duplicates are pruned.

Keeps 1 element if 2+ identical elts exist in the original input.

All list elts must be hashable.

Helper for Student constructor. 
'''
def list_without_duplicates(input_list):
    return list(OrderedDict.fromkeys(input_list))


'''
A student in MEET signing up for MEETConf.

choice_list_ordered should have strings representing class names. Must have the same number of unique elements as
TOTAL_NUM_BLOCKS (the number of class times offered). (Otherwise throws exception)

Name is the (string) name of the student, year is a string representing the class year of the student.
'''
class Student:
    def __init__(self, name, year, choice_list_ordered=[]):
        self.name = name
        choices_pruned = list_without_duplicates(choice_list_ordered)
        self.choice_list_ordered = choices_pruned
        if len(choices_pruned) < TOTAL_NUM_BLOCKS:
            # instead of breaking, could just assign them to a random class, or one that is under capacity,
            #   or put them in the same class for multiple blocks
            #   (would need changes to the code for any of these modifications)
            raise Exception("Student with name {} chose only {} classes ({} required)".format(
                    name, str(len(choices_pruned)), TOTAL_NUM_BLOCKS
                ))

        self.year = year
        self.classes_assigned = [None,None,None]

'''
Get a list of students from a csv of their preferences.

Name/year pairs should be unique. I recommend asking for full names in the form, or creating a dropdown,
to make it easier to check who is missing. 

input_filename must be a string representing the path to a csv from the working directory (from 
which this file was run). The csv must have columns titled Name, Year, First Choice, Second Choice, and Third Choice. 

Assumes that every student will choose 3 distinct classes. 
'''
def load_students(input_filename):
    students = []
    filepath = os.path.abspath(input_filename)
    with open(filepath, 'rt') as form_responses_csv:
        reader = csv.DictReader(form_responses_csv)
        for row in reader:
            students.append(
                Student(
                    row['Name'],
                    row['Year'],
                    ([
                        row['First Choice'],
                        row['Second Choice'],
                        row['Third Choice'] #NOTE: assumes TOTAL_NUM_BLOCKS == 3
                    ])
                )
            )
    return students


def clear_assignments(): #for debugging
    for student in students:
        student.classes_assigned = [None,None,None]
    print ('assignments cleared')

##helper for assign
def assign_students_for_class(class_name, students_in_class, num_blocks_for_class=TOTAL_NUM_BLOCKS):
    num_assignments = 0
    for start_block in range(TOTAL_NUM_BLOCKS): #if you dont do this and everyone has block 1 filled, blocks 2 and 3 wont be tried
        next_block_to_fill = start_block
        for student in (students_in_class):
            if student.classes_assigned[next_block_to_fill] == None and class_name not in student.classes_assigned:
                student.classes_assigned[next_block_to_fill] = class_name
                next_block_to_fill = (next_block_to_fill + 1) % num_blocks_for_class
                num_assignments += 1
    return num_assignments

'''
Assigns students to classes.

For a given class, keeps the size roughly equal between "blocks" (sessions in which the class is taught). Assumes
3 blocks total. If the number of blocks is changed, the number of class choices should also be changed.

Guarantees that students will get into their chosen classes. Order of students' preferences not taken into account.

Does NOT take capacity of classes into account, since different rules for who gets into which over-subscribed class
 are possible (by year, by preference order, by order of signup, etc). The input sheet should be manually adjusted to 
 reflect class capacity constraints. (For example, if there are too many students who chose "Painting", excess students' 
 preferences should be changed in the spreadsheet so that they are not assigned to "Painting" (some under-subscribed 
 class should fill that space instead).  
 
The year this script was used, Zumba was only available in blocks 1 and 2. Commented-out code handles this special case.
'''
def assign(students, verbose=False):
    class_name_to_students_list = defaultdict(lambda:[])
    for student in students:
        for class_name in student.choice_list_ordered:
            class_name_to_students_list[class_name].append(student)

    #GREEDY
    #possible bug: zumba has fewer blocks, so some students may never get assignments for it
    #workaround: assign blocks for zumba first
    # class_name_to_num_blocks = defaultdict(lambda:TOTAL_NUM_BLOCKS)
    # class_name_to_num_blocks["Zumba / Dance Dance Revolution (Adina)"] = 2 #SPECIAL CASE: zumba only available in blocks 1 or 2

    total_assignments = sum([len(student.choice_list_ordered) for student in students])
    num_assignments = 0
    print('assignments to make: ' + str(total_assignments))

    while num_assignments < total_assignments:
        prev_num_assignments = num_assignments
        # if num_assignments == 0: ##fill zumba first
        #     zumba = "Zumba / Dance Dance Revolution (Adina)"
        #     num_blocks_for_zumba = 2
        #     num_assignments += assign_students_for_class(zumba, class_name_to_students_list[zumba], class_name_to_num_blocks[zumba])
        for class_name in class_name_to_students_list:
            # num_assignments += assign_students_for_class(class_name, class_name_to_students_list[class_name],
            #   class_name_to_num_blocks[class_name])
            num_assignments += assign_students_for_class(class_name, class_name_to_students_list[class_name])
        print (num_assignments)
        if prev_num_assignments == num_assignments:
            print('no new assignments found! check output for blank spaces!')
            break
    
    if verbose: #prints out the number of students per class in each block
        for class_name in class_name_to_students_list:
            print (class_name + '\n')
            for block_num in range(TOTAL_NUM_BLOCKS):
                num_students = len([student for student in students if student.classes_assigned[block_num] == class_name])
                print ('\tBlock {}: {}\n'.format(str(block_num), str(num_students)))

### writing the output csv
def save_assignments(students, output_filename):
    with open(output_filename, 'wt') as output_file:
        fieldnames = ["Name","Year","Block 1", "Block 2", "Block 3"]
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for student in students: 
            writer.writerow({
                "Name": student.name, 
                "Year": student.year, 
                "Block 1": student.classes_assigned[0],
                "Block 2": student.classes_assigned[1],
                "Block 3": student.classes_assigned[2]
            })

### checking for duplicate names
def check_for_duplicate_names(students):
    names_seen = set([])
    for student in students:
        name_year = student.name.lower() + ' (' + student.year + ')'
        if name_year in names_seen:
            raise Exception("duplicate name: " + name_year)
        names_seen.add(name_year)

if __name__=='__main__':
    input_filename = input('What is the filepath to the input? \nFor example, if this script is run from the desktop and ' +
             "the csv with the students to class preferences is called student_prefs.csv and is also on the desktop, write " +
             "student_prefs.csv (but without the quotation marks!) \n")

    while not input_filename or input_filename[-4:] != ".csv":
        input_filename = input("Sorry, didn't get that. Please type in a valid csv file name and press return.\n")
    students = None
    while students == None:
        try:
            students = load_students(input_filename)
        except IOError or KeyError:
            input_filename = input("\nI can't read that :( . Make sure the input filename is a csv with columns titled Name, Year, First Choice, " +
                  "Second Choice, and Third Choice (case sensitive!).\n\nType the input filename again:\n")

    check_for_duplicate_names(students)
    assign(students, True)
    save_assignments(students, 'meetconf_assignments_output.csv')
    print('Saved assignments to meetconf_assignments_output.csv . Good luck at MEETConf!')
