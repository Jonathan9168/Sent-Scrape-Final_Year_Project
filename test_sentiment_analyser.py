from unittest import TestCase
import unittest
from sentiment_analyser import pre_process


class TestPreProcess(TestCase):

    def test_pre_process(self):
        comment = "Hi @user! Check out my website: http://www.example.com"
        expected_output = "hi check out my website"
        self.assertEqual(pre_process(comment), expected_output)

    def test_pre_process_punctuation(self):
        comment = "This is a test! @user. #hashtag, http://www.example.com"
        expected_output = "this is a test"
        self.assertEqual(pre_process(comment), expected_output)

    def test_pre_process_emotes(self):
        comment = "I'm feeling happy! 😊"
        expected_output = "im feeling happy"
        self.assertEqual(pre_process(comment), expected_output)

    def test_pre_process_whitespace(self):
        comment = "This is    a  test    with    extra   whitespace."
        expected_output = "this is a test with extra whitespace"
        self.assertEqual(pre_process(comment), expected_output)


if __name__ == '__main__':
    unittest.main()
