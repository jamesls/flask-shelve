#!/usr/bin/env python

import unittest
import awesome

class TestAwesome(unittest.TestCase):
    def setUp(self):
        self.db = {}

    def assertAwesomeWords(self, *words):
        for word in words:
            self.assertIn(word, self.db['awesome_words'])

    def assertLameWords(self, *words):
        for word in words:
            self.assertIn(word, self.db['lame_words'])

    def test_process_new_content_new_words(self):
        content = 'awesome cool sweet excellent python'
        awesome.process_incoming_content(content, label='awesome',
                                         db=self.db)
        self.assertAwesomeWords('awesome', 'cool', 'sweet', 'excellent',
                                'python')
        self.assertEqual(self.db['awesome_words_count'], 5)
        self.assertEqual(self.db['total_awesome_docs'], 1)
        self.assertEqual(self.db['total_docs_seen'], 1)

    def test_process_two_new_articles(self):
        content = 'awesome cool sweet'
        content2 = 'excellent python awesome'
        awesome.process_incoming_content(content, label='awesome',
                                         db=self.db)
        awesome.process_incoming_content(content2, label='awesome',
                                         db=self.db)
        # We should see 2 awesome documents.
        self.assertEqual(self.db['total_awesome_docs'], 2)
        self.assertEqual(self.db['total_docs_seen'], 2)
        self.assertAwesomeWords('awesome', 'cool', 'sweet', 'excellent',
                                'python')

    def test_process_lame(self):
        content = 'lame stupid dumb'
        awesome.process_incoming_content(content, label='lame',
                                         db=self.db)
        self.assertLameWords('lame', 'stupid', 'dumb')
        self.assertEqual(self.db['total_docs_seen'], 1)

    def test_decide_if_awesome(self):
        awesome.process_incoming_content(
            'awesome cool sweet', label='awesome', db=self.db)
        awesome.process_incoming_content(
            'excellent python', label='awesome', db=self.db)
        awesome.process_incoming_content(
            'totally great', label='awesome', db=self.db)
        awesome.process_incoming_content(
            'lame lame stupid dumb', label='lame', db=self.db)
        awesome.process_incoming_content(
            'sucky terrible crap', label='lame', db=self.db)

        self.assertEqual(
            awesome.decide_if_awesome('awesome', self.db)['is_awesome'],
            True, "'awesome' is not awesome!")
        self.assertEqual(
            awesome.decide_if_awesome('lame dumb', self.db)['is_awesome'],
            False, "'lame' is not lame!")


if __name__ == '__main__':
    unittest.main()
