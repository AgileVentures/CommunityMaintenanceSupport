import unittest, datetime
import slack_posts as sp

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def test_total_posts_for_week_ending_on_given_day(self):
        posts = {datetime.datetime(2014, 9, 26, 0, 0): 1, datetime.datetime(2014, 9, 24, 0, 0): 4}
        self.assertEqual(sp.total_posts_for_week_ending_on_given_day(posts,datetime.datetime(2014,9,27,0,0)),5)

if __name__ == '__main__':
    unittest.main()
