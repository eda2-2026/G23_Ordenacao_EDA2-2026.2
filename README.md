# CHAMDA INTELIGENTE

 ---

 ## Aluno
| Matricula | Aluno           |
| --------- | --------------- |
| 221007715 | Fernanda Santos |

## Sobre  
**Classificação por Risco:** Utiliza o algoritmo de ordenação Quicksort para agrupar e ordenar os alunos de acordo com a faixa de risco de reprovação.

**Sistema de Notificações:** Permite o envio automático (ou manual) de alertas e notificações para os estudantes identificados com alto risco de reprovação.

> [!IMPORTANT]
> Nota: Para fins de teste e demonstração do sistema, foram utilizados dados fictícios (nomes, notas, frequências e endereços de e-mail).

## Como executar

## Estrutura de dados usada

Algoritmo de ordenação Quicksort 
- pivô por **mediana de três**, evitando o pior caso em listas já ordenadas;
- particionamento em **três vias** (`<`, `==`, `>` pivô), que lida bem com valores repetidos (ex.: vários alunos com 0 faltas);
- recursão só na menor partição, mantendo a pilha em O(log n);
- complexidade média O(n log n); aceita `key` e `reverse`.

Como o Quicksort não é estável, cada coluna usa o nome do aluno como critério de desempate. 

## Imagens



## Vídeo demonstrativo

<br>

</p>

