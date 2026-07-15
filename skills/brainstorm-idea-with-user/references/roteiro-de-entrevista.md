# Roteiro de entrevista por tipo de projeto

Use como banco de perguntas, nunca como questionário fixo. Faça duas ou três por rodada, priorize
decisões estruturais e pule tudo que os artefatos já respondem. Depois de cada resposta material,
registre IDs, origem e revisão antes de continuar.

## Núcleo comum

### Problema e resultado

- Quem sofre o problema, com que frequência e qual é o impacto observável?
- Como o trabalho acontece hoje e quais soluções improvisadas existem?
- Qual mudança mínima faria o usuário perceber valor? Qual seria o resultado ideal?
- Que resultado seria explicitamente proibido, mesmo que pareça eficiente?

### Atores, permissões e jornadas

- Quem inicia, executa, aprova, consulta ou administra o fluxo?
- O que cada ator pode ver ou alterar? Existem organizações ou clientes que precisam ficar isolados?
- Qual é o gatilho, caminho feliz, exceção mais comum e falha mais perigosa?

### Escopo

- Qual é a primeira entrega utilizável que testa a hipótese central?
- O que pertence à visão completa, mas não ao MVP?
- O que está explicitamente fora de escopo? O que é apenas futuro possível?

### Dados, privacidade e escala

- Quais dados entram e saem, e qual sistema é a fonte de verdade?
- Há dados pessoais, financeiros, médicos, credenciais ou outros dados sensíveis?
- Qual retenção e exclusão são necessárias? Quem pode solicitar ou executar a exclusão?
- Qual volume, frequência e crescimento devem ser suportados?

### Integrações e restrições

- Quais serviços externos são obrigatórios e qual alternativa existe se falharem?
- Há stack, hospedagem, compatibilidade, prazo, orçamento ou ferramentas já decididos?
- Existem obrigações legais, regulatórias, de segurança ou privacidade?

### Sucesso e evidência

- Qual é o estado atual da métrica, a meta e como ela será medida?
- Que exemplo concreto de entrada e saída demonstra sucesso?
- Qual caso problemático precisa ser tratado desde a primeira entrega?

## Produto ou app novo

- Existe algo semelhante que o público já usa? O que não funciona nessa alternativa?
- A solução precisa ser web, mobile, desktop ou multicanal? Por quê?
- Qual hipótese de adoção é mais arriscada e como poderia ser validada cedo?

## Feature em produto existente

- A feature substitui, estende ou interfere em qual fluxo atual?
- Quais contratos, padrões, métricas e comportamentos não podem regredir?
- Há migração de dados, compatibilidade retroativa ou rollout gradual?

## Automação ou ferramenta interna

- O que dispara a automação e quem é responsável por operá-la?
- O que acontece após falha, repetição ou execução parcial?
- A operação precisa ser idempotente, auditável ou aprovada por alguém?

## Pesquisa ou problema sem solução definida

- Se o problema desaparecesse hoje, o que mudaria concretamente?
- O que já foi tentado, qual evidência existe e por que falhou?
- Qual decisão a pesquisa precisa permitir e até quando?

## Classificação das respostas

Ao registrar, diferencie:

- `CONFIRMED`: decisão explícita de autoridade competente;
- `DELEGATED`: decisão que o usuário autorizou o planejamento a tomar;
- `INFERRED`: inferência baseada em evidência, ainda não confirmada;
- `PROPOSAL`: sugestão ainda não aceita;
- `REJECTED`: opção recusada e preservada para não reaparecer;
- questão `STRUCTURAL`: pode mudar intenção, MVP, atores, arquitetura, dados centrais ou integração;
- questão `MINOR`: o planejamento pode resolver sem alterar esses elementos.
