# Organização documental do brainstorm

Use uma única raiz durante todo o workflow:

```text
docs/ai/<project-slug>/
├── PROGRESS.md                 # único ponteiro operacional
├── CONTEXT-INDEX.md            # índice, sem estado duplicado
├── SOURCE-REGISTER.md          # origem e autoridade das informações
├── GLOSSARY.md
├── brainstorm/
│   ├── BRAINSTORM.md           # estado detalhado da etapa
│   └── topics/                 # criado somente quando necessário
└── handoffs/
    └── BRAINSTORM-TO-PLAN.md
```

## Autoridade

- `PROGRESS.md`: etapa, status, skill ativa, próxima ação e revisões.
- `BRAINSTORM.md`: conteúdo consolidado do brainstorm.
- `SOURCE-REGISTER.md`: autoridade, versão e validade das fontes.
- `BRAINSTORM-TO-PLAN.md`: pacote imutável da revisão entregue ao planejamento.
- `AGENTS.md`: apenas descoberta de `PROGRESS.md`; nunca status.

Não duplique uma afirmação para “garantir”. Registre o detalhe na fonte competente e use links nos
índices e handoffs.

## Quando extrair um tópico

Comece somente com `brainstorm/BRAINSTORM.md`. Extraia para
`brainstorm/topics/<topic>.md` quando qualquer condição ocorrer:

- a seção ultrapassar aproximadamente 40–50 linhas;
- o tema tiver sido renegociado três ou mais vezes e o raciocínio precisar ser preservado;
- o conteúdo técnico prejudicar a leitura do brainstorm principal.

No arquivo principal, deixe um resumo de duas ou três linhas e um link local. O tópico deve declarar
os IDs relacionados e nunca pode ficar órfão.

## Limites

Se `topics/` passar de seis a oito arquivos, reavalie se as questões estruturais já estão fechadas.
Detalhes menores devem seguir para o planejamento, não prolongar indefinidamente o brainstorm.

## Proibido

- Arquivo por sessão ou data.
- Outro `PROGRESS.md` dentro de subpastas.
- Nomes alternativos como `brainstorm.md`, `topicos/` ou `docs/brainstorms/` no contrato v2.
- Status operacional em `AGENTS.md` ou `CONTEXT-INDEX.md`.
- Tópicos sem link a partir de `BRAINSTORM.md`.
- Alterar documentos de `plan/` ou `ROUTING.md` durante esta skill.
