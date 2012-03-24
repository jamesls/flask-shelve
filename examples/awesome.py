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
    if data['is_awesome'].lower() == 'true':
        label = 'awesome'
    else:
        label = 'lame'
    content = data['content']
    process_incoming_content(content, label, db=shelve.get_shelve())
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


# Remember bayes theorem:
# P(awesomeness|content) ~ p(content|awesomeness) * p(awesomeness)
# or:
# P(awesomeness|content) ~ multiply(ratio of awesome docs word appears in) *
#                          p(aweomness)
#
def check_probability(label, word_frequencies, db):
    if 'total_docs_seen' not in db:
        # Then we haven't processed any documents yet so just
        # return 0.0
        return 0.0
    log.debug("== computing: p(%s|content)", label)
    total_docs_seen = float(db['total_docs_seen'])
    log.debug("total_docs_seen: %s", total_docs_seen)
    # The number of docs marked as label.
    total_label_docs = float(db['total_%s_docs' % label])
    log.debug("total_%s_docs: %s", label, total_label_docs)
    p_prior = total_label_docs / total_docs_seen
    # Total number of unique words for a class.
    word_count = float(db.get('%s_words_count' % label, 1))
    log.debug("word count: %s", word_count)
    log.debug("p(%s) = %s", label, p_prior)
    frequencies = db['%s_words' % label]
    content_given_label = {}
    log.debug("words: %s", word_frequencies)
    for word in word_frequencies:
        term = (frequencies.get(word, 1) / word_count) * \
                word_frequencies[word]
        content_given_label[word] = term
    p_content_given_label = reduce(lambda a, b: a * b,
                                   content_given_label.itervalues())
    log.debug("p(content|%s) = %s", label, p_content_given_label)
    prob = (p_content_given_label * (p_prior))
    log.debug("p(%s|content) ~ %s", label, prob)
    return prob


def process_incoming_content(content, label, db):
    word_frequencies = _get_word_frequencies(content)
    # A mapping of word -> frequency.  This says how
    # many times a word occurs for a given class label.
    existing_words = db.get('%s_words' % label, {})
    # The total number of words
    existing_words_count = db.get('%s_words_count' % label, 0)
    for word in word_frequencies:
        existing_words[word] = existing_words.get(word, 0) + \
                word_frequencies[word]
        existing_words_count += word_frequencies[word]
    # Write the data back to the db.
    count = float(existing_words_count)
    # Word -> frequencies
    db['%s_words' % label] = existing_words
    # Total number of words (this is also used as the total
    # number of training examples.
    db['%s_words_count' % label] = existing_words_count
    db['total_docs_seen'] = db.get('total_docs_seen', 0) + 1
    db['total_%s_docs' % label] = db.get('total_%s_docs' % label, 0) + 1


def _get_word_frequencies(content):
    # Return a frequency dictionary, excluding stop words.
    words = {}
    for word in re.split(r'\W*', content):
        word = word.lower().strip()
        if word not in STOP_WORDS:
            words[word] = words.get(word, 0) + 1
    return words


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True) #, threaded=True)
