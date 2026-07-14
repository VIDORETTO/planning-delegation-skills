# Organização da pasta de brainstorm

Objetivo: contexto rico o suficiente para não se perder entre sessões, sem virar uma pasta com
dezenas de arquivos que ninguém mais consegue acompanhar.

## Estrutura padrão (o normal, para a maioria dos casos)

```
docs/brainstorms/<slug>/
└── brainstorm.md          # único arquivo, sempre atualizado in-place
```

Isso é suficiente para a grande maioria dos brainstorms. Não crie a subpasta `topicos/` de
antemão "por precaução" — só quando o gatilho abaixo for atingido de verdade.

## Quando dividir em mais arquivos

Divida um tema para `topicos/<tema>.md` quando **qualquer** um destes for verdade:

- A seção sobre aquele tema no `brainstorm.md` já passou de ~40-50 linhas.
- O tema foi renegociado 3+ vezes ao longo da conversa (ex: modelo de dados mudou várias vezes) e
  vale preservar o raciocínio de cada mudança, não só o estado final.
- O tema é tecnicamente denso o suficiente para atrapalhar a leitura do resto (ex: um desenho de
  arquitetura com vários componentes, uma comparação extensa de fornecedores/bibliotecas).

Quando dividir:

```
docs/brainstorms/<slug>/
├── brainstorm.md
└── topicos/
    ├── modelo-de-dados.md
    ├── integracao-pagamentos.md
    └── arquitetura-notificacoes.md
```

No `brainstorm.md`, deixe apenas um resumo de 2-3 linhas por tópico + o link para o arquivo. Quem
só quer o estado geral não precisa abrir os tópicos; quem precisa do detalhe, abre o específico.

## Limite prático de arquivos

Como regra prática: se a pasta (incluindo `topicos/`) está passando de **6-8 arquivos**, é sinal
de que o brainstorm ficou grande demais para o formato de brainstorm — nesse ponto, considere
propor ao usuário avançar para o spec formal mesmo que ainda restem detalhes menores, já que o
spec tem uma estrutura melhor para organizar esse volume de informação do que uma pasta de notas.

## O que NUNCA fazer

- Um arquivo por sessão de conversa (`sessao-1.md`, `sessao-2.md`, `2026-07-14.md`...). Isso
  obriga quem retoma o brainstorm a ler tudo em ordem cronológica para entender o estado atual.
  Sempre consolide no `brainstorm.md`.
- Duplicar a mesma informação em dois arquivos "pra garantir". Se uma decisão pertence a um
  tópico, ela vive lá — no `brainstorm.md` fica só o resumo com link.
- Deixar arquivos de tópico órfãos (sem nenhuma referência a partir do `brainstorm.md`).
