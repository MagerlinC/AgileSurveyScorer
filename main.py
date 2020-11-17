import csv
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
SINGLE_ANSWER_MAX_DOING = len(doing_question_indexes) # Equivalent of answering "Yes" to every doing question


def main():
    # TODO, do this for every file in the answers folder
    file_paths = ["./answers/testanswers.csv"]
    boxplot_data = []
    for file in file_paths:
        name, being, doing, max_being, max_doing, being_answers, doing_answers = get_company_scores(file)
        being_percent = round(being / max_being * 100, 2)
        doing_percent = round(doing / max_doing * 100, 2)
        print(f"{name} scored - Being: {being} ({being_percent}%), Doing: {doing} ({doing_percent}%). Disparity: {abs(being_percent - doing_percent)} percentage points.")
        boxplot_data.append({
            "company_name": name,
            "being_score": being,
            "doing_score": doing,
            "max_being_score": max_being,
            "max_doing_score": max_doing,
            "being_answers": being_answers,
            "doing_answers": doing_answers
        })
    show_boxplots(boxplot_data)

def val_to_percentage(val, max):
    return round(val / max * 100, 4)

def show_boxplots(company_data):
    doing_answers = []
    being_answers = []
    for company_answer in company_data:
        doing_answers.append(company_answer.get("doing_answers"))
        being_answers.append(company_answer.get("being_answers"))
    max_being = 2 * len(being_answers) # Max points for being answers is "STRONGLY AGREE" (2) per.
    max_doing = len(doing_answers) # Max points for doing answers is answering "yes" (1) to all doing questions.
    # Multiple box plots on one Axes
    fig, ax = plt.subplots()
    fig.suptitle('Company Being/Doing Scores', fontsize=14, fontweight='bold')
    ax.set_ylabel('Percentage Scored') 
    ax.set_ylim([0,100])

    labels = list(map(lambda company_answer: company_answer.get("company_name"), company_data))
    plt.margins(0.2)

    # Convert "being" score answers to percentage of max possible
    being_percentage_answers = list(map(lambda answer: list(map(lambda inner_answer: val_to_percentage(inner_answer, SINGLE_ANSWER_MAX_BEING), answer)), being_answers))
    ax.boxplot(being_percentage_answers, labels=labels)
    #savefig('boxplots.jpg', bbox_inches='tight', dpi=500)
    plt.show()
    
def get_company_scores(file_path):
    company_doing = 0
    company_being = 0
    company_name = None
    doing_answers = []
    being_answers = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        num_answers = 0
        for (index, row) in enumerate(reader):
            num_answers += 1
            if(index > 0): # first row is headers
                if(company_name == None):
                    company_name = row[0] # First col is company name
                doing_score, being_score = get_answer_score(row)
                company_doing += doing_score
                company_being += being_score
                doing_answers.append(doing_score)
                being_answers.append(being_score)
    max_doing = num_answers * len(doing_question_indexes)
    max_being = num_answers * len(being_question_indexes) * 2 # 2 pts for answering "STRONGLY agree" to everything is max
    return (company_name, company_being, company_doing, max_being, max_doing, being_answers, doing_answers)

def get_answer_score(answer_data):
    doing_score = 0
    being_score = 0
    for(index, answer) in enumerate(answer_data):
        if(index in doing_question_indexes):
            doing_score += 1 if "yes" in answer.lower() else 0
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