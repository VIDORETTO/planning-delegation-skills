# Checklist de UI/UX (Interface e Experiência)

UI e UX são tratadas juntas aqui porque, na prática, quase todo achado mistura os dois (um botão mal posicionado é visual E de fluxo ao mesmo tempo). Use isto como lente de observação, não como formulário a preencher item por item — só documente o que realmente notar.

## Primeira impressão e hierarquia
- O que mais chama atenção na tela é de fato a coisa mais importante dela?
- Dá pra entender o propósito da tela em poucos segundos, sem precisar ler tudo?

## Consistência
- Botões, cards, ícones, cores e nomes de conceitos são usados do mesmo jeito em todas as telas, ou variam sem motivo?
- O mesmo tipo de ação (editar, excluir, filtrar) se comporta igual em todos os lugares?

## Clareza visual
- Contraste de texto suficiente para leitura confortável; cor não é o único jeito de indicar erro/sucesso/status.
- Espaçamento e alinhamento parecem intencionais, não aleatórios.

## Fluxo e esforço do usuário
- Quantos passos até a ação principal da tela? Algum passo parece desnecessário?
- Existe um caminho óbvio, ou o usuário precisaria "adivinhar" o que fazer?
- Valores padrão e atalhos reduzem trabalho manual quando fazem sentido?

## Estados da tela
- Carregando, vazio (sem dados ainda) e erro têm uma mensagem clara e útil, ou a tela só "fica em branco"/trava?
- Mensagens de erro dizem o que fazer para corrigir, não só que "algo deu errado"?
- Toda ação do usuário gera uma resposta visível (confirmação, mudança de estado, feedback)?

## Prevenção de erro
- Ações difíceis de desfazer (excluir, cancelar, enviar) pedem confirmação?
- Formulários validam em tempo real ou só depois de tentar enviar tudo?

## Acessibilidade básica
- Dá pra navegar com teclado em uma ordem lógica?
- Áreas clicáveis/toque grandes o suficiente (principalmente mobile)?

## Responsividade (quando aplicável)
- A tela se adapta bem a mobile/tablet/desktop, ou tem corte, sobreposição ou scroll horizontal indevido?

## Descobribilidade
- Funcionalidades úteis estão fáceis de encontrar, ou escondidas demais?
- Um usuário novo entenderia essa tela sem precisar de ajuda externa?

## Como registrar um achado
Cada achado vai marcado com uma destas etiquetas (ver `references/etiquetas-de-achado.md` para o racional completo):

- **[Fato]** algo objetivamente quebrado ou incoerente (ex: botão não faz nada, contraste ilegível).
- **[Sugestão]** uma opinião de melhoria, não um erro (ex: "esse fluxo poderia ter uma etapa a menos").
- **[Ponto aberto]** algo que depende de uma decisão de produto/negócio que só o usuário pode tomar (ex: "vale a pena simplificar esse formulário ou os campos extras são exigência legal?").

Formato:
- **Onde**: elemento/tela específico
- **[Etiqueta] O que**: descrição objetiva
- **Por que importa**: impacto no usuário (se for relevante explicar)
- **Ideia de solução**: mudança concreta (quando fizer sentido propor uma)
