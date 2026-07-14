# Roteiro de entrevista por tipo de projeto

Use como banco de perguntas — não como questionário fixo. Escolha 2-3 por rodada, priorizando o
que é mais estrutural para o caso específico. Pule perguntas cuja resposta já está implícita no
que o usuário já disse.

## Produto/app novo

**Rodada — problema e público**
- Quem sente esse problema hoje, e o que essa pessoa faz na ausência da sua solução?
- Existe algo parecido que as pessoas já usam (mesmo que de forma manual/improvisada)? O que
  incomoda nisso?
- Qual é o cenário mínimo que, se funcionar, já prova que a ideia vale a pena?

**Rodada — escopo e restrições**
- Existe uma plataforma alvo específica (web, mobile, ambos)?
- Há alguma restrição técnica já decidida (stack, hospedagem, orçamento, prazo)?
- Existe algo que você sabe que NÃO quer fazer agora, mesmo que pareça óbvio incluir?

**Rodada — dados e integrações**
- O sistema depende de dados/serviços externos (pagamento, autenticação social, APIs de
  terceiros)? Quais?
- Precisa funcionar offline ou em baixa conectividade?

## Feature em produto já existente

**Rodada — encaixe**
- Como essa feature se encaixa no que já existe? Ela substitui algo ou é aditiva?
- Existe um padrão de design/arquitetura do projeto atual que ela precisa respeitar?
- Quem mais no time/projeto é afetado por essa mudança (outras telas, outros fluxos)?

**Rodada — critério de sucesso**
- Como você vai saber que essa feature está pronta e funcionando como esperado?
- Existe alguma métrica ou comportamento que ela precisa preservar (não pode quebrar)?

## Automação / script / ferramenta interna

**Rodada — gatilho e frequência**
- O que dispara essa automação (evento, agenda, ação manual)?
- Com que frequência ela roda, e o que acontece se ela falhar uma vez?
- Quem é o "dono" dessa automação — quem precisa entender/ajustar ela no futuro?

**Rodada — dados de entrada e saída**
- De onde vêm os dados de entrada, e em que formato?
- Onde o resultado precisa aparecer (arquivo, planilha, mensagem, outro sistema)?

## Problema ainda sem forma de solução

Quando o usuário descreve uma dor mas não uma solução ainda:

- Se você pudesse resolver isso hoje magicamente, o que mudaria no seu dia a dia?
- O que você já tentou que não funcionou, e por quê não funcionou?
- Existe uma solução que seria "boa o suficiente" mesmo que não fosse perfeita?

Nesses casos, é especialmente importante fazer o Passo 5 (Refletir e sugerir) da skill principal
com força — o usuário pode não ter ainda um formato de solução em mente, e cabe a você propor 1-2
caminhos concretos para reagir, em vez de só perguntar "o que você quer construir?" no vácuo.
