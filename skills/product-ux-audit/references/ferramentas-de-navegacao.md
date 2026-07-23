# Ferramentas de navegação real

O requisito central desta skill é analisar a **tela efetivamente renderizada**, nunca uma
descrição, um mockup ou uma leitura do código-fonte. Como a skill é genérica para qualquer
projeto (web, mobile, desktop), o mecanismo exato de navegação muda de ambiente para ambiente.
Não assuma qual está disponível — confira o que existe agora antes de prosseguir.

## Como decidir

1. **Verifique conectores/MCPs de navegação já disponíveis** — ex: um MCP de browser automation
   (Playwright, Chrome DevTools), uma extensão de navegador conectada, ou uma ferramenta de
   computer use com tela/display. Use o que já estiver disponível em vez de propor instalar algo
   novo.
2. **Se estiver em um ambiente com bash e acesso de rede liberado para o domínio do produto**,
   considere instalar Playwright (`pip install playwright --break-system-packages && playwright
   install chromium`) como alternativa para automatizar navegação + captura de tela. Isso só
   funciona se a rede do ambiente permitir acessar o domínio do produto — se a política de rede
   for restrita a poucos domínios, avise o usuário em vez de tentar forçar.
3. **Produtos mobile** precisam de um dispositivo real ou simulador acessível (via ferramenta de
   automação mobile, espelhamento de tela, ou similar). Sem isso, não há como ver a renderização
   real — diga isso ao usuário em vez de inferir a partir de descrições.
4. **Produtos desktop** precisam de automação em nível de sistema operacional ou compartilhamento
   de tela. Mesma lógica: sem acesso real à interface renderizada, pare e avise.

## Regra de ouro

Se, em qualquer momento, a única forma de "ver" a tela for através de uma descrição do usuário,
uma captura enviada manualmente sem poder navegar de forma independente, ou o código-fonte do
frontend, **isso não cumpre o requisito desta skill**. É melhor pausar e explicar o que falta do
que produzir uma auditoria baseada em suposição — o valor inteiro desta skill vem de constatar o
que está de fato na tela, não de imaginar como ela provavelmente está.

Se mais de uma ferramenta plausível estiver disponível ao mesmo tempo e não for óbvio qual usar,
pergunte ao usuário em vez de escolher sozinho — mas não pergunte se só existe uma opção razoável.
