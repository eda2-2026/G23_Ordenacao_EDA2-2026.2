# Chamada Inteligente

![Banner do Projeto](assets/EDA2.png)

---

## Autor

| Matrícula | Aluno |
| :---: | :--- |
| **221007715** | Fernanda Santos |

---

## Sobre o Projeto

O **Chamada Inteligente** é um sistema focado na gestão de frequência e desempenho acadêmico, oferecendo:

* **Classificação por Risco:** Utiliza o algoritmo de ordenação **Quicksort** para agrupar e ordenar os alunos de acordo com a faixa de risco de reprovação.
* **Sistema de Notificações:** Permite o envio automático ou manual de alertas e notificações para os estudantes identificados com alto risco de reprovação.

> [!IMPORTANT]
> **Nota:** Para fins de teste e demonstração do sistema, foram utilizados dados fictícios (nomes, notas, frequências e endereços de e-mail).

---

## Como Executar

### 1. Iniciar o Sistema
Navegue até a pasta raiz do projeto e execute:

```bash
python sistemachamada.py
```

> **Dica (Windows):** Caso o comando `python` não seja reconhecido, utilize `py sistemachamada.py`.

### 2. Executar os Testes Unitários
Para rodar os testes da ordenação:

```bash
python testordenacao.py
```
*(ou `py testordenacao.py` no Windows)*

### Configuração de E-mail (SMTP)
Dentro do sistema, clique na opção **Configurar e-mail**. Caso utilize o Gmail, preencha com as seguintes informações:

* **Servidor SMTP:** `smtp.gmail.com`
* **Porta:** `587`
* **Usuário / E-mail:** `seu-email@gmail.com`
* **Senha:** Senha de aplicativo do Gmail (App Password)
* **Remetente:** `seu-email@gmail.com`

---

## Algoritmos e Estruturas de Dados

O projeto implementa o algoritmo de ordenação **Quicksort** customizado, otimizado com as seguintes técnicas:

* **Pivô por Mediana de Três:** Evita a degradação para o pior caso $O(n^2)$ em listas já ordenadas ou quase ordenadas.
* **Particionamento em Três Vias (3-Way Partitioning):** Trata com eficiência elementos com chaves duplicadas (ex.: múltiplos alunos com o mesmo número de faltas).
* **Otimização de Espaço na Pilha:** Aplica recursão de cauda apenas na menor partição, mantendo a complexidade de espaço em $O(\log n)$.
* **Complexidade Temporal Média:** $O(n \log n)$.
* **Desempate Customizado:** Como o Quicksort não é um algoritmo estável, o **nome do aluno** é utilizado como critério secundário de desempate.

---

## Capturas de Tela

![Interface do Sistema](assets/Captura%20de%20tela%202026-10-06%20194945.png)

---

## Vídeo Demonstrativo

<p align="center">
  <a href="https://www.youtube.com/watch?v=jCYyG6SnK8E" target="_blank">
    <img src="https://img.youtube.com/vi/jCYyG6SnK8E/maxresdefault.jpg" alt="Assistir vídeo de demonstração no YouTube" width="100%">
  </a>
</p>
