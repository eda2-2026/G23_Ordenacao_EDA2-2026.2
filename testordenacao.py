import random
import sys
import unittest

from ordenacao import quicksort, texto_normalizado


class TesteQuicksort(unittest.TestCase):
    def test_vazio_e_um_elemento(self):
        self.assertEqual(quicksort([]), [])
        self.assertEqual(quicksort([7]), [7])

    def test_aleatorio_igual_ao_sorted(self):
        rnd = random.Random(42)
        for n in (2, 3, 10, 100, 1000):
            lista = [rnd.randint(-50, 50) for _ in range(n)]
            self.assertEqual(quicksort(lista), sorted(lista))

    def test_ja_ordenada_e_inversa_sem_estourar_pilha(self):
        n = 20000
        self.assertEqual(quicksort(list(range(n))), list(range(n)))
        self.assertEqual(quicksort(list(range(n, 0, -1))), list(range(1, n + 1)))
        self.assertEqual(quicksort([5] * n), [5] * n)

    def test_reverse_e_key(self):
        self.assertEqual(quicksort([3, 1, 2], reverse=True), [3, 2, 1])
        palavras = ["ccc", "a", "bb"]
        self.assertEqual(quicksort(palavras, key=len), ["a", "bb", "ccc"])

    def test_nao_altera_original(self):
        original = [3, 1, 2]
        quicksort(original)
        self.assertEqual(original, [3, 1, 2])

    def test_acentos(self):
        nomes = ["Zeca", "João", "Ana", "Álvaro"]
        self.assertEqual(
            quicksort(nomes, key=texto_normalizado),
            ["Álvaro", "Ana", "João", "Zeca"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
