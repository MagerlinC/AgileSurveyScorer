import csv
# Indexes in the CSV file which are answers to questions about BEING agile
being_question_indexes = [9, 10, 12, 13, 14, 16, 17, 18, 19, 21, 22, 24, 25, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]
# Indexes in the CSV file which are answers to questions about DOING agile
doing_question_indexes = [11, 15, 20, 23, 26]
# Indexes in the CSV file where the answers are asked inverted (eg. DONT you instead of DO you)
inverted_question_indexes = [14, 25, 28, 34, 37]


def main():
    # TODO, do this for every file in the answers folder
    file_paths = ["./answers/testanswers.csv"]
    for file in file_paths:
        name, being, doing, max_being, max_doing = get_company_scores(file)
        print(f"{name} scored - Being: {being}/{max_being}, Doing: {doing}/{max_doing}. Disparity: {abs(being - doing)}")
    

def get_company_scores(file_path):
    company_doing = 0
    company_being = 0
    company_name = None
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
    max_doing = num_answers * len(doing_question_indexes)
    max_being = num_answers * len(being_question_indexes) * 2 # 2 pts for answering "STRONGLY agree"
    return (company_name, company_being, company_doing, max_being, max_doing)

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