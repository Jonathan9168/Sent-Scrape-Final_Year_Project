import unittest
from config import generate_verdict_rob


class TestGenerateVerdictRob(unittest.TestCase):

    def test_inconclusive_verdict(self):
        final = 0.05
        term = "example"
        expected_verdict = ("Inconclusive - [0.05]",
                            "A final score of 0.05, indicates that the data doesn't seem to strongly favour one direction. You might want to consider checking how the scoring of <span style='color: lightblue'>'EXAMPLE'</span> fares on other platforms.")
        verdict = generate_verdict_rob(final, term)
        self.assertEqual(verdict, expected_verdict)

    def test_relatively_unpopular_verdict(self):
        final = -0.3
        term = "example"
        expected_verdict = ('<span style="color: #f98686">Relatively Unpopular</span> - [-0.3]',
                            "A score of <span style='color: #f98686'>-0.3</span> reflects a noticeable amount of negativity around <span style='color: #f98686'>'EXAMPLE'</span>, see if this trend follows on other platforms and take a look at the dataset snapshot to see what's being discussed.")
        verdict = generate_verdict_rob(final, term)
        self.assertEqual(verdict, expected_verdict)

    def test_highly_unpopular_verdict(self):
        final = -0.8
        term = "example"
        expected_verdict = ('<span style="color: #f98686">Highly Unpopular</span> - [-0.8]',
                            "A score of <span style='color: #f98686'>-0.8</span> indicates a significant amount of negativity surrounding <span style='color: #f98686'>'EXAMPLE'</span>. Is there a specific event that might have caused this?")
        verdict = generate_verdict_rob(final, term)
        self.assertEqual(verdict, expected_verdict)

    def test_relatively_popular_verdict(self):
        final = 0.3
        term = "example"
        expected_verdict = ('<span style="color: lightgreen">Relatively Popular</span> - [0.3]',
                            "A score of <span style='color: lightgreen'>0.3</span> suggests significant positivity. You may want to explore if this trend persists on other platforms. Click the button below to view talking points about <span style='color: lightgreen'>'EXAMPLE'</span>.")
        verdict = generate_verdict_rob(final, term)
        self.assertEqual(verdict, expected_verdict)

    def test_highly_popular_verdict(self):
        final = 0.8
        term = "example"
        expected_verdict = ('<span style="color: lightgreen">Highly Popular</span> - [0.8]',
                            "A score of <span style='color: lightgreen'>0.8</span> reflects an overwhelming amount of positivity around <span style='color: lightgreen'>'EXAMPLE'</span>. Can you identify any specific factors or events that might have contributed to this positive sentiment?")
        verdict = generate_verdict_rob(final, term)
        self.assertEqual(verdict, expected_verdict)


if __name__ == "__main__":
    unittest.main()
