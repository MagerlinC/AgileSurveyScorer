import csv
import sys
import os
import functools 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
# Indexes in the CSV file which are answers to questions about BEING agile
being_question_indexes = [9, 10, 12, 13, 14, 16, 17, 18, 19, 21, 22, 24, 25, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]
# Indexes in the CSV file which are answers to questions about DOING agile
doing_question_indexes = [11, 15, 20, 23, 26]
# Indexes in the CSV file where the answers are asked inverted (eg. DONT you instead of DO you)
inverted_question_indexes = [14, 25, 28, 34, 37]

# The maximum being score a single answer can give
SINGLE_ANSWER_MAX_BEING = len(being_question_indexes) * 2 # Equivalent of answering "Strongly Agree" to every being question
# The maximum doing score a single answer can give
SINGLE_ANSWER_MAX_DOING = len(doing_question_indexes) + 1 # Equivalent of answering "Yes" to every doing question, +1 from YES EVERY

AGILE_PRINCIPLES = [
    "Our highest priority is to satisfy the customer through early and continuous delivery of valuable software.",
    "Welcome changing requirements, even late in development. Agile processes harness change for the customer's competitive advantage.",
    "Deliver working software frequently, from a couple of weeks to a couple of months, with a preference to the shorter timescale.",
    "Business people and developers must work together daily throughout the project.",
    "Build projects around motivated individuals. Give them the environment and support they need, and trust them to get the job done.",
    "The most efficient and effective method of conveying information to and within a development team is face-to-face conversation.",
    "Working software is the primary measure of progress.",
    "Agile processes promote sustainable development. The sponsors, developers, and users should be able to maintain a constant pace indefinitely.",
    "Continuous attention to technical excellence and good design enhances agility.",
    "Simplicity--the art of maximizing the amount of work not done--is essential.",
    "The best architectures, requirements, and designs emerge from self-organizing teams.",
    "At regular intervals, the team reflects on how to become more effective, then tunes and adjusts its behavior accordingly."
]
PRINCIPLE_QUESTION_MAP = {1: [9, 10], 2: [12, 13]}


def main():
    boxplot_data = []
    directory = "./answers/"
    sorted_files = os.listdir(directory)
    sorted_files.sort()
    input_data = []
    questions = []
    for filename in sorted_files:
        if filename.endswith(".csv") and "aggr" in filename:
            with open(directory + filename, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                company_data = []
                for (index, row) in enumerate(reader):
                    if(index > 0):
                        company_data.append(row)
                    else:
                        questions = (row)
                input_data += company_data
                being, doing, being_answers, doing_answers = get_company_scores(company_data, False)
                # print(f"{filename} - Avg. Being: {being_avg}/{SINGLE_ANSWER_MAX_BEING}, Avg. Doing: {doing_avg}/{SINGLE_ANSWER_MAX_DOING}")
                boxplot_data.append({
                    "name": filename.replace(".csv", ""),
                    "being_answers": being_answers,
                    "doing_answers": doing_answers
                })
        else:
            continue
    #show_boxplots(boxplot_data)
    get_principle_breakdown(input_data)


def get_principle_breakdown(input_data):
    principle_score_list = []
    for (principle, principle_question_indexes) in PRINCIPLE_QUESTION_MAP.items():
        principle_averages = []
        for question_index in principle_question_indexes:
            principle_averages.append(get_col_average(question_index, input_data))
        principle_total_score = sum(principle_averages)
        principle_avg_score = principle_total_score / len(principle_averages)
        principle_score_list.append(principle_avg_score)
    # Print results
    print("*** Score per Principle ***")
    for (index, score) in enumerate(principle_score_list):
        print("Nr. | Score | Principle |")
        print(f"  {index + 1} | {round(score, 3)} | {AGILE_PRINCIPLES[index]}")



def get_col_average(col_indx, input_data):
    col_averages = []
    for (index, row) in enumerate(input_data):
        if(index > 0): # Ignore questions in row 0
            col_averages.append(likert_to_int(row[col_indx]))
    return sum(col_averages) / len(col_averages)


def calc_being_correlations(file_path):
    original_stdout = sys.stdout # Save a reference to the original standard output
    answer_data = []
    # Map of question nr to possible answers for that question, eg. 3:["Less than 1 Year", "1-2 years"]
    questions = {}
    # For each question find unique answer options
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for (index, row) in enumerate(reader):
            if(index > 0):
                answer_data.append(row) # Build list of all answers
            if(index == 0): # First row is headers
                for (index, val) in enumerate(row): # Every question
                    questions.setdefault(index, []) # Store question number, empty list in map
            else:
                for (index, val) in enumerate(row):
                    cur_opts = questions.get(index)
                    if(not val in cur_opts): # Add the answer if this answer isn't already in the list of possible answers
                        cur_opts.append(val)
    # Remove output from previous runs
    os.remove("output.csv")
    # For every unique question:option...
    for (question_nr, question_opts) in questions.items():
        if(question_nr > 1): # Question 0 and 1 are company and timestamp, we don't care
            for opt in question_opts:
                # Get a filtered data set of answers that have this question:opt combination
                filtered_data = list(filter(lambda row: row[question_nr] == opt, answer_data))
                num_answer_matches = len(filtered_data)
                # Get being score for the filtered data set
                being_score, doing_score, being_answers, doing_answers = get_company_scores(filtered_data, False)
                # Create a unique key for that question and answer combination
                combination_key = str(question_nr) + ":" + opt
                # Calculate average being for that combination
                being_avg = round(sum(being_answers) / len(being_answers), 2)
                # Print to file
                with open('output.csv', 'a') as f:
                    sys.stdout = f # Change the standard output to the file we created.
                    print("\"" + combination_key + "\"" + "," + str(being_avg) + "," + str(num_answer_matches))
                sys.stdout = original_stdout # Reset the standard output to its original value
               

   

def val_to_percentage(val, max):
    return round(val / max * 100, 4)

def combine_lists_alternating(list1, list2):
    output = []
    for (index, elem) in enumerate(list1):
        output.append(elem)
        output.append(list2[index])
    return output

def show_boxplots(company_data):
    doing_answers = []
    being_answers = []
    for company_answer in company_data:
        doing_answers.append(company_answer.get("doing_answers"))
        being_answers.append(company_answer.get("being_answers"))
    # Multiple box plots on one Axes
    fig, ax = plt.subplots()
    fig.suptitle('Team "Being" Agile Scores', fontsize=14, fontweight='bold')
    ax.set_ylabel('Being Score')
    ax.set_ylim([-SINGLE_ANSWER_MAX_BEING - 1, SINGLE_ANSWER_MAX_BEING + 1])

    being_labels = list(map(lambda company_answer: company_answer.get("name") + ": Be", company_data))
    #doing_labels = list(map(lambda company_answer: company_answer.get("name") + ": Do", company_data))
    plt.margins(0.2)

    # Convert "being" score answers to percentage of max possible per answer
    #being_percentage_answers = list(map(lambda answer: list(map(lambda inner_answer: val_to_percentage(inner_answer, SINGLE_ANSWER_MAX_BEING), answer)), being_answers))
    #doing_percentage_answers = list(map(lambda answer: list(map(lambda inner_answer: val_to_percentage(inner_answer, SINGLE_ANSWER_MAX_DOING), answer)), doing_answers))
    ax.boxplot(being_answers, labels=being_labels) 
    #savefig('boxplots.jpg', bbox_inches='tight', dpi=500)
    plt.show()

    
    
def get_company_scores(iterable, has_headers = True):
    company_doing = 0
    company_being = 0
    doing_answers = []
    being_answers = []
    num_answers = 0
    for (index, row) in enumerate(iterable):
        num_answers += 1
        if(not has_headers or index > 0): # first row is headers
            doing_score, being_score = get_answer_score(row)
            company_doing += doing_score
            company_being += being_score
            doing_answers.append(doing_score)
            being_answers.append(being_score)
    #max_doing = num_answers * SINGLE_ANSWER_MAX_DOING
    #max_being = num_answers * SINGLE_ANSWER_MAX_BEING
    return (company_being, company_doing, being_answers, doing_answers)

def get_answer_score(answer_data):
    doing_score = 0
    being_score = 0
    for(index, answer) in enumerate(answer_data):
        if(index in doing_question_indexes):
            doing_score += 1 if "yes" in answer.lower() else 0
            doing_score += 1 if "every" in answer.lower() else 0
        elif(index in being_question_indexes):
            being_score += (-1 * likert_to_int(answer)) if index in inverted_question_indexes else likert_to_int(answer)
    return (doing_score, being_score)

def likert_to_int(likert_val):
    if(likert_val):
        conversion_dict = {
            "strongly agree": 2,
            "agree": 1,
            "neutral": 0,
            "disagree": -1,
            "strongly disagree": -2
        }
        return conversion_dict[likert_val.lower()]
    else:
        return 0


if __name__ == "__main__":
    main()