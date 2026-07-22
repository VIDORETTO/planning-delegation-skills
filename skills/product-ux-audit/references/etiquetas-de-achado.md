# Etiquetas de Achado — Fato / Sugestão / Ponto Aberto

Ideia inspirada em um princípio comum em planejamento assistido por IA: nunca misturar "o que é objetivamente verdade", "o que é opinião de quem analisou" e "o que precisa de uma decisão humana". Aqui isso é usado de um jeito leve, só para o documento cumprir seu objetivo real: dar munição para você (o usuário) concordar, discordar ou decidir — não para prescrever tarefas obrigatórias.

Toda skill deste tipo tem o risco de soar como "a IA decidiu o que está errado". Para evitar isso, cada achado leva uma das três etiquetas abaixo, e o relatório final deve deixar claro que **o usuário é quem decide o que vira ação de fato**.

## [Fato]
Algo verificável, que qualquer pessoa observando a mesma tela chegaria à mesma conclusão: um link quebrado, um erro no console, um texto ilegível por falta de contraste, um número que não bate. Baixa margem de discordância.

## [Sugestão]
Uma opinião de melhoria, baseada em boas práticas gerais de UI/UX, mas que envolve gosto ou contexto de negócio que a auditoria não tem acesso total. Exemplo: "esse formulário poderia ser dividido em 2 etapas". É perfeitamente razoável o usuário discordar dessas.

## [Ponto aberto]
Algo que a auditoria não tem informação suficiente para julgar sozinha, porque depende de uma decisão de produto, regra de negócio, ou contexto que só o dono do produto sabe. Exemplo: "esse campo obrigatório parece desnecessário — é uma exigência legal ou pode ser removido?". Esses pontos existem para gerar reflexão e decisão, não para virar tarefa automaticamente.

## Por que isso importa no relatório final
O `REPORT.md` deve separar visualmente:
- achados **[Fato]** relevantes → viram candidatos naturais a tarefa;
- achados **[Sugestão]** → aparecem como "vale considerar", nunca como obrigação;
- achados **[Ponto aberto]** → aparecem numa lista própria de perguntas para o usuário responder antes de qualquer implementação.

Isso mantém o documento fiel ao objetivo: abrir a mente sobre o que pode melhorar, e deixar a decisão final com quem conhece o produto de verdade.
