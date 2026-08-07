# Runbook — Fonte mudou de formato

**Gatilho:** validação de esquema falhou na chegada; taxa de quarentena subiu; ou o Curador alertou divergência estrutural. Este é o **modo de falha dominante da borda** (C4 contexto) — o desenho já congelou a carga automaticamente; o runbook é o caminho de volta.

## Passos

1. **Confirmar o congelamento.** A carga da fonte afetada deve estar parada com o arquivo em quarentena. Se algo malformado entrou na base, isso é outro incidente (ver rollback bitemporal no passo 7).
2. **Diagnosticar a mudança.** Diff entre o esquema recebido e o esperado (o conector registra ambos). Classificar:
   - **Aditiva** (coluna nova) → baixo risco;
   - **Renomeação/reordenação** → médio;
   - **Semântica** (mesmo nome, significado novo — ex.: código de município mudou de padrão) → **alto risco, o diff não acusa**: comparar distribuições de valores, não só cabeçalhos.
3. **Verificar se é oficial.** Mudança pode ser erro de publicação da fonte (acontece). Checar aviso no portal da fonte; aguardar 1 dia útil antes de adaptar a mudanças não anunciadas — a fonte pode republicar.
4. **Adaptar o conector** (Strategy/Adapter — a mudança fica no adaptador, o domínio não vê). Atualizar o esquema esperado versionado.
5. **Atualizar o [catálogo de fontes](../../dados/catalogo-fontes.md)** — entrada de changelog da fonte com data, natureza da mudança e link do diff. O CI de docs exige isso junto do código.
6. **Reprocessar da zona bruta** os arquivos em quarentena, na ordem de chegada.
7. **Se dado malformado entrou:** correção bitemporal (operação 2 do [modelo](../../dados/modelo-bitemporal.md)) — nunca `UPDATE`. A versão errada permanece consultável as-of; é assim que o sistema conta a própria história.
8. **Mudança semântica → post-mortem curto** com o que o monitor de distribuição deveria ter pego.

## O que NÃO fazer

- Ajustar o parser para "engolir" o formato novo sem registrar no catálogo — a próxima pessoa herda um esquema fantasma.
- Carregar por cima da carga anterior "para destravar" — quarentena existe para isso não acontecer.
- Tratar volume anômalo como formato: dump 30% menor com esquema válido é o [runbook vizinho](dump-mensal-ausente-ou-anomalo.md).
