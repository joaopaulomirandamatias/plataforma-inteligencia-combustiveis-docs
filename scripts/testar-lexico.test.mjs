import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";

/**
 * Guarda do léxico canônico.
 *
 * Este arquivo virou FONTE, e não mais uma das duas cópias: o backend e o site
 * comparam os espelhos deles contra ele, cada um no seu CI. A consequência é
 * que um defeito aqui não fica contido aqui — ele quebra os dois CIs a jusante,
 * e lá o sintoma chega deformado ("não consegui ler o léxico"), longe da causa.
 *
 * Por isso a validação estrutural mora do lado da fonte: o erro fica vermelho
 * no PR que o introduziu, com o nome do campo errado, em vez de aparecer dois
 * repositórios adiante.
 */

const RAIZ = resolve(import.meta.dirname, "..");
const LEXICO = resolve(RAIZ, "docs/agentes/lexico-bloqueado.json");

function carregar() {
  return JSON.parse(readFileSync(LEXICO, "utf8"));
}

test("o léxico canônico é JSON válido e tem a forma que os espelhos leem", () => {
  const doc = carregar();
  assert.ok(Array.isArray(doc.termos), "`termos` precisa ser uma lista");
  for (const [i, termo] of doc.termos.entries()) {
    assert.equal(typeof termo.radical, "string", `termos[${i}] sem \`radical\` textual`);
    assert.ok(termo.radical.length > 0, `termos[${i}] com \`radical\` vazio`);
    assert.equal(typeof termo.alcanca, "string", `termos[${i}] (${termo.radical}) sem \`alcanca\``);
    assert.ok(termo.alcanca.length > 0, `termos[${i}] (${termo.radical}) com \`alcanca\` vazia`);
  }
});

test("a lista não está vazia", () => {
  // A forma extrema da falha: um léxico vazio libera QUALQUER texto, e os dois
  // espelhos continuariam "idênticos à fonte" — verdes, concordando em nada.
  // Igualdade entre camadas não é a propriedade que protege; a lista existir é.
  const doc = carregar();
  assert.ok(doc.termos.length > 0, "léxico vazio desliga a política inteira sem ficar vermelho");
});

test("nenhum radical aparece duas vezes", () => {
  // Duplicata é sintoma de merge malfeito, e faz o detector devolver o mesmo
  // termo repetido para quem lista as violações.
  const radicais = carregar().termos.map((t) => t.radical);
  const repetidos = radicais.filter((r, i) => radicais.indexOf(r) !== i);
  assert.deepEqual(repetidos, [], `radicais duplicados: ${repetidos.join(", ")}`);
});

test("os termos são RADICAIS, não palavras flexionadas", () => {
  // A propriedade 1 do detector, escrita como teste: em português o feminino
  // troca a vogal FINAL. "suspeito" na lista deixaria "suspeita" passar — e os
  // substantivos deste domínio são majoritariamente femininos. Este é o erro
  // exato que já aconteceu, então ele fica versionado como guarda.
  const radicais = new Set(carregar().termos.map((t) => t.radical));
  for (const flexionada of ["suspeito", "culpado", "garantido", "criminoso", "comprovado", "provado"]) {
    assert.ok(
      !radicais.has(flexionada),
      `"${flexionada}" é palavra flexionada, não radical — o feminino escaparia`,
    );
  }
  for (const radical of ["suspeit", "culpad", "garantid", "criminos", "comprovad", "provad"]) {
    assert.ok(radicais.has(radical), `o radical "${radical}" sumiu da lista`);
  }
});

test("a prosa que sustenta o detector continua no arquivo", () => {
  // As duas propriedades do detector são a parte que impede alguém de
  // "simplificar" o casamento e reabrir o buraco. Elas moravam num docstring do
  // backend — repositório privado, invisível para quem lê o contrato. Se
  // alguém enxugar o JSON para uma lista pelada, isto fica vermelho.
  const doc = carregar();
  assert.ok(doc.detector, "o bloco `detector` explica POR QUE a lista é de radicais com fronteira");
  for (const chave of [
    "propriedade_1_alcancar_a_flexao_de_genero",
    "propriedade_2_nao_disparar_dentro_de_outra_palavra",
  ]) {
    const prop = doc.detector[chave];
    assert.ok(prop, `\`detector.${chave}\` é normativo e não pode sumir`);
    assert.ok(prop.regra?.length > 0, `\`detector.${chave}.regra\` vazia`);
    assert.ok(prop.porque?.length > 0, `\`detector.${chave}.porque\` vazia`);
  }
});
