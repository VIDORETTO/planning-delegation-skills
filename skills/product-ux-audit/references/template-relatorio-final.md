# Relatório de Auditoria — [Nome do Produto]

**Data**: [data]
**Escopo**: [páginas/áreas cobertas]
**Conta usada no teste**: [e-mail/usuário — NUNCA incluir senha aqui]
**Ferramenta de navegação**: [ex: Claude in Chrome / prints fornecidos pelo usuário]

## Resumo executivo
2-4 parágrafos: estado geral do produto, principais forças, principais problemas encontrados, e o que o usuário ganha implementando as recomendações. Sem jargão técnico desnecessário — este resumo deve fazer sentido para um stakeholder não-técnico.

## Sitemap auditado
Lista/árvore das páginas e subpáginas cobertas, com link para cada pasta.

```
01-login/
02-dashboard/
  02-01-widgets/
03-configuracoes/
  ...
```

## Achados por severidade (visão consolidada)
Inclua a etiqueta de cada achado — [Fato], [Sugestão] ou [Ponto aberto] — ver `references/etiquetas-de-achado.md`.

### Críticos
- [Fato] [Título] — página: `NN-slug/pagina.md` — resumo de 1 linha

### Altos
- ...

### Médios (padrões recorrentes)
- ...

### Baixos
- Agregado: "N itens de polimento menor catalogados — ver pastas individuais."

## Pontos abertos para você decidir
Lista consolidada de tudo que foi marcado `[Ponto aberto]` nas páginas — perguntas que dependem de contexto de negócio/produto que só você tem. Nada aqui vira tarefa automaticamente; é para gerar reflexão e decisão.
- Pergunta 1 — página: `NN-slug/pagina.md`
- Pergunta 2 — página: `NN-slug/pagina.md`

## Fases e tarefas de implementação

### Fase 1 — Correções críticas e quebras
- [ ] **[Crítico] ...** — onde: ... Problema: ... Sugestão: ... Esforço: ... Referência: ...

### Fase 2 — Consistência de UI e padrões
- [ ] **[Alto] ...**

### Fase 3 — Melhorias de fluxo e experiência
- [ ] **[Alto/Médio] ...**

(adicione mais fases só se fizer sentido pelo volume/natureza dos achados — não force um número fixo de fases)

## Alertas fora de escopo
Esta auditoria cobre só UI/UX. Se durante a navegação surgir algo de backend, banco de dados, lógica de negócio, bug funcional ou possível falha de segurança, registre aqui apenas como um alerta breve (1 linha), sem investigar a fundo, e recomende uma auditoria técnica separada (para segurança, a skill `vulnerability-hunter`) para tratar do assunto.

## Anexos
- Pastas de página com screenshots: `01-.../`, `02-.../`, ...
- Padrões transversais: `99-cross-cutting/`
