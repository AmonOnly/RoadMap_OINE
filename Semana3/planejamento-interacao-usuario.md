# Planejamento preliminar de interacao com o usuario

## Objetivo
Guiar o aluno em uma trilha diaria de estudo em Fisica para o ENEM, com
conteudo completo por dia, quiz adaptativo e acompanhamento de progresso.

## Fluxo principal (web)
1. Acesso a pagina inicial.
2. Aluno informa nome, horas por dia, dias planejados, objetivo e idioma.
3. Sistema gera a trilha diaria e mostra o painel (XP, sequencia, progresso).
4. Aluno escolhe "Conteudo do dia" ou "Quiz".

## Fluxo de conteudo do dia
1. Aluno entra em /content.
2. Mapa de dias mostra bolinhas (estado: pendente ou concluido).
3. Ao clicar em um dia, o sistema carrega o conteudo detalhado:
   - visao geral
   - conceitos-chave
   - formulas
   - exemplo guiado
   - demonstracao
   - imagens
   - recursos externos
4. Aluno marca o dia como concluido e recebe XP + atualiza sequencia.

## Fluxo de quiz adaptativo
1. Aluno entra em /quiz.
2. Configura idioma e horas por dia.
3. Clica em "Iniciar quiz".
4. Sistema gera questoes com base em nivel (proficiencia) e tempo disponivel.
5. Aluno responde e recebe retorno imediato.
6. O desempenho atualiza a proficiencia do topico.

## Interacao com assistente (chat)
- O assistente coleta dados iniciais (nome, horas, dias, objetivo).
- Sugere a proxima acao (abrir conteudo do dia ou quiz).
- Reforca a rotina diaria (mensagens curtas, motivacionais).

## Estados e mensagens
- Estado inicial: "Bem-vindo, configure sua rotina."
- Estado ativo: "Dia selecionado, conteudo pronto."
- Estado quiz: "Questao em andamento, aguarde resposta."
- Estado concluido: "Dia concluido, XP e sequencia atualizados."

## Persistencia
- Preferencias do usuario (nome, horas, dias, idioma) via SQLite.
- Progresso diario (dias concluidos, XP, sequencia).
- Proficiencia por topico para adaptar o quiz.

## Consideracoes de usabilidade
- Botao principal sempre visivel (CTA).
- Retorno imediato apos acao (ex: concluir dia, responder questao).
- Linguagem simples e objetiva (nivel ensino medio).
