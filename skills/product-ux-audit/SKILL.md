---
name: product-ux-audit
description: >
  Use whenever the user asks to audit, review, or evaluate the visual/UI/UX quality of a real,
  navigable digital product (web, mobile, or desktop) — logging into a live app/site and
  inspecting actual rendered screens, never mockups, descriptions, or source code. Trigger on:
  "audita a UI/UX do produto", "revisa a interface visual do app", "faz um UX audit", "analisa a
  experiência visual do sistema", "comece a trabalhar buscando por problemas de ui ux". Also
  trigger on "continue trabalhando" whenever a UX audit is already in progress — check for an
  existing `_sitemap.md` audit folder first. Strictly visual/UI/UX — NOT backend, bugs,
  performance, or data. Always maps a full sitemap and builds the folder skeleton before
  analyzing, then does exactly one page per turn, consolidating a final phased report only once
  the whole sitemap is audited.
---

# Auditoria Visual de Produto (UX/UI)

Transforma a navegação real de um produto digital já existente em uma **auditoria visual/UX/UI
estruturada e fundamentada em evidência** — nunca a partir de mockups, descrições ou leitura de
código, sempre a partir da tela efetivamente renderizada.

Esta skill é deliberadamente **restrita em escopo**: cobre só a camada visual/UI/UX (layout,
espaçamento, alinhamento, tipografia, cor, consistência, feedback de estados). Bugs de backend,
performance, dados ou lógica de negócio ficam de fora — se aparecerem no caminho, anote como
observação lateral e siga em frente, não vire o objetivo da auditoria.

O trabalho é desenhado para se espalhar por **várias execuções/turnos de conversa**. O usuário
normalmente vai mandar só "comece a trabalhar" na primeira mensagem e depois só "continue
trabalhando" nas seguintes, sem especificar mais nada — a skill precisa saber sozinha em que ponto
está e o que fazer a seguir.

---

## Escopo: o que audita e o que não audita

**Audita:**
- Espaçamento e distribuição de espaço vazio
- Proporção entre elementos (tamanho, peso visual)
- Alinhamento e consistência de grid
- Hierarquia tipográfica
- Paleta de cor e contraste
- Overflow, corte de texto, scroll horizontal indevido
- Consistência entre padrões repetidos (cards, listas, formulários)
- Feedback visual de ações do usuário e tratamento de loading/vazio/erro
- Harmonia geral da tela e clareza de leitura/uso

**Não audita:** lógica de backend, bugs de sistema, performance/velocidade real, corretude de
dados, segurança, decisões de negócio. Exceção: se uma lentidão ou erro de sistema se manifesta
como *ausência de feedback visual* (ex: tela congelada sem spinner durante um carregamento
lento), isso entra em escopo como achado de UX — o que importa é a experiência visual resultante,
não a causa técnica.

---

## Visão geral do fluxo

```
1. Reunir o essencial (URL/entry point, credenciais, plataforma, ferramenta de navegação disponível)
2. [SEMPRE primeiro, nunca pular] Mapear o sitemap + criar o esqueleto de pastas
3. Analisar UMA página/subpágina por vez → repetir a cada "continue trabalhando"
4. Consolidar o relatório final (só quando o sitemap inteiro estiver "concluído")
5. Manter o AGENTS.md do projeto atualizado ao longo de todo o processo
```

Nunca pule a etapa 2 para ir direto à análise. Sem sitemap e esqueleto completos, o usuário não
consegue acompanhar o que falta, e é fácil deixar telas de fora sem perceber.

---

## Passo 1: Reunir o essencial antes de tocar no produto

Pergunte (se ainda não tiver sido dito) só o que for indispensável para começar:

- Onde está o produto (URL de entrada, ou como abrir o app/desktop)
- Se precisa de login, e as credenciais de uma conta real para usar
- Que plataforma é — web, mobile ou desktop (isso decide a ferramenta de navegação a usar)
- Se existe alguma área explicitamente fora do escopo (ex: "não entra no painel admin interno")

Deixe claro que a senha será usada **só para logar** e não vai ser salva em nenhum arquivo gerado
(ver Segurança, mais abaixo).

### Verifique a ferramenta de navegação disponível

Esta skill não funciona a partir de descrição verbal, screenshot enviado manualmente pelo usuário,
ou leitura do código-fonte do frontend — o requisito central é ver a tela **de verdade**,
renderizada. Antes de prosseguir, confira qual mecanismo de navegação real está disponível no
ambiente atual (extensão de browser, MCP de navegação/browser automation, computer use, device/
simulador mobile, etc.) — ver `references/ferramentas-de-navegacao.md` para como detectar e usar
cada tipo. Se nenhuma ferramenta de navegação real estiver disponível, diga isso abertamente ao
usuário em vez de tentar "simular" a auditoria a partir de suposições.

---

## Passo 2: Sitemap + esqueleto de pastas (sempre primeiro, sem exceção)

Mesmo que a primeira mensagem do usuário seja só "comece a trabalhar buscando por problemas de ui
ux", esta etapa acontece antes de qualquer análise de detalhe visual:

1. Logue de verdade com as credenciais fornecidas.
2. Explore o produto em **largura, não profundidade** — percorra menus, abas, wizards, modais e
   tente alcançar estados de erro/vazio razoavelmente óbvios (ex: um formulário vazio, uma busca
   sem resultado). O objetivo aqui é catalogar o que existe, não analisar detalhe visual ainda —
   resista ao impulso de já escrever um achado se notar algo quebrado nesta fase; apenas anote a
   página e continue mapeando.
3. Monte o sitemap como uma árvore, com um ID curto por página/subpágina e uma coluna de status
   (`pendente` / `em andamento` / `concluído`). Use `templates/sitemap-template.md`.
4. Crie o esqueleto de pastas de saída espelhando o sitemap, uma pasta por página/subpágina
   (mesmo aninhada), em:
   ```
   <slug-do-produto>-ux-audit/
   ├── _sitemap.md
   ├── RELATORIO-FINAL.md        (criado só no Passo 4)
   ├── pagina-a/
   │   └── screenshots/
   ├── pagina-a/sub-pagina-a1/
   │   └── screenshots/
   └── pagina-b/
       └── screenshots/
   ```
5. Salve `_sitemap.md` na raiz — ele é a **fonte única de verdade do progresso**. Toda a
   continuidade entre turnos depende deste arquivo, então mantenha-o sempre atualizado in-place.
6. Apresente o esqueleto ao usuário para que ele veja o alcance total da auditoria antes de entrar
   em detalhe.
7. **Continue direto para o Passo 3** e analise a primeira página do sitemap ainda neste mesmo
   turno — não pare só no esqueleto, a menos que o usuário tenha pedido explicitamente só o
   mapeamento.

### Continuidade entre turnos

Antes de repetir este passo, verifique se já existe um `_sitemap.md` desta auditoria (na pasta de
saída, ou referenciado no `AGENTS.md` do projeto — ver Passo 5). Se existir, **não remapeie do
zero**: leia o status de cada página e retome de onde parou. Se o ambiente tiver sido reiniciado e
os arquivos não existirem mais, mas o histórico da conversa mostrar o que já foi analisado,
reconstrua o estado a partir da conversa em vez de perder o trabalho já feito.

---

## Passo 3: Analisar uma página por vez

**Regra central da skill: uma execução = uma página/subpágina, nunca mais.** Tentar cobrir várias
páginas na mesma passada produz achados genéricos e rasos — o valor desta auditoria vem de olhar
com atenção para uma tela de cada vez.

1. Leia `_sitemap.md` e escolha a próxima página: a que estiver `em andamento` (se uma execução
   anterior foi interrompida no meio) ou, senão, a primeira `pendente` na ordem do sitemap.
2. Navegue de verdade até essa página/estado específico. Não assuma que a sessão de login
   anterior ainda está válida sem checar — logue de novo se necessário.
3. Capture screenshot(s) da tela realmente renderizada, incluindo estados relevantes e
   razoavelmente alcançáveis sem engenharia excessiva (ex: um hover no CTA principal, um estado de
   lista vazia, um erro de validação simples) além do estado padrão.
4. Percorra **cada categoria** do checklist em `references/criterios-visuais.md`, uma por uma, em
   vez de listar achados por associação livre — o checklist existe justamente para que os achados
   sejam reproduzíveis e concretos, não "achismo" de gosto pessoal.
5. Para cada achado real, registre usando `templates/pagina-audit-template.md`:
   - **Onde** — elemento/área específica da tela
   - **O que está acontecendo** — descrição concreta, com referência ao screenshot salvo
   - **Por que importa** — impacto real no usuário final
   - **Sugestão** — ajuste concreto e específico, não genérico
   - **Classificação** — `[FATO OBJETIVO]` / `[OPINIÃO/SUGESTÃO]` / `[DEPENDE DO DONO DO PRODUTO]`
     (ver `references/criterios-visuais.md` para como decidir entre as três)
6. Se uma categoria do checklist não apresentar problema nesta página, não force um achado — deixe
   registrado que a categoria foi checada e está limpa. Uma auditoria honesta tem páginas com
   poucos ou nenhum achado.
7. Salve o documento na pasta correspondente da página, junto dos screenshots.
8. Atualize `_sitemap.md`: marque esta página como `concluído`. Se novas subpáginas, modais ou
   estados foram descobertos durante a análise (mais detalhada que o mapeamento inicial), adicione
   como novas linhas `pendente` e crie as pastas correspondentes.
9. **Encerre o turno aqui.** Conte ao usuário em poucas linhas o que mais chamou atenção nesta
   página (o relatório detalhado já está salvo no arquivo — não duplique tudo na conversa) e
   indique que ele pode mandar "continue" para seguir para a próxima página.

---

## Passo 4: Consolidação final

Só entre nesta etapa quando **todas** as linhas de `_sitemap.md` estiverem `concluído` — ou quando
o usuário pedir explicitamente para encerrar e consolidar o que já foi feito até agora (nesse
caso, marque claramente no relatório que a cobertura é parcial e por quê).

1. Leia todos os documentos de página já salvos.
2. Agrupe **padrões recorrentes entre páginas** (ex: espaçamento inconsistente aparecendo em 6 de
   9 telas) em vez de listar cada ocorrência separadamente — o relatório final não é uma soma dos
   relatórios de página, é uma síntese.
3. Classifique cada padrão/achado por **gravidade** (impacto no usuário) x **esforço** (custo de
   correção) — ver `references/classificacao-gravidade-esforco.md` para a rubrica.
4. Organize em **fases de melhoria priorizadas** (ex: Fase 1 — ganhos rápidos de alto impacto;
   Fase 2 — ajustes estruturais; Fase 3 — refinamento e polimento) — nunca uma lista plana de
   dezenas de itens soltos sem hierarquia.
5. Salve como `RELATORIO-FINAL.md` na raiz da pasta de saída, usando
   `templates/relatorio-final-template.md`.
6. Se o usuário quiser transformar as fases em um backlog executável, isso é trabalho de
   planejamento, não de auditoria — se a skill `spec-driven-dev` (ou equivalente) estiver
   disponível no ambiente, sugira usá-la a partir do `RELATORIO-FINAL.md` em vez de duplicar esse
   trabalho aqui.

---

## Segurança (sempre, em qualquer passo)

- **Nunca realize ações destrutivas ou com efeito real** — excluir, enviar, publicar, pagar,
  confirmar pedidos, etc. — sem confirmação explícita do usuário. Se a navegação levar a um botão
  desses por acidente durante o mapeamento ou a análise, pare e pergunte antes de clicar.
- **Nunca grave a senha (ou qualquer credencial)** em nenhum arquivo gerado, screenshot, nome de
  arquivo, log ou commit. Use-a apenas de forma transitória para logar a cada sessão de trabalho.
- Se a sessão expirar no meio de uma análise, logue de novo com as credenciais já fornecidas pelo
  usuário nesta conversa — não é necessário pedir de novo, mas também nunca escreva em disco.

---

## Passo 5: Manter o AGENTS.md do projeto atualizado

Sempre que o esqueleto for criado ou o status de uma página mudar em `_sitemap.md`, atualize
também o `AGENTS.md` na raiz do projeto (crie o arquivo se não existir; se já existir, edite só a
seção relevante, sem tocar no resto). Use `templates/agents-md-snippet-template.md` como formato.

Isso é o que permite que qualquer IA (Claude ou outra) que abra o projeto do zero encontre a
auditoria em andamento e retome de onde parou, sem que o usuário precise reexplicar tudo — mesma
lógica usada por outras skills desta família (ex: `brainstorm-idea-with-user`).

---

## Erros comuns a evitar

- Analisar a partir de descrição, mockup ou código-fonte em vez da tela renderizada de verdade.
- Pular o sitemap/esqueleto e ir direto para achados soltos.
- Tentar cobrir várias páginas em uma única execução — rasteja a análise e gera achados genéricos.
- Misturar bugs de backend/performance/dados com achados visuais.
- Fazer do relatório final uma lista plana de dezenas de itens soltos, em vez de agrupar padrões
  recorrentes e organizar em fases.
- Rotular tudo como `[FATO OBJETIVO]` — boa parte de crítica de design é opinião fundamentada;
  seja honesto sobre o que é mensurável e o que é julgamento.
- Forçar um achado em categoria que está genuinamente limpa, só para "preencher" a página.
- Esquecer de atualizar o `_sitemap.md` ou o `AGENTS.md` antes de encerrar o turno.
- Gravar senha ou credencial em qualquer arquivo gerado.

---

## Referências

Carregue apenas o arquivo relevante para o momento atual — não carregue todos de uma vez.

| Arquivo | Quando carregar |
|---|---|
| `references/criterios-visuais.md` | Ao analisar uma página (Passo 3) — checklist objetivo por categoria e como decidir a classificação do achado |
| `references/ferramentas-de-navegacao.md` | No Passo 1, para identificar qual ferramenta de navegação real usar no ambiente atual |
| `references/classificacao-gravidade-esforco.md` | Na consolidação final (Passo 4), para classificar gravidade x esforço e montar as fases |
| `templates/sitemap-template.md` | Criar ou atualizar o `_sitemap.md` |
| `templates/pagina-audit-template.md` | Criar o documento de auditoria de uma página |
| `templates/relatorio-final-template.md` | Criar o `RELATORIO-FINAL.md` |
| `templates/agents-md-snippet-template.md` | Criar/atualizar a seção de auditoria no `AGENTS.md` |
