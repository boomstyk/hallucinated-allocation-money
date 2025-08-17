from flask import Flask, request, jsonify, render_template
import logging 

logger = logging.getLogger("web_logger")
logging.basicConfig(filename='web.log', encoding='utf-8', level=logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch.setFormatter(formatter)

logger.addHandler(ch)

app = Flask(__name__)

def get_completion(prompt):
    # Simulate a completion response for demonstration purposes
    response = f"Processed prompt: {prompt}"
    logger.debug(f"Received prompt: {prompt}")
    logger.debug(f"Generated response: {response}")
    return response

@app.route("/", methods=['POST', 'GET'])
def query_view():
    if request.method == 'POST':
        prompt = request.form['prompt']
        response = get_completion(prompt)
        print(response)

        return jsonify({'response': response})
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)