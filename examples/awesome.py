#!/usr/bin/env python
"""Example app for Flask-Shelve.

This is just a demo app that shows how to use flask shelve
in a basic application.

"""
import os
import re
import math
import logging

import flask
from flask.ext import shelve


app = flask.Flask(__name__)
app.config['SHELVE_FILENAME'] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '_awesome.db')
shelve.init_app(app)
log = logging.getLogger('awesome')

# From:
# http://www.textfixer.com/resources/common-english-words.txt
STOP_WORDS = set([
    'a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also', 'am',
    'among', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been',
    'but', 'by', 'can', 'cannot', 'could', 'dear', 'did', 'do', 'does',
    'either', 'else', 'ever', 'every', 'for', 'from', 'get', 'got', 'had',
    'has', 'have', 'he', 'her', 'hers', 'him', 'his', 'how', 'however', 'i',
    'if', 'in', 'into', 'is', 'it', 'its', 'just', 'least', 'let', 'like',
    'likely', 'may', 'me', 'might', 'most', 'must', 'my', 'neither', 'no',
    'nor', 'not', 'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our',
    'own', 'rather', 'said', 'say', 'says', 'she', 'should', 'since', 'so',
    'some', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'these',
    'they', 'this', 'tis', 'to', 'too', 'twas', 'us', 'wants', 'was', 'we',
    'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why',
    'will', 'with', 'would', 'yet', 'you', 'your'
])

@app.route('/')
def index():
    '', 200


@app.route('/awesomeness/', methods=['POST'])
def awesomeness():
    data = flask.request.form
    is_awesome = data['is_awesome'].lower() == 'true'
    content = data['content']
    process_incoming_content(content, is_awesome, db=shelve.get_shelve())
    return '', 201


@app.route('/awesomeness/check/', methods=['POST'])
def check_awesomeness():
    content = flask.request.form['content']
    response = decide_if_awesome(content, db=shelve.get_shelve('r'))
    return flask.jsonify(**response)


# This would normally be a DELETE, but in order to not have to
# deal with urllib2 customization, I'm just making it a POST.
@app.route('/reset/', methods=['POST'])
def reset_data():
    db = shelve.get_shelve('c')
    for k in db.keys():
        del db[k]
    return '', 200


# Remember bayes theorem:
# P(awesomeness|content) = p(content|awesomeness) * p(awesomeness)
#                          ---------------------------------------
#                                         p(content)
def decide_if_awesome(content, db):
    word_frequencies = _get_word_frequencies(content)
    p_is_awesome = check_probability('awesome', word_frequencies, db)
    p_is_not_awesome = check_probability('lame', word_frequencies, db)
    if p_is_awesome > p_is_not_awesome:
        is_awesome = True
    else:
        is_awesome = False
    return {'awesome': p_is_awesome, 'lame': p_is_not_awesome,
            'is_awesome': is_awesome}


def check_probability(label, word_frequencies, db):
    if 'total_docs_seen' not in db:
        # Then we haven't processed any documents yet so just
        # return 0.0
        return 0.0
    total_docs_seen = float(db['total_docs_seen'])
    log.debug("total_docs_seen: %s", total_docs_seen)
    total_awesome_docs = float(db['total_awesome_docs'])
    log.debug("total_awesome_docs: %s", total_awesome_docs)
    p_prior = total_awesome_docs / total_docs_seen
    unknown_probability = math.log(1 / total_awesome_docs)
    if label != 'awesome':
        # Assuming binary decision
        p_prior = 1 - p_prior
        unknown_probability = math.log(
            1 / (total_docs_seen - total_awesome_docs))
    log.debug("unknown_probability: %s", unknown_probability)
    probabilities = db['%s_words_probabilities' % label]
    content_given_label = {}
    for word in word_frequencies:
        term = probabilities.get(word, unknown_probability) * \
                word_frequencies[word]
        content_given_label[word] = term
    from heapq import nlargest
    largest = nlargest(10, content_given_label, key=lambda x: content_given_label[x])
    print
    for l in largest:
        print l, content_given_label[l]
    p_content_given_label = sum(content_given_label.itervalues())
    return (p_content_given_label + math.log(p_prior))


def process_incoming_content(content, is_awesome, db):
    word_frequencies = _get_word_frequencies(content)
    all_words = db.get('all_word_frequencies', {})
    if is_awesome:
        existing_words = db.get('awesome_words', {})
        existing_words_count = db.get('awesome_words_count', 0)
    else:
        existing_words = db.get('lame_words', {})
        existing_words_count = db.get('lame_words_count', 0)

    for word in word_frequencies:
        existing_words[word] = existing_words.get(word, 0) + \
                word_frequencies[word]
        existing_words_count += word_frequencies[word]
    # Write the data back to the db.
    count = float(existing_words_count)
    if is_awesome:
        db['awesome_words'] = existing_words
        db['awesome_words_count'] = existing_words_count
        db['awesome_words_probabilities'] = dict(
            (word, math.log(existing_words[word] / count))
            for word in existing_words
        )
    else:
        db['lame_words'] = existing_words
        db['lame_words_count'] = existing_words_count
        db['lame_words_probabilities'] = dict(
            (word, math.log(existing_words[word] / count))
            for word in existing_words
        )
    db['total_docs_seen'] = db.get('total_docs_seen', 0) + 1
    if is_awesome:
        db['total_awesome_docs'] = db.get('total_awesome_docs', 0) + 1


def _get_word_frequencies(content):
    # Return a frequency dictionary, excluding stop words.
    words = {}
    for word in re.split(r'\W*', content):
        word = word.lower().strip()
        if word not in STOP_WORDS:
            words[word] = words.get(word, 0) + 1
    return words


# Copied from:
# http://love-python.blogspot.com/2011/04/html-to-text-in-python.html
def html_to_text(data):        
    # remove the newlines
    data = data.replace("\n", " ")
    data = data.replace("\r", " ")
   
    # replace consecutive spaces into a single one
    data = " ".join(data.split())   
   
    # get only the body content
    bodyPat = re.compile(r'<body[^<>]*?>(.*?)</body>', re.I)
    result = re.findall(bodyPat, data)
    if not result:
        return data
    data = result[0]
   
    # now remove the java script
    p = re.compile(r'<script[^<>]*?>.*?</script>')
    data = p.sub('', data)
   
    # remove the css styles
    p = re.compile(r'<style[^<>]*?>.*?</style>')
    data = p.sub('', data)
   
    # remove html comments
    p = re.compile(r'')
    data = p.sub('', data)
   
    # remove all the tags
    p = re.compile(r'<[^<]*?>')
    data = p.sub('', data)
   
    return data


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True) #, threaded=True)
