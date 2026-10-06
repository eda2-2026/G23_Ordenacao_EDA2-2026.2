# CHAMDA INTELIGENTE

![Texto Alternativo](https://raw.githubusercontent.com/eda2-2026/G23_Ordenacao_EDA2-2026.2/refs/heads/main/assets/EDA2.png?token=GHSAT0AAAAAAEFR35JN42INPW4RY7T4EBFM2WFPYOQ)

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

cd C:

Execute o sistema:
python sistemachamada.py

Se o comando python não funcionar no Windows, use:
py sistemachamada.py

Como rodar os testes:
python testordenacao.py

ou:
py testordenacao.py

Configurar e-mail real:
Dentro do sistema, clique em Configurar e-mail.

Para Gmail, use:
- Servidor SMTP: smtp.gmail.com
- Porta: 587
- Usuário / e-mail: seu e-mail do Gmail
- Senha: senha de aplicativo do Gmail
- Remetente: seu e-mail do Gmail

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

