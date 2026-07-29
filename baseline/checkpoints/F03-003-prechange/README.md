<div align="center">

# Skill Team

### De ideia a release — skills coordenadas para agentes de IA

[![Skills](https://img.shields.io/badge/skills-9-7c3aed?style=for-the-badge)](#as-9-skills)
[![Contract](https://img.shields.io/badge/contract-skill--team%2Fv3-0f766e?style=for-the-badge)](contracts/skill-team-v3.md)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)](#validação)
[![Last commit](https://img.shields.io/github/last-commit/VIDORETTO/planning-delegation-skills?style=for-the-badge&logo=github)](https://github.com/VIDORETTO/planning-delegation-skills/commits/main)

Um kit reutilizável que transforma intenção ambígua em plano executável, distribui o trabalho ao modelo certo, implementa com evidência, revisa com independência e decide se está pronto para release.

[Começar](#início-rápido) · [Skills](#as-9-skills) · [Fluxo](#como-funciona) · [Validar](#validação)

</div>

---

## O que é o Skill Team

Agentes de IA costumam misturar descoberta, planejamento e código na mesma conversa. O resultado: contratos inventados, dependências puladas, “feito” sem prova e ninguém sabe onde o trabalho parou.

**Skill Team** é um conjunto de 9 skills que trabalham em cadeia. Cada uma tem um trabalho claro, entrega artefatos objetivos e passa o bastão para a próxima — sem pular etapa e sem dois escritores ao mesmo tempo.

Contrato operacional: [`contracts/skill-team-v3.md`](contracts/skill-team-v3.md)  
Catálogo: [`catalog/skills.json`](catalog/skills.json)

## Como funciona

```mermaid
flowchart LR
    D[Descoberta] --> P[Plano]
    P --> R[Roteamento]
    R --> E[Execução]
    E --> V[Revisão]
    V --> L[Release]
```

| Etapa | Skills | Pergunta que responde |
|---|---|---|
| Descoberta | brainstorm · investigate · ux-audit | O que queremos e o que já existe? |
| Planejamento | create-spec-driven-plan | Como fazer isso de forma executável? |
| Roteamento | route-ai-work-by-capability | Quem deve fazer cada tarefa? |
| Execução | execute-routed-task | Implementar a próxima tarefa pronta |
| Qualidade | review-implementation-evidence | A evidência sustenta o “feito”? |
| Release | validate-release-readiness | Podemos lançar? |
| Manutenção | author-repository-skill | Como evoluir este próprio kit? |

O ponteiro operacional único em qualquer projeto consumidor é:

```text
docs/ai/<slug>/PROGRESS.md
```

Ele diz qual skill está ativa (`required_skill`), quem escreve agora (`writer_skill`) e qual é a próxima ação. `next_skill` é proibido em novos artefatos. Cada skill conclui, valida, atualiza o ponteiro e para; ela nunca executa a etapa sucessora na mesma invocação.

Os caminhos canônicos em um projeto consumidor são `discovery/`, `plan/`, `routing/`, `execution/`, `review/`, `release/`, `blockers/`, `findings/` e `handoffs/`, todos sob `docs/ai/<slug>/`. Consulte o [contrato](contracts/skill-team-v3.md).

---

## As 9 skills

### 1. `brainstorm-idea-with-user`

**Para quê:** amadurecer uma ideia vaga com o usuário até ela ficar pronta para virar plano.

**Quando usar:** produto novo, pedido ambíguo, “quero algo assim”, requisitos incompletos.

**Como pedir:**

```text
Use $brainstorm-idea-with-user para explorar esta ideia comigo até
estarmos prontos para planejar.
```

**Entrega:** `BRAINSTORM.md` + handoff `BRAINSTORM-TO-PLAN.md`

---

### 2. `investigate-existing-codebase`

**Para quê:** inspecionar o código real e trocar achismo por evidência antes de planejar mudança.

**Quando usar:** bug, feature em repo legado, refactor, auditoria técnica, “como isso funciona hoje?”.

**Como pedir:**

```text
Use $investigate-existing-codebase para mapear a arquitetura atual,
o impacto desta mudança e a evidência técnica necessária ao plano.
```

**Entrega:** `discovery/codebase/INVESTIGATION.md`, `EVIDENCE.md` + handoff `CODEBASE-TO-PLAN.md`

---

### 3. `product-ux-audit`

**Para quê:** auditar a interface renderizada (fluxos, cobertura, problemas de UX) com taxonomia única.

**Quando usar:** produto vivo, preview local, protótipo navegável, revisão visual antes de replanejar.

**Como pedir:**

```text
Use $product-ux-audit neste produto. Mapeie o sitemap, cubra as telas
combinadas e produza o handoff para o plano.
```

**Entrega:** `SITEMAP.md`, `COVERAGE.md`, `UX-AUDIT.md` + handoff `UX-AUDIT-TO-PLAN.md`

---

### 4. `create-spec-driven-plan`

**Para quê:** transformar descoberta (ou brief compacto) em plano spec-driven: contratos, fases, tarefas testáveis e rastreabilidade.

**Quando usar:** depois da descoberta, ou quando o escopo já está claro e falta um plano executável por outra IA.

**Como pedir:**

```text
Use $create-spec-driven-plan com o handoff de descoberta e gere o
planejamento completo (perfil standard), pronto para roteamento.
```

Perfis: `compact` (mudança pequena), `standard` (padrão), `critical` (risco alto).

**Entrega:** `plan/SPEC.md` (visão compacta derivada), plano, checklists, análise de consistência e handoff `PLAN-TO-ROUTING.md`.

Durante `PLAN_IN_PROGRESS`, a skill faz uma pergunta material por vez, registra a resposta e atualiza a prontidão. Perguntas que revelem intenção de produto ausente retornam à descoberta; não criam uma etapa nova. Checklists avaliam a qualidade do requisito escrito, e `plan/CONSISTENCY-REPORT.md` bloqueia lacunas estruturais antes de `PLAN_VALIDATED`.

---

### 5. `route-ai-work-by-capability`

**Para quê:** classificar cada tarefa por risco/capacidade e atribuir executor (e revisor quando preciso), sem amarrar a skill a um modelo de marca.

**Quando usar:** plano validado, com tarefas e dependências prontas para filas.

**Como pedir:**

```text
Use $route-ai-work-by-capability para classificar as tarefas,
registrar os modelos em MODEL-CAPABILITIES.md e criar as filas.
```

**Entrega:** `ROUTING.md`, `MODEL-CAPABILITIES.md` + handoff `ROUTING-TO-IMPLEMENTATION.md`

---

### 6. `execute-routed-task`

**Para quê:** implementar a próxima tarefa pronta da fila do modelo ativo — mudança mínima, checks, evidência, e parar limpo.

**Quando usar:** roteamento validado, revisões alinhadas, um único escritor ativo, tarefa com dependências satisfeitas.

**Como pedir:**

```text
Use $execute-routed-task. Sou o modelo X. Continue a partir do
PROGRESS.md e execute o próximo lote autorizado da minha fila.
```

**Entrega:** `execution/EVIDENCE.md`, `HISTORY.md` + `IMPLEMENTATION-TO-REVIEW.md` (ou `IMPLEMENTATION-TO-RELEASE.md` quando a revisão for explicitamente dispensada)

---

### 7. `review-implementation-evidence`

**Para quê:** revisar de forma independente se a implementação realmente cumpre o plano — sem “consertar” em silêncio.

**Quando usar:** política do projeto exige review, hard gate, ou dúvida se o “feito” tem prova.

**Como pedir:**

```text
Use $review-implementation-evidence na tarefa F02-004. Aprove,
peça correção limitada ou escale — sem implementar o fix.
```

**Entrega:** `review/REVIEW-REPORT.md`, findings em `findings/<FINDING-ID>.md` e handoff para release ou correção limitada.

Findings são classificados como `missing`, `partial`, `contradicts` ou `unrequested`. Correções locais retornam à execução; problemas de atribuição retornam ao roteamento; lacunas de contrato retornam ao plano; contradições técnicas retornam à investigação; e mudança de intenção retorna ao brainstorm. Review não altera implementação, plano ou roteamento.

---

### 8. `validate-release-readiness`

**Para quê:** decidir, com evidência, se o release pode sair — testes, reviews, segurança, migração, rollback, observabilidade.

**Quando usar:** trabalho da release concluído (ou quase) e alguém precisa de um go / no-go explícito.

**Como pedir:**

```text
Use $validate-release-readiness e produza a decisão de release
com blockers claros. Não faça deploy.
```

**Entrega:** `release/RELEASE-READINESS.md` + atualização do ponteiro de release no `PROGRESS.md`.

Release só fica pronto quando cada gate aplicável tem evidência de aprovação ou risco aceito com responsável, justificativa, condição de expiração/revisão e confirmação de que não enfraquece gate não dispensável. A rota sem review independente exige política explícita no roteamento e o handoff canônico `IMPLEMENTATION-TO-RELEASE.md`.

---

### 9. `author-repository-skill`

**Para quê:** criar, atualizar, fundir, dividir ou auditar skills **deste** repositório, mantendo catálogo, contrato e validadores.

**Quando usar:** manutenção do Skill Team — não é parte do fluxo de produto do usuário final.

**Como pedir:**

```text
Use $author-repository-skill para adicionar/atualizar a skill X,
checando overlap no catálogo antes de criar algo novo.
```

---

## Início rápido

### 1. Clone

```bash
git clone https://github.com/VIDORETTO/planning-delegation-skills.git
cd planning-delegation-skills
```

### 2. Instale as skills no seu agente

Adapters por ferramenta:

| Ferramenta | Guia |
|---|---|
| Codex | [`adapters/codex/README.md`](adapters/codex/README.md) |
| OpenCode | [`adapters/opencode/README.md`](adapters/opencode/README.md) |
| Cursor | [`adapters/cursor/README.md`](adapters/cursor/README.md) |

Exemplo Cursor (PowerShell):

```powershell
Copy-Item .\skills\* "$env:USERPROFILE\.cursor\skills" -Recurse -Force
```

### 3. Escolha o ponto de entrada

| Situação | Comece com |
|---|---|
| Ideia nova / ambígua | `brainstorm-idea-with-user` |
| Código existente a entender | `investigate-existing-codebase` |
| UI/produto a auditar | `product-ux-audit` |
| Já tem contexto, falta plano | `create-spec-driven-plan` |
| Plano pronto, falta filas | `route-ai-work-by-capability` |
| Filas prontas, implementar | `execute-routed-task` |

O inicializador cria somente estados iniciais estritos de descoberta:

```bash
python scripts/init_workflow.py --root <repository-root> --project-id <stable-id> --project-slug <kebab-slug> --profile <compact|standard|critical> --discovery <brainstorm|codebase|ux>
```

Ele não cria handoff pronto. Para retomar um fluxo existente, abra o `PROGRESS.md` canônico e execute somente a `required_skill`.

### 4. Continuidade

Depois do primeiro ciclo, mensagens curtas bastam:

```text
Continue.
```

O agente lê `PROGRESS.md` e sabe a skill exigida, o escritor ativo e a próxima ação.

---

## Validação

Só biblioteca padrão do Python.

```bash
# Repositório inteiro (catálogo, links, schemas, templates e fixtures estritos)
python scripts/validate_repository.py

# Por skill, em um projeto consumidor
python skills/create-spec-driven-plan/scripts/validate_plan.py docs/ai/<slug>
python skills/route-ai-work-by-capability/scripts/validate_routing.py docs/ai/<slug>
```

Testes:

```bash
python -m unittest discover -s tests
```

O workflow de CI em [`.github/workflows/validate-skills.yml`](.github/workflows/validate-skills.yml) executa a validação completa. Ela inclui schemas, templates instanciados, fixtures válidas e inválidas, catálogo, links, recursos, compilação e toda a suíte `unittest`.

---

## Princípios (versão curta)

1. **Especificação antes do código** — contratos e aceites vêm primeiro.
2. **Um ponteiro** — `PROGRESS.md` é a fonte operacional; `AGENTS.md` só indexa.
3. **Skill certa, sem atalho** — `required_skill` não se ignora.
4. **Um escritor por vez** — evita corrida e estado inconsistente.
5. **Modelos são configuração do projeto** — a skill classifica papéis; o nome do modelo fica em `MODEL-CAPABILITIES.md`.
6. **Conclusão exige evidência** — “feito” sem prova não conta.
7. **Núcleo portátil** — adapters são opcionais; o core não depende de uma IDE.

---

## Estrutura do repositório

```text
planning-delegation-skills/
├── README.md
├── AGENTS.md
├── contracts/          # skill-team/v3 + schemas
├── catalog/            # registro das skills
├── skills/             # as 9 skills
├── adapters/           # Codex / OpenCode / Cursor
├── scripts/            # validadores do repositório
├── tests/              # unit + integração
└── docs/migration/     # v2 → v3, mapa do advisor-planner
```

Migração a partir de `planning-delegation/v2`:

```bash
python scripts/migrate_v2_to_v3.py docs/ai/<slug> --dry-run
```

Revise o manifesto do dry run antes de migrar. A migração preserva artefatos não-pointer, recusa estado ambíguo ou escritor ativo e é idempotente após produzir um ponteiro v3 estrito. Para uma interrupção, use o backup e a verificação de hash do migrador:

```bash
python scripts/migrate_v2_to_v3.py --rollback docs/ai/<slug>/.migration-backup/<UTC>
```

Detalhes: [`docs/migration/v3-strict-migration.md`](docs/migration/v3-strict-migration.md).

## Inspiração

As capacidades de especificação, clarificação, checklist, análise e convergência foram inspiradas conceitualmente pelo [GitHub Spec Kit](https://github.com/github/spec-kit). Skill Team permanece independente: não requer pacote, CLI, runtime, resolvedor de templates ou workflow engine do Spec Kit.

---

## Contribuindo e segurança

- Contribuição: [`CONTRIBUTING.md`](CONTRIBUTING.md) — use `author-repository-skill` antes de criar skill nova.
- Segurança: [`SECURITY.md`](SECURITY.md) — sem secrets em fixtures; sem instalar pacotes com `--break-system-packages`.

---

<div align="center">

**Descubra com evidência. Planeje com contratos. Delegue com critérios. Entregue com prova.**

[Voltar ao topo](#skill-team)

</div>
