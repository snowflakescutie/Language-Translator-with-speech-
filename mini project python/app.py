from flask import Flask, render_template, request,jsonify
import re
from gtts import gTTS

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

languages = {'1': 'Arabic', '2': 'German', '3': 'English', '4': 'Spanish', '5': 'French', '6': 'Hebrew',
             '7': 'Japanese', '8': 'Dutch', '9': 'Polish', '10': 'Portuguese', '11': 'Romanian', '12': 'Russian',
             '13': 'Turkish'}

def response_function(input_data):
    user_agent = 'Mozilla/5.0'
    try:
        response = requests.get(f'https://context.reverso.net/translation/{languages[input_data[0]].lower()}-{languages[input_data[1]].lower()}/{input_data[2]}', headers={'User-Agent': user_agent})
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find translations and examples
        translations = [word.text.strip() for word in soup.find_all('a', class_='translation')]
        examples = [word.text.strip() for word in soup.find_all('div', class_='example')]
        
        # If translations are not found but examples are available, prioritize examples
        if not translations and examples:
            translations = ['Translations not directly available. See examples below.']
        
        return translations, examples
    except:
        return None, None



@app.route('/')
def index():
    return render_template('index.html', languages=languages)

@app.route('/translate', methods=['POST'])
def translate():
    if request.method == 'POST':
        # Check if the request contains speech recognition data
        if 'speechToTranslate' in request.form:
            speech_to_translate = request.form['speechToTranslate']
            # Process the speech for translation...
            # Example: pass the speech to your existing translation function
            translations, examples = response_function(['3', '4', speech_to_translate])  # Assuming '3' is English and '4' is Spanish
            if translations and examples:
                return jsonify({'translations': translations, 'examples': examples})
            else:
                return jsonify({'error': 'Error occurred while fetching translations.'})
        else:
            # If no speech recognition data is present, proceed with regular text input translation
            language_from = request.form['language_from']
            language_to = request.form['language_to']
            word = request.form['word'].lower()

            translations, examples = response_function([language_from, language_to, word])

            if translations and examples:
                return render_template('translation_result.html', translations=translations, examples=examples)
            else:
                return "Error occurred while fetching translations."


@app.route('/faq')
def faq():
    faq_content = """
    Frequently Asked Questions
    
    Q: How accurate is the translation?
    A: The translation provided by the app is based on available online resources and may not always be 100% accurate.
    
    Q: Can I translate entire sentences?
    A: Yes, you can translate words, phrases, or entire sentences using the app.
    
    Q: Can I translate between any two languages?
    A: The app supports translation between a variety of languages listed on the home page.
    """
    
    # Generate speech for FAQ content
    tts_faq = gTTS(text=faq_content, lang='en')
    tts_faq.save("faq.mp3")

    return render_template('faq.html', faq_content=faq_content, faq_audio="faq.mp3")





if __name__ == '__main__':
    app.run(debug=True)