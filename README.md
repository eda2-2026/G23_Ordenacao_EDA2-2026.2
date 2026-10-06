# CHAMDA INTELIGENTE

 ---

 ## Aluno
| Matricula | Aluno           |
| --------- | --------------- |
| 221007715 | Fernanda Santos |

## Sobre  
>uma chamada inteligente que usa Bucket Sort para organizar os alunos por faixa de risco de reprovação por falta e gerar notificações.

## Como executar

## Estrutura de dados usada

Algoritmo de ordenação Quicksort 
 
Características:
- Pivô por mediana de três (primeiro, meio, último): evita o pior caso O(n²)
  em listas já ordenadas, que é justamente o caso da lista vinda do banco.
- Particionamento em três vias (<, ==, > pivô), in-place, sobre uma cópia da
  lista original: chaves repetidas não degradam o desempenho.
- Recursão apenas na partição menor (a maior vira laço): profundidade de
  pilha O(log n).
- Aceita `key` e `reverse`, como o sorted() do Python.
- Não é estável; por isso, no sistema, as chaves de ordenação incluem o nome
  como critério de desempate.
 

## Imagens



## Vídeo demonstrativo

<br>

</p>

