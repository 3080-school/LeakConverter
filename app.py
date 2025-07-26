from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
import os
import json
import re
import psycopg2

app = Flask(__name__)
app.secret_key = "e3f9a27f93519f8f65b47973c2b1a0f0c4d75a5c946fd7b64db36bbf3b3d8c17"

PRACTICE_DIR = "practices"
TABLE_DIR = "tables_cropped"

modules = [
    {"start": 1, "end": 27, "name": "Verbal Module 1"},
    {"start": 28, "end": 54, "name": "Verbal Module 2"},
    {"start": 55, "end": 76, "name": "Math Module 1"},
    {"start": 77, "end": 98, "name": "Math Module 2"},
]

def load_questions(practice_id):
    filepath = os.path.join(PRACTICE_DIR, f"{practice_id}.json")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_page_number(name):
    match = re.search(r"page[_-](\d+)", name)
    return int(match.group(1)) if match else 9999

@app.route("/debug_session")
def debug_session():
    return session.get("answers", {})

@app.route("/practice/<practice_id>/question/<int:q_number>", methods=["GET", "POST"])
def single_question(practice_id, q_number):
    if "user_id" not in session:
        return redirect(url_for("login"))

    questions = load_questions(practice_id)
    questions.sort(key=lambda q: int(q["id"].replace("q", "")))
    question = next((q for q in questions if int(q["id"].replace("q", "")) == q_number), None)
    
    if (q_number == 55):
        return """
        <script>
            alert('Вы успешно сдали вербал! У вас есть 10 минут перерыва.');
            window.location.href = '/practices';
        </script>
        """
    
    if not question:
        return "Вопрос не найден", 404

    table_img = None
    if question.get("has-table"):
        page_num = question.get("page")
        if page_num:
            table_img = f"{practice_id}/cropped_page_{page_num}_table.png"

    # для правильной передачи отмеченных/отвеченных
    answers = session.get("answers", {})
    marked = set(session.get("marked", []))

    if request.method == "POST":
        selected = request.form.get("answer")
        nav_action = request.form.get("nav_action", "stay")

        # Сохраняем ответ (None если пустой — тогда не засчитывается как "ответил")
        answers = answers.copy()
        if selected:
            answers[question["id"]] = selected
        else:
            # если убрал выбор — удаляем ответ
            answers.pop(question["id"], None)
        session["answers"] = answers

        # Обработка действий навигации
        current_index = questions.index(question)

        if nav_action == "next" and current_index + 1 < len(questions):
            next_q = int(questions[current_index + 1]["id"].replace("q", ""))
            return redirect(url_for("single_question", practice_id=practice_id, q_number=next_q))

        elif nav_action == "prev" and current_index > 0:
            prev_q = int(questions[current_index - 1]["id"].replace("q", ""))
            return redirect(url_for("single_question", practice_id=practice_id, q_number=prev_q))

        elif nav_action.isdigit():
            return redirect(url_for("single_question", practice_id=practice_id, q_number=int(nav_action)))

        elif nav_action == "submit":
            conn = psycopg2.connect(
                dbname='leakconverter_db',
                user='leakconverter_db_user',
                password='Sv7BeHxCht4NvZdKXsxwr9z55bEpxpCM',
                host='dpg-d224aladbo4c73eqcm6g-a',
                port='5432'
            )
            cursor = conn.cursor()

            # Замени ? на %s для psycopg2
            for qid, ans in session["answers"].items():
                cursor.execute("""
                    INSERT INTO answers (username, practice_id, question_id, answer)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (username, practice_id, question_id)
                    DO UPDATE SET answer=EXCLUDED.answer
                """, (session["user_id"], practice_id, qid, ans))
            conn.commit()
            conn.close()

            session["answers"] = {}

            # определим следующий модуль
            current_q_num = int(question["id"].replace("q", ""))
            next_module_start = None
            for m in modules:
                if m["start"] > current_q_num:
                    next_module_start = m["start"]
                    break
            if next_module_start:
                return redirect(url_for("single_question", practice_id=practice_id, q_number=next_module_start))
            else:
                return f"Все модули завершены. Ответы сохранены в БД для {session['user_id']}."
               
        return redirect(url_for("single_question", practice_id=practice_id, q_number=q_number))

    # GET — отображаем
    saved_answer = session.get("answers", {}).get(question["id"])

    # Собираем все qid в модуле
    module_start = (q_number <= 27 and 1) or (q_number <= 54 and 28) or (q_number <= 76 and 55) or 77
    module_end = (q_number <= 27 and 27) or (q_number <= 54 and 54) or (q_number <= 76 and 76) or 98
    qids_in_module = ['q%d' % i for i in range(module_start, module_end+1)]

    # answered_ids — только если не None/пусто
    answered_ids = [qid for qid in qids_in_module if answers.get(qid, '') not in [None, '']]
    marked_ids = [qid for qid in qids_in_module if qid in marked]

    return render_template("question_single.html",
                           question=question,
                           q_number=q_number,
                           table_img=table_img,
                           practice_id=practice_id,
                           selected=saved_answer,
                           answered_ids=answered_ids,
                           marked_ids=marked_ids)

@app.route('/toggle_mark', methods=['POST'])
def toggle_mark():
    qid = request.json.get('qid')
    if not qid:
        return jsonify({"error": "No question id"}), 400

    marked = set(session.get("marked", []))
    if qid in marked:
        marked.remove(qid)
        marked_status = False
    else:
        marked.add(qid)
        marked_status = True
    session["marked"] = list(marked)
    return jsonify({"marked": marked_status})

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        if not user_id or not password:
            return "Missing user ID or password", 400

        conn = psycopg2.connect(
            dbname='leakconverter_db',
            user='leakconverter_db_user',
            password='Sv7BeHxCht4NvZdKXsxwr9z55bEpxpCM',
            host='dpg-d224aladbo4c73eqcm6g-a',
            port='5432'
        )
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = %s AND password = %s", (user_id, password))
        user = c.fetchone()
        conn.close()

        if user:
            session.clear()
            session["user_id"] = user_id
            return redirect(url_for("practice_list"))
        else:
            return "Неверный логин или пароль", 403

    return render_template("login.html")

@app.route("/practices")
def practice_list():
    if "user_id" not in session:
        return redirect(url_for("login"))

    files = [f for f in os.listdir(PRACTICE_DIR) if f.endswith(".json")]
    practices = [f[:-5] for f in files]
    return render_template("practices.html", practices=practices)

@app.route("/practice/<practice_id>")
def show_practice(practice_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    questions = load_questions(practice_id)
    question_table_map = map_questions_to_tables(questions)

    module_blocks = []
    for module in modules:
        mod_questions = []
        for q in questions:
            q_num = int(q["id"].replace("q", ""))
            if module["start"] <= q_num <= module["end"]:
                mod_questions.append({
                    "id": q["id"],
                    "question": q.get("question", ""),
                    "options": q.get("choices", []),
                    "passage": q.get("passage", ""),
                    "table_img": question_table_map.get(q["id"])
                })
        module_blocks.append({
            "name": module["name"],
            "start": module["start"],
            "end": module["end"],
            "questions": mod_questions
        })

    return render_template("index.html", modules=module_blocks)

def map_questions_to_tables(questions):
    questions_with_tables = [q for q in questions if q.get("has-table")]
    questions_with_tables.sort(key=lambda q: int(q["id"].replace("q", "")))
    image_files = sorted(os.listdir(TABLE_DIR), key=extract_page_number)

    question_table_map = {}
    for q, img in zip(questions_with_tables, image_files):
        question_table_map[q["id"]] = img
    return question_table_map

@app.route("/tables_cropped/<path:filename>")
def table_image(filename):
    return send_from_directory(TABLE_DIR, filename)

@app.route('/download-db')
def download_db():
    return send_from_directory('.', 'leakconverter_db.db', as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
