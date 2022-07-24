import unittest


# Arquivo de exemplo para testes de unidade
# Fontes:
# https://realpython.com/python-testing/#writing-your-first-test
# https://docs.python.org/3/library/unittest.html
# https://www.blog.pythonlibrary.org/2016/07/07/python-3-testing-an-intro-to-unittest/

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


class TestDummy(unittest.TestCase):

    def sum(arg):
        total = 0
        for val in arg:
            total += val
        return total

    def test_dummy(self):
        """
        Exemplo de um caso de teste
        """
        data = [1, 2, 3]
        result = sum(data)
        self.assertEqual(result, 6)
