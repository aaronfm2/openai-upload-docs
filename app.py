import os

import openai
from flask import Flask, redirect, render_template, request, url_for
import concurrent.futures

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        files = request.files.getlist('file')
        folders = request.files.getlist('folder')
        fullString = createFileList(files)
        fullString += createFileList(folders)
        prompt = request.form["files"]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": generate_prompt(fullString, prompt)}
            ]
        )
        return redirect(url_for("index", result=response.choices[0].message.content))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def createFileList(files):
    count = 1
    results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(read_file, file) for file in files]
        for future in concurrent.futures.as_completed(futures):
            filename, contents = future.result()
            result = f'File number: {count} is {filename} The contents are:\n{contents}\n\n'
            results.append(result)
            count += 1

    fullString = ''.join(results)
    return fullString

def read_file(file):
    filename = file.filename
    contents = file.read().decode('utf-8')
    return filename, contents

def generate_prompt(fullString, prompt):
    return "These are the files in my project: " + fullString + " " + prompt