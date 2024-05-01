from flask import Flask, render_template, request
import csv

app = Flask(__name__)

student_email = ""
student_phone = ""


@app.route("/", methods=['POST', 'GET'])
@app.route("/login", methods=['POST', 'GET'])
def login():
    return render_template("index.html")


@app.route("/question", methods=['POST', 'GET'])
def question():
    global student_email
    global student_phone
    if request.method == "POST":
        csv_file = open("static/csv/question.csv")
        csv_file = csv.DictReader(csv_file)
        no = []
        questions = []
        answers1 = []
        answers2 = []
        answers3 = []
        answers4 = []
        correct = []

        for store in csv_file:
            no.append(store["No"])
            questions.append(store["Question"])
            answers1.append(store["Answers1"])
            answers2.append(store["Answers2"])
            answers3.append(store["Answers3"])
            # Changed
            answers4.append(store["Answers4"])
            correct.append(store["Correct"])

        join = zip(no, questions, answers1, answers2, answers3, answers4, correct)
        join = list(join)

        choice = join

        import sqlite3
        db = sqlite3.connect("students.db")
        con = db.cursor()
        con.execute("""
            CREATE TABLE IF NOT EXISTS Students(
            pid INTEGER PRIMARY KEY,
            name TEXT,
            phone INTEGER,
            email TEXT,
            dob TEXT,
            marks TEXT
            )
            """)
        db.commit()

        student_name = request.form.get("name").capitalize()
        student_email = request.form.get("email").lower()
        student_phone = request.form.get("phone")
        student_dob = request.form.get("dob")
        if not (con.execute("SELECT * FROM Students").fetchall() == []) or con.execute(
                "SELECT * FROM Students").fetchall() == []:
            if con.execute("SELECT * FROM Students where email=? and phone=?",
                           (student_email, student_phone)).fetchone() == None:
                query = """
                        INSERT INTO Students VALUES(NULL,?,?,?,?,null)
                    """
                con.execute(query, (student_name, student_phone, student_email, student_dob))
                db.commit()

            else:
                data = con.execute("SELECT * FROM Students where email=? and phone=?",
                                   (student_email, student_phone)).fetchone()
                if not (data[5] == None or str(data[5]).startswith("0")):
                    return render_template("already.html", data=data)

        return render_template("question.html", questions=choice)


@app.route("/score", methods=["POST", "GET"])
def score():
    global student_email
    global student_phone

    csv_file = open("static/csv/question.csv")
    csv_file = csv.DictReader(csv_file)

    score = 0
    total = 30

    if request.method == "POST":
        import sqlite3
        answers = []
        choices = []
        for y in range(1, 29):
            selected = request.form.get(f"question_{y}")
            answers.append(selected)
        for x in csv_file:
            choices.append(x["Correct"])
        for i in range(0, 28):
            if str(choices[i]).lower() == str(answers[i]).lower():
                score += 1
        if not (score == 0):
            score += 3
        db = sqlite3.connect("students.db")
        cursor = db.cursor()
        cursor.execute("UPDATE Students SET marks = ? WHERE email = ? and phone = ?",
                       (f"{score}/{total}", student_email, student_phone))
        db.commit()
        return render_template("score.html", score=f"Score : {score}/{total}")


if __name__ == "__main__":
    app.run(debug=True)
