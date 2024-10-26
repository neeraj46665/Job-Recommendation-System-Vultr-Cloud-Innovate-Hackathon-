from flask import Flask, render_template, request, jsonify
import pandas as pd
import docx
import PyPDF2
import os
from langchain_cohere.llms import Cohere
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sklearn.feature_extraction.text import TfidfVectorizer
from dotenv import load_dotenv
import requests

load_dotenv()
app = Flask(__name__)

# Load the job data from the CSV file
job_data = pd.read_csv('job_final.csv')

# Initialize the vectorizer globally
vectorizer = TfidfVectorizer()

# Initialize the Cohere language model
os.environ['COHERE_API_KEY']=os.getenv('COHERE_API_KEY')
chat_prompt_template = ChatPromptTemplate.from_template("""
You are an AI assistant that helps employers screen candidates based on resumes and job descriptions. Your task is to analyze the following:
Job Description:{job_description}
Candidate Resume:{resume}
Please provide a summary of the candidate's suitability for the job, including strengths, weaknesses, and any skill gaps along with recommendations for skills that the candidate should acquire to improve employability.
""")
llm = Cohere()
analysis_chain = chat_prompt_template | llm | StrOutputParser()

# Function to extract text from DOCX files
def extract_text_from_docx(filename):
    doc = docx.Document(filename)
    return '\n'.join([para.text for para in doc.paragraphs])

# Function to extract text from PDF files
def extract_text_from_pdf(filename):
    with open(filename, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return '\n'.join([page.extract_text() for page in reader.pages if page.extract_text()])

# Function to vectorize text using the global vectorizer
def vectorize_text(text):
    return vectorizer.transform([text])

# Function to run the candidate analysis
def analyze_candidate(job_description, resume):
    analysis_result = analysis_chain.invoke({"job_description": job_description, "resume": resume})
    return analysis_result

@app.route('/')
def index():
    return render_template("index1.html")

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_data():
    if request.method == 'POST':
        f = request.files['userfile']
        if f:
            f.save(f.filename)  # Save the uploaded file
            # Extract text based on the file type
            if f.filename.endswith('.docx'):
                extracted_text = extract_text_from_docx(f.filename)
            elif f.filename.endswith('.pdf'):
                extracted_text = extract_text_from_pdf(f.filename)
            else:
                extracted_text = "Unsupported file format."
                message = "Unsupported file format. Please upload a DOCX or PDF file."
                return render_template("index.html", message=message, matching_jobs=None)

            # Fit the vectorizer on the job descriptions only if it's not already fitted
            if not hasattr(vectorizer, 'vocabulary_'):
                job_descriptions = job_data['Job_Description'].fillna('').astype(str).tolist()
                vectorizer.fit(job_descriptions)

            job_descriptions = job_data['Job_Description'].fillna('').astype(str).tolist()
            job_vectorized = vectorizer.transform(job_descriptions)
            vectorized_text = vectorizer.transform([extracted_text])
            similarity_matrix = (vectorized_text * job_vectorized.T).toarray()
            matching_indices = similarity_matrix[0].argsort()[::-1][:10]  # Top 10 matches
            matching_jobs = job_data.iloc[matching_indices]

            message = "Resume received and processed successfully! Click below to analyze the candidate."
            return render_template("index.html", message=message, matching_jobs=matching_jobs.to_dict(orient='records'), extracted_text=extracted_text)
        else:
            message = "No file received. Please try again."
            return render_template("index.html", message=message, matching_jobs=None)
        

@app.route('/analyze', methods=['POST'])
def analyze():
    job_description = request.form.get('job_description')
    extracted_text = request.form.get('extracted_text')

    # Perform the candidate analysis
    analysis_results = analyze_candidate(job_description, extracted_text)
    
    # Return the analysis results as JSON
    return jsonify({'analysis_results': analysis_results})


VULTR_CLOUD_INFERENCE_API_KEY=os.getenv('VULTR_CLOUD_INFERENCE_API_KEY')
api_key = {{secrets.VULTR_CLOUD_INFERENCE_API_KEY}}
api_key=str(api_key)

# Initialize a history list to keep track of messages
history = []
history.append({'role': 'system', 'content': "You are chatbot(Career Mitra) for job recommendation system. Help users solve their queries."})

@app.route('/chat', methods=['POST'])
def chat():
    # Get the JSON data from the request
    data = request.get_json()
    user_message = data.get('message')
    
    # Validate input
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Append the user message to history
    history.append({'role': 'user', 'content': user_message})
    
    model = 'llama2-70b-chat-Q5_K_M'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Prepare the data for the API request
    payload = {
        'model': model,
        'messages': history  # Send the entire conversation history
    }

    try:
        # Send request to the Vultr API
        response = requests.post('https://api.vultrinference.com/v1/chat/completions', headers=headers, json=payload)
        
        # Check response status code
        if response.status_code == 200:
            llm_response = response.json()['choices'][0]['message']['content']
            
            # Append the bot's response to history
            history.append({'role': 'assistant', 'content': llm_response})
            return jsonify({"response": llm_response, "history": history})
        else:
            return jsonify({"error": f"Error from API: {response.status_code} - {response.text}"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

