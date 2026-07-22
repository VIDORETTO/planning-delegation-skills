# Severidade, Esforço e Priorização

O objetivo aqui é evitar dois erros opostos: (1) reportar só o óbvio e perder achados importantes, e (2) transformar cada micro-detalhe em uma "tarefa formal", inflando o relatório com ruído. Documentação completa por página sim; lista de tarefas enxuta e realmente acionável no relatório final.

## Severidade

- **Crítico**: impede o usuário de completar uma tarefa essencial na interface, gera confusão que trava o uso, ou torna uma tela inutilizável (ex: elemento essencial ilegível, fluxo sem saída visível). Sempre vira tarefa.
- **Alto**: gera confusão significativa, retrabalho, ou abandono provável, mas existe um jeito (ruim) de contornar. Sempre vira tarefa.
- **Médio**: incômodo real mas contornável facilmente; inconsistência visível de design; fluxo que poderia ser mais direto. Vira tarefa se for um padrão que se repete ou afeta uma área de alto tráfego; senão, fica documentado na página mas agrupado/resumido no relatório final.
- **Baixo**: polimento, preferência estética, detalhe menor. NÃO vira tarefa individual no relatório final — mencione apenas agregado (ex: "17 pequenas inconsistências de espaçamento catalogadas nas páginas X, Y, Z — ver arquivos individuais") ou omita se for realmente irrelevante.

## Esforço (estimativa grosseira, não técnica de verdade)
- **P (pequeno)**: ajuste de CSS/copy/espaçamento/cor, sem mudança de layout ou fluxo.
- **M (médio)**: precisa reorganizar um componente ou um trecho de fluxo, mas contido a uma tela.
- **G (grande)**: toca múltiplas telas, um padrão de design system inteiro, ou reestrutura um fluxo de navegação completo.

## Regra prática para montar as fases do relatório final
1. Liste todos os achados Crítico + Alto primeiro, agrupados por área do produto — isso normalmente vira a "Fase 1".
2. Achados Médio que se repetem em várias páginas (um padrão) formam a "Fase 2" (consistência de design/fluxo).
3. Achados Médio pontuais de melhoria de experiência, priorizados pelos que trazem mais valor com menos esforço, formam a "Fase 3".
4. Achados Baixo isolados: não criam fase própria. Ficam só documentados nos `pagina.md` individuais.
5. Cada fase deve ter poucas tarefas (o suficiente para ser executável, não uma lista de 80 itens). Se uma fase estiver com uma lista enorme, provavelmente itens de baixa severidade entraram por engano — revise e corte.

## Formato de uma tarefa no relatório final
```
- [ ] **[Fato/Sugestão][Severidade] Título curto da tarefa** — onde: (página/fluxo). Problema: (1-2 frases). Ideia de solução: (1-2 frases). Esforço: P/M/G. Referência: `01-pagina/pagina.md`
```

Achados marcados `[Ponto aberto]` nunca entram nessa lista de tarefas — eles vão só na seção "Pontos abertos para você decidir" do relatório final, porque dependem de uma decisão que a auditoria não pode tomar sozinha.
