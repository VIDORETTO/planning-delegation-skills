# Classificação de gravidade x esforço

Usada no Passo 4 (Consolidação final) para transformar a lista de achados por página em fases de
melhoria priorizadas, em vez de uma lista plana de dezenas de itens soltos.

## Gravidade (impacto no usuário)

- **Alta** — impede ou confunde a tarefa principal da página; afeta legibilidade/acessibilidade
  básica (ex: contraste muito baixo); ocorre em um fluxo de alto tráfego (ex: login, checkout,
  onboarding).
- **Média** — gera atrito perceptível mas contornável; o usuário consegue completar a tarefa, só
  que com mais esforço ou confusão do que deveria.
- **Baixa** — polimento estético que não afeta a conclusão da tarefa (ex: um espaçamento levemente
  inconsistente numa área secundária).

## Esforço (custo estimado de correção)

- **Alto** — exige redesenho de um componente compartilhado, mudança no design system, ou afeta
  várias telas ao mesmo tempo.
- **Médio** — ajuste localizado em poucos componentes ou uma única página, mas com mais de uma
  mudança envolvida.
- **Baixo** — mudança isolada de um valor (espaçamento, cor, tamanho), tipicamente poucas linhas
  de CSS/estilo, sem afetar outras telas.

## Como priorizar em fases

| Gravidade | Esforço | Fase |
|---|---|---|
| Alta | Baixo ou Médio | **Fase 1 — ganhos rápidos de alto impacto** |
| Alta | Alto | **Fase 2 — ajustes estruturais** |
| Média | Baixo ou Médio | **Fase 2 — ajustes estruturais** |
| Média | Alto | **Fase 3 — refinamento e polimento** |
| Baixa | Qualquer | **Fase 3 — refinamento e polimento** |

Dentro de cada fase, ordene os padrões pelo número de páginas afetadas (o que aparece em mais
telas primeiro) — corrigir um padrão recorrente uma vez só costuma valer mais do que corrigir
vários problemas isolados de baixo impacto.

Achados que não formam um padrão recorrente (aparecem em uma única página) mas ainda são
relevantes entram na seção "Achados isolados" do relatório final, fora das fases — não force um
achado isolado para dentro de uma fase só para não deixá-lo de fora do relatório.
