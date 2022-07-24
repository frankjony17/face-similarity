import unittest


# Arquivo de exemplo para testes de integracao
# Fontes:
# https://realpython.com/python-testing/#writing-your-first-test

class TestDummy2(unittest.TestCase):

    def sum(arg):
        total = 0
        for val in arg:
            total += val
        return total

    def test_dummy2(self):
        """
        Exemplo de um caso de teste
        """
        data = [1, 2, 3, 4]
        result = sum(data)
        self.assertEqual(result, 10)
