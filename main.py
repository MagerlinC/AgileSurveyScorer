import csv
being_question_indexes = [8, 9]
doing_question_indexes = [10]


def main():
    file_path = "./answers/testanswers.csv"
    company_doing = 0
    company_being = 0
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for (index, row) in enumerate(reader):
            if(index > 0): # first row is headers
                doing_score, being_score = get_answer_score(row)
                company_doing += doing_score
                company_being += being_score
                print(f"Company scored - Doing: {company_doing}, Being: {company_being}. Disparity: {abs(company_being - company_doing)}")


def get_answer_score(answer_data):
    doing_score = 0
    being_score = 0
    for(index, answer) in enumerate(answer_data):
        if(index in doing_question_indexes):
            doing_score += 1 if "yes" in answer.lower() else 0
        elif(index in being_question_indexes):
            being_score += likert_to_int(answer)
    return (doing_score, being_score)

def likert_to_int(likert_val):
    conversion_dict = {
        "strongly agree": 2,
        "agree": 1,
        "neutral": 0,
        "disagree": -1,
        "strongly disagree": -2
    }
    return conversion_dict[likert_val.lower()]


if __name__ == "__main__":
    main()