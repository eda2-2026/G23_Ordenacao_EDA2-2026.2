import unicodedata


def quicksort(itens, key=None, reverse=False):
    dados = list(itens)
    chave = key or (lambda x: x)
    pares = [(chave(x), x) for x in dados]
    _quicksort(pares, 0, len(pares) - 1)
    resultado = [x for _, x in pares]
    if reverse:
        resultado.reverse()
    return resultado


def _quicksort(a, baixo, alto):
    while baixo < alto:
        menor, maior = _particionar_3_vias(a, baixo, alto)
        if menor - baixo < alto - maior:
            _quicksort(a, baixo, menor - 1)
            baixo = maior + 1
        else:
            _quicksort(a, maior + 1, alto)
            alto = menor - 1


def _mediana_de_tres(a, baixo, alto):
    meio = (baixo + alto) // 2
    x, y, z = a[baixo][0], a[meio][0], a[alto][0]
    if x < y:
        return y if y < z else (z if x < z else x)
    return x if x < z else (z if y < z else y)


def _particionar_3_vias(a, baixo, alto):
    pivo = _mediana_de_tres(a, baixo, alto)
    menor, i, maior = baixo, baixo, alto
    while i <= maior:
        k = a[i][0]
        if k < pivo:
            a[menor], a[i] = a[i], a[menor]
            menor += 1
            i += 1
        elif pivo < k:
            a[i], a[maior] = a[maior], a[i]
            maior -= 1
        else:
            i += 1
    return menor, maior


def texto_normalizado(s):
    sem_acento = unicodedata.normalize("NFD", s)
    sem_acento = "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")
    return sem_acento.casefold()
