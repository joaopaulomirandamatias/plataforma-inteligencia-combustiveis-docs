# Runbook — Verificar produção logo após um deploy

**Armadilha catalogada (2026-08-08):** durante a troca de versão, **as duas versões respondem** — o roteador serve ora a antiga, ora a nova, até o rollout estabilizar. Quem verifica produção nesse instante pode capturar o estado ANTIGO e reportá-lo como se fosse o novo (ou vice-versa). Aconteceu numa verificação de payload: um fetch pegou 1 localizador (versão antiga), o fetch seguinte pegou 0 (versão nova).

## Regra

1. **Fetch único e determinístico:** baixe a resposta UMA vez para arquivo (`curl -o`) e analise o arquivo — não faça dois `curl` e compare, porque cada um pode bater numa versão diferente.
2. **Espere a estabilização** antes de afirmar: confirme `status: Online` e que o healthcheck do deploy NOVO passou, ou repita o fetch até dois consecutivos concordarem.
3. **Grep conta linha, não ocorrência:** `grep -c` num HTML minificado de uma linha devolve 1 para qualquer match. Para contar ocorrências reais: `grep -o PADRÃO arquivo | wc -l`.
4. Se o resultado for inesperado, **reproduza no arquivo salvo** antes de escalar — não conclua de uma leitura que pode ter pego a versão em trânsito.
