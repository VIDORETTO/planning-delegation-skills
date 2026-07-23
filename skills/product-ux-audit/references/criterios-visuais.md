# Critérios visuais objetivos

Este checklist existe para que a auditoria produza achados **reproduzíveis e concretos**, não
opiniões de gosto disfarçadas de análise técnica. Ao analisar uma página (Passo 3 do SKILL.md),
percorra cada categoria abaixo, uma de cada vez, e só registre um achado quando conseguir apontar
o sintoma observável — não escreva "isso não ficou legal" sem conseguir dizer exatamente o que,
onde, e por quê.

Para cada achado, decida a classificação usando a seção "Como classificar" no final deste
arquivo.

---

## 1. Espaços vazios excessivos ou mal distribuídos

O que procurar:
- Áreas em branco grandes sem função (força scroll desnecessário sem conteúdo real acima da dobra)
- Margens/respiros diferentes entre seções visualmente equivalentes (ex: 80px acima de uma seção
  e 16px acima da seção seguinte, sem motivo de hierarquia)
- Espaço morto causado por colunas de grid não preenchidas
- Estados vazios com muito espaço em branco e nenhuma orientação sobre o que fazer a seguir

Como checar: compare o respiro entre elementos repetidos (cards, linhas de lista, campos de
formulário) lado a lado — se um tem 12px de espaço acima e outro visualmente equivalente tem 24px,
sem que o conteúdo justifique, é um achado.

## 2. Elementos desproporcionais entre si

O que procurar:
- Ação principal (CTA) menor ou com peso visual menor que uma ação secundária ao lado
- Ícone maior que o texto que o acompanha, competindo por atenção
- Avatares/thumbnails com tamanhos inconsistentes entre itens de uma mesma lista
- Botões do mesmo grupo com alturas/paddings diferentes

Como checar: identifique qual é a ação principal pretendida da tela (pelo contexto/copy) e
compare o tamanho/peso visual dela com as ações concorrentes ao redor. Se a secundária "ganha" a
atenção, é um achado.

## 3. Alinhamento quebrado / grid inconsistente

O que procurar:
- Elementos que deveriam compartilhar uma borda (esquerda, direita, ou linha de base) mas estão a
  poucos pixels de distância um do outro
- Colunas de um grid com larguras diferentes sem razão aparente
- Labels de formulário e campos não alinhados verticalmente
- Ícone e texto com linha de base (baseline) desencontrada

Como checar: trace guias imaginárias (verticais/horizontais) pelas bordas de elementos vizinhos —
se 3 ou mais elementos deveriam compartilhar uma borda mas não compartilham, é um achado.

## 4. Hierarquia tipográfica fraca

O que procurar:
- Título e corpo de texto com pouca diferença de peso/tamanho/cor
- Muitos níveis de heading parecidos entre si, sem uma ordem de leitura clara
- Texto de corpo com mais destaque visual do que o título da seção
- Ausência de uma ordem clara de leitura (o que ler primeiro, segundo, terceiro)

Como checar: sem ler o conteúdo do texto, dá para saber qual é o título principal e qual é o texto
de apoio só pela diferença tipográfica? Se não, a hierarquia está fraca.

## 5. Paleta de cor e contraste inconsistentes

O que procurar:
- O mesmo elemento semântico (botão primário, texto de erro, cor de link) renderizado com cores
  diferentes em páginas/telas diferentes, sem razão documentada
- Combinações de texto/fundo com contraste baixo, difíceis de ler
- Uma cor de destaque usada tanto para "sucesso" quanto para "informativo", misturando significados

Como checar: catalogue a cor usada para o mesmo elemento (ex: botão primário) em cada página já
auditada até agora — qualquer desvio é candidato a achado. Pode haver um motivo legítimo (ex: uma
seção com identidade visual própria) — nesse caso, classifique como opinião/depende, não fato.

## 6. Texto cortado, overflow, scroll horizontal indevido

O que procurar:
- Labels truncados sem reticências ou tooltip explicando o texto completo
- Texto sobrepondo outro elemento
- Container gerando scrollbar horizontal em desktop quando o conteúdo deveria quebrar linha
- Botões com texto quebrando de forma estranha no meio de uma palavra

Como checar: esta categoria costuma ser a mais objetiva e menos discutível de todas — na dúvida,
prefira classificar como `[FATO OBJETIVO]`.

## 7. Padrões repetidos com variações sem motivo

O que procurar:
- Cards similares (ex: 5 cards de produto) com espaçamento interno diferente entre si
- Linhas de lista com alturas alternadas não explicadas pelo conteúdo
- Conjunto de ícones misturando estilos/pesos diferentes (ex: outline e filled juntos sem padrão)

Como checar: compare as instâncias repetidas lado a lado (recorte os screenshots se ajudar) e veja
se o espaçamento/tamanho difere sem que o conteúdo justifique.

## 8. Falta de feedback visual em ações do usuário / loading, vazio e erro mal tratados

O que procurar:
- Clique em botão sem nenhum reconhecimento visual (sem estado de disabled/spinner/hover)
- Mensagem de erro genérica ou em branco, sem orientação do que fazer
- Estado vazio que é só um espaço em branco, sem explicar o que fazer a seguir
- Carregamento sem skeleton/spinner, deixando a tela com aparência de travada

Como checar: quando for razoavelmente alcançável sem engenharia excessiva, tente de verdade essas
situações (submeter um formulário vazio, buscar algo sem resultado, aguardar um carregamento) e
registre se aparece um feedback real.

## 9. Falta geral de harmonia / dificuldade de entendimento

Esta é a categoria "guarda-chuva" — use-a **só** quando um problema real não se encaixa claramente
nas categorias 1 a 8. Quando usar, seja ainda mais rigoroso em fundamentar com um sintoma
observável e específico, por exemplo:

> "A primeira leitura da tela não deixa claro qual é a ação principal, porque há 4 elementos com
> peso visual semelhante competindo por atenção (categoria 2 + categoria 4 combinadas)."

em vez de:

> "Não gostei muito do design desta tela."

Se um achado desta categoria puder ser reescrito apontando para uma das categorias 1-8, prefira
fazer isso — a categoria 9 deve ser rara no relatório final, não o destino padrão de tudo que "não
parece bom".

---

## Como classificar cada achado

- **`[FATO OBJETIVO]`** — mensurável/verificável sem depender de gosto: overflow, corte de texto,
  contraste abaixo do mínimo legível, desalinhamento visível em pixels, o mesmo elemento semântico
  usando valores diferentes em telas diferentes.
- **`[OPINIÃO/SUGESTÃO]`** — crítica de design válida e fundamentada em princípios, mas onde
  pessoas razoáveis poderiam discordar da gravidade ou da solução exata. A maioria dos julgamentos
  de proporção, espaçamento e hierarquia cai aqui.
- **`[DEPENDE DO DONO DO PRODUTO]`** — é de fato uma inconsistência, mas pode ser uma escolha
  intencional de marca/estratégia que só o dono do produto pode confirmar (ex: um layout
  propositalmente assimétrico numa página de campanha específica).

Não force tudo para `[FATO OBJETIVO]` só para parecer mais rigoroso — isso não é o objetivo aqui;
o objetivo é honestidade sobre o que é mensurável e o que é julgamento.
