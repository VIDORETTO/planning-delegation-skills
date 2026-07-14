---
name: brainstorm-idea-with-user
description: >
  Use whenever the user brings a new project/feature idea — breve ou já detalhada — e o objetivo
  ainda é "entender e amadurecer o que construir", não escrever código ainda. Entrevista em
  rodadas curtas, reflete e sugere alternativas com trade-offs mas sempre deixa a decisão final
  com o usuário, e mantém contexto entre sessões gravando um arquivo de estado enxuto em pasta
  dedicada + resumo em AGENTS.md. Ao final, entrega o brainstorm para spec-driven-dev (ou
  equivalente) gerar o documento com fases e tarefas. Trigger: "tenho uma ideia", "quero criar um
  app/sistema/feature", "vamos pensar juntos sobre...", "validar essa ideia antes de codar",
  "continuar o brainstorm", "onde paramos com aquela ideia", "brainstorm". Vem ANTES de
  spec-driven-dev, não substitui.
---

# Brainstorm de Ideia com o Usuário

Transforma uma ideia inicial (rascunho de uma frase ou um parágrafo detalhado) em um **brainstorm
maduro e documentado**, através de diálogo real — não um questionário mecânico. O resultado final
é contexto rico e persistente o suficiente para que qualquer IA (ou você, em uma sessão futura)
entenda o projeto e gere um plano formal de execução.

Esta skill cobre **antes** do plano formal. Quando o brainstorm estiver maduro, o hand-off natural
é para `spec-driven-dev` (Modo B — Criar spec do zero), que já sabe entrevistar, classificar e
gerar o documento com fases/tarefas. Não duplique esse trabalho aqui — o objetivo desta skill é
preparar o terreno para que aquela etapa seja rápida e sem retrabalho.

---

## Visão geral do fluxo

```
1. Captar a ideia inicial (verbatim)
2. Detectar estado da sessão (nova ou continuação)  → ver "Continuidade entre sessões"
3. Diagnosticar lacunas (o que falta para decidir)
4. Entrevistar em rodadas curtas
5. Refletir e sugerir (sempre com alternativas + trade-offs)
6. Registrar decisões e pontos em aberto no arquivo de estado
7. Checar sinais de "pronto para virar plano"
8. Atualizar AGENTS.md
9. Repetir 3-8 até maduro
10. Hand-off para spec-driven-dev (ou skill de planejamento/roteamento disponível)
```

Nunca pule o passo 6 — é o que garante que a próxima sessão não comece do zero.

---

## Passo 1: Captar a ideia inicial

Guarde a ideia exatamente como o usuário descreveu, sem reescrever ou "melhorar" ainda. Isso vai
para a seção `## Ideia original` do arquivo de estado (ver template). Não interprete demais nesse
momento — resista ao impulso de já sugerir soluções antes de entender o problema.

Classifique mentalmente o nível de detalhe recebido:
- **Semente** (uma frase, tipo "quero um app para dividir contas entre amigos")
- **Esboço** (alguns parágrafos, já com um público-alvo ou funcionalidade central clara)
- **Detalhado** (já tem fluxos, restrições técnicas, ou exemplos concretos)

Quanto mais raso o nível, mais rodadas de entrevista serão necessárias — mas mesmo uma ideia
"detalhada" quase sempre tem lacunas de decisão que valem uma pergunta.

---

## Passo 2: Continuidade entre sessões

**Sempre, antes de perguntar qualquer coisa, verifique se já existe brainstorm em andamento:**

1. Procure em `AGENTS.md` (ou `agents.md`) uma seção `## Brainstorms` ou `## Brainstorm em andamento`.
2. Se existir referência a uma pasta de brainstorm para este projeto/tema, leia os arquivos dela
   (comece pelo arquivo de estado principal, não pelos arquivos de tópicos — ver
   `references/organizacao-de-pasta.md` para saber o que ler primeiro quando houver vários arquivos).
3. Se encontrar um brainstorm relacionado ao que o usuário está trazendo agora, **não recomece do
   zero**. Abra com um recap curto (3-5 linhas) do que já foi decidido e do que ficou em aberto, e
   pergunte se algo mudou desde então.
4. Se não existir nada, trate como novo brainstorm e siga o fluxo normal a partir do Passo 3.

Se o usuário mencionar um projeto/ideia por nome mas você não achar a pasta esperada, diga isso
abertamente em vez de fingir que lembra ou de inventar contexto.

---

## Passo 3: Diagnosticar lacunas

Antes de perguntar qualquer coisa, pense (internamente, não precisa expor todo o raciocínio):

- O que já está claro o suficiente para não precisar perguntar de novo?
- Quais decisões, se erradas, custariam caro mudar depois (arquitetura, modelo de dados, escopo)?
  Essas têm prioridade de pergunta.
- Quais são só preferências de superfície (cores, nomes) que podem esperar ou nem precisam de
  pergunta — você pode sugerir um padrão razoável e seguir?
- Existe alguma suposição perigosa que, se eu simplesmente assumir, pode levar a retrabalho grande?

Isso vira a pauta das rodadas de entrevista.

---

## Passo 4: Entrevistar em rodadas curtas

Regras:
- **No máximo 2-3 perguntas por rodada.** Espere a resposta antes de continuar — nunca dispare
  uma lista de 10 perguntas de uma vez.
- Priorize perguntas que decidem algo estrutural sobre perguntas de detalhe cosmético.
- Prefira perguntas com opções sugeridas ("A, B ou algo diferente do que você tem em mente?") a
  perguntas totalmente abertas quando fizer sentido — mas não force isso quando a pergunta é
  genuinamente aberta ("o que mais te incomoda no processo atual?").
- Se o ambiente tiver suporte a botões de escolha rápida e a pergunta for de preferência entre
  opções concretas (não uma questão de julgamento aberto), considere usar essa interação em vez de
  perguntar em texto corrido.
- Depois de cada rodada respondida, registre o que foi decidido no arquivo de estado (Passo 6)
  antes de seguir para a próxima rodada — não acumule tudo para escrever no final.

Veja `references/roteiro-de-entrevista.md` para bancos de perguntas por tipo de projeto (produto
novo, feature em produto existente, automação/script, problema ainda sem forma de solução).

---

## Passo 5: Refletir e sugerir

Depois de cada resposta relevante, faça sua própria análise antes de só aceitar o que foi dito:

- Existe uma abordagem mais simples, mais barata ou mais robusta do que a que o usuário descreveu?
- O escopo pedido parece maior do que o necessário para validar a ideia central? Vale sugerir um
  corte (ex: MVP) sem tirar a decisão final do usuário?
- Há um risco técnico ou de produto que o usuário provavelmente não considerou?

Quando notar algo assim, **diga claramente e proponha a alternativa com trade-offs em 2-3 frases**,
por exemplo:

> "Você descreveu um sistema com login próprio. Uma alternativa mais rápida de validar seria usar
> login social (menos código, menos manutenção), com a desvantagem de depender de terceiros. Quer
> seguir com login próprio mesmo, ou prefere essa rota mais enxuta pra validar primeiro?"

**Regra de ouro: a decisão final é sempre do usuário.** Sua sugestão é uma oferta, não uma
imposição — se o usuário already disse "quero X", não insista em Y depois de ele já ter escolhido,
a menos que surjam novas informações. Registre tanto a sugestão feita quanto a decisão tomada,
mesmo quando o usuário não seguiu sua recomendação (isso evita que uma sessão futura sugira a
mesma coisa de novo).

---

## Passo 6: Registrar no arquivo de estado

Depois de qualquer troca que gere uma decisão, uma pergunta em aberto, ou uma mudança de escopo,
atualize a pasta de brainstorm. Não espere o fim da conversa.

### Onde gravar

Pasta: `docs/brainstorms/<slug-do-projeto>/` (ou `brainstorms/<slug>/` na raiz se o projeto não
tiver pasta `docs/`). Use um slug curto e estável em kebab-case (ex: `divide-contas-app`,
`onboarding-v2`).

### Arquivo principal (sempre existe, sempre um só): `brainstorm.md`

Use `templates/brainstorm-state-template.md` como base. Este arquivo é a **fonte única de
verdade em andamento** — atualize-o in-place (edite seções existentes), não acumule histórico
duplicado nele. Ele deve caber numa leitura de poucos minutos mesmo depois de várias sessões.

### Quando criar arquivos adicionais

A pasta **não deve virar uma bagunça de arquivos soltos**. Comece só com `brainstorm.md`. Só
adicione arquivos extras quando um tópico específico crescer demais para caber legível dentro
dele — regra prática: se uma seção do `brainstorm.md` passaria de ~40-50 linhas ou está sendo
reescrita/renegociada muitas vezes, extraia para `topicos/<tema>.md` e deixe no `brainstorm.md`
apenas um resumo de 2-3 linhas + link para o arquivo. Consulte
`references/organizacao-de-pasta.md` para os limites exatos e exemplos de quando vale a pena
dividir.

Nunca crie um arquivo novo por sessão (tipo `sessao-2026-07-14.md`) — isso é exatamente o tipo de
pasta confusa que o usuário pediu para evitar. Histórico de sessão vira uma seção curta
"Últimas atualizações" dentro do próprio `brainstorm.md`, com no máximo as últimas 3-5 entradas —
entradas mais antigas são resumidas ou removidas, não empilhadas para sempre.

---

## Passo 7: Sinais de "pronto para virar plano"

Depois de atualizar o estado, cheque se já dá para avançar para `spec-driven-dev`. Sinais:

- O problema central e o público/uso estão claros e sem contradição.
- As decisões estruturais de maior risco (arquitetura, escopo do MVP, restrições técnicas,
  integrações externas) estão fechadas ou o usuário disse explicitamente "decide você".
- Não há mais pergunta em aberto que, se respondida diferente, mudaria o plano inteiro.
- O usuário sinalizou diretamente que quer avançar ("bora pro plano", "acho que já temos o
  suficiente", "pode gerar o documento").

Se **todos** os sinais estruturais baterem mas ainda houver only itens de detalhe menor, você pode
propor avançar e resolver os detalhes menores durante a criação do spec. Não trave o processo por
perfeccionismo.

Se faltar clareza estrutural, diga isso ao usuário e continue a entrevista — não force um hand-off
prematuro só porque a conversa está longa.

---

## Passo 8: Atualizar o AGENTS.md

Sempre que a pasta de brainstorm for criada ou atualizada de forma relevante (não a cada pergunta
trivial — a cada decisão estrutural ou mudança de status), atualize `AGENTS.md` na raiz do
projeto (crie o arquivo se não existir; se o usuário já tiver um `AGENTS.md`, edite apenas a seção
relevante, sem tocar no resto).

Use `templates/agents-md-snippet-template.md` como formato da seção. Ela deve conter, por
brainstorm ativo ou concluído:

- Status (`em andamento` / `pronto para virar spec` / `convertido em spec em <caminho>`)
- Caminho da pasta e do arquivo principal
- Resumo de 2-3 linhas da ideia original
- Data da última atualização

Isso é o que permite que **qualquer** IA (Claude ou outra) que abra o projeto do zero encontre o
brainstorm sem precisar que o usuário reexplique tudo.

---

## Passo 9: Handoff para o plano formal

Quando os sinais do Passo 7 baterem e o usuário confirmar que quer seguir:

1. Diga explicitamente que vai passar para a etapa de planejamento formal.
2. Invoque o fluxo da skill `spec-driven-dev`, **Modo B — Criar spec do zero**, usando o conteúdo
   do `brainstorm.md` (e arquivos de tópico, se houver) como a base já entrevistada — não repita
   perguntas que o brainstorm já respondeu, passe o contexto adiante. Se o ambiente tiver outra
   skill de roteamento de tarefas por capacidade/modelo de IA disponível, use-a na etapa de
   classificação e sequenciamento, exatamente como o Modo A de `spec-driven-dev` já orienta.
3. Depois que o documento de spec for gerado, atualize o `AGENTS.md` para
   `convertido em spec em <caminho do spec>` e deixe a pasta de brainstorm como está — ela serve
   como histórico do raciocínio por trás das decisões, não precisa ser apagada.

---

## Erros comuns a evitar

- Perguntar tudo de uma vez em uma lista longa — cansa o usuário e piora as respostas.
- Aceitar a primeira descrição do usuário sem nenhuma reflexão própria — isso não é brainstorm, é
  ditado.
- Insistir na sua sugestão depois que o usuário já decidiu diferente.
- Criar um arquivo novo a cada sessão em vez de atualizar o `brainstorm.md` existente.
- Deixar o `AGENTS.md` sem atualização depois de decisões importantes — é o que quebra a
  continuidade entre sessões.
- Avançar para gerar o documento de fases/tarefas sem que as decisões estruturais estejam
  fechadas.

---

## Referências

| Arquivo | Quando carregar |
|---|---|
| `references/roteiro-de-entrevista.md` | Montar as perguntas de uma rodada, por tipo de projeto |
| `references/organizacao-de-pasta.md` | Decidir se/quando dividir o brainstorm em mais arquivos |
| `templates/brainstorm-state-template.md` | Criar ou reestruturar o `brainstorm.md` |
| `templates/agents-md-snippet-template.md` | Criar/atualizar a seção de brainstorm no `AGENTS.md` |
