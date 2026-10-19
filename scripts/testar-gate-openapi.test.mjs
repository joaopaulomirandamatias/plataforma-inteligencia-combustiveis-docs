import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import test from "node:test";
import { parse } from "yaml";

const RAIZ = resolve(import.meta.dirname, "..");
const REDOCLY = resolve(RAIZ, "node_modules/.bin/redocly");
const CONFIG = resolve(RAIZ, "redocly.yaml");
const CONTRATO = resolve(RAIZ, "docs/api/openapi.yaml");
const WORKFLOW = resolve(RAIZ, ".woodpecker/contrato-openapi.yml");
const METODOS = new Set(["get", "put", "post", "delete", "options", "head", "patch", "trace"]);

function refsInternas(valor) {
  if (Array.isArray(valor)) {
    valor.forEach(refsInternas);
    return;
  }
  if (!valor || typeof valor !== "object") return;
  if ("$ref" in valor) {
    assert.equal(typeof valor.$ref, "string", "$ref precisa ser texto");
    assert.match(valor.$ref, /^#\//, "$ref externo/remoto é proibido no contrato canônico");
  }
  Object.values(valor).forEach(refsInternas);
}

function operacoesValidas(documento) {
  assert.equal(documento.openapi, "3.1.0", "o contrato precisa permanecer OpenAPI 3.1.0");
  assert.ok(documento.paths && typeof documento.paths === "object", "paths é obrigatório");
  const ids = new Set();
  for (const [caminho, item] of Object.entries(documento.paths)) {
    for (const [metodo, operacao] of Object.entries(item)) {
      if (!METODOS.has(metodo)) continue;
      assert.equal(typeof operacao.operationId, "string", `${metodo.toUpperCase()} ${caminho} sem operationId`);
      assert.ok(operacao.operationId.length > 0, `${metodo.toUpperCase()} ${caminho} com operationId vazio`);
      assert.ok(!ids.has(operacao.operationId), `operationId duplicado: ${operacao.operationId}`);
      ids.add(operacao.operationId);
    }
  }
  assert.ok(ids.size > 0, "o contrato precisa declarar operações");
}

function preflight(caminho) {
  const documento = parse(readFileSync(caminho, "utf8"));
  refsInternas(documento);
  operacoesValidas(documento);
}

function resolverRefLocal(documento, referencia) {
  assert.match(referencia, /^#\//, "o gate estrito só resolve referências locais");
  return referencia
    .slice(2)
    .split("/")
    .map((parte) => parte.replaceAll("~1", "/").replaceAll("~0", "~"))
    .reduce((atual, parte) => atual?.[parte], documento);
}

function exigirObjetosFechados(documento, schema, caminho, refsVisitadas = new Set()) {
  assert.ok(schema && typeof schema === "object", `${caminho} precisa declarar schema`);

  if (schema.$ref) {
    if (refsVisitadas.has(schema.$ref)) return;
    refsVisitadas.add(schema.$ref);
    const resolvido = resolverRefLocal(documento, schema.$ref);
    assert.ok(resolvido, `${caminho} aponta para ref ausente: ${schema.$ref}`);
    exigirObjetosFechados(documento, resolvido, `${caminho} -> ${schema.$ref}`, refsVisitadas);
    return;
  }

  for (const composicao of ["allOf", "anyOf", "oneOf"]) {
    for (const [indice, parte] of (schema[composicao] ?? []).entries()) {
      exigirObjetosFechados(documento, parte, `${caminho}.${composicao}[${indice}]`, refsVisitadas);
    }
  }

  const tipos = Array.isArray(schema.type) ? schema.type : [schema.type];
  if (tipos.includes("object") || schema.properties) {
    assert.equal(
      schema.additionalProperties,
      false,
      `${caminho} voltou a aceitar propriedades desconhecidas`,
    );
    for (const [nome, propriedade] of Object.entries(schema.properties ?? {})) {
      exigirObjetosFechados(documento, propriedade, `${caminho}.${nome}`, refsVisitadas);
    }
  }

  if (tipos.includes("array") || schema.items) {
    exigirObjetosFechados(documento, schema.items, `${caminho}[]`, refsVisitadas);
  }
}

function lint(caminho) {
  return spawnSync(REDOCLY, ["lint", "--config", CONFIG, caminho], {
    cwd: RAIZ,
    encoding: "utf8",
    env: { ...process.env, NO_COLOR: "1" },
  });
}

function contratoMinimo({ ref = "#/components/schemas/Resposta", operationId = "consultar", exemplo = "ok" } = {}) {
  return {
    openapi: "3.1.0",
    info: { title: "Contrato sintético", version: "1.0.0" },
    paths: {
      "/teste": {
        get: {
          operationId,
          responses: {
            "200": {
              description: "OK",
              content: {
                "application/json": { schema: { $ref: ref }, example: { valor: exemplo } },
              },
            },
          },
        },
      },
    },
    components: {
      schemas: {
        Resposta: {
          type: "object",
          required: ["valor"],
          properties: { valor: { type: "integer" } },
        },
      },
    },
  };
}

test("contrato canônico passa preflight e lint com refs resolvidas", () => {
  preflight(CONTRATO);
  execFileSync(REDOCLY, ["lint", "--config", CONFIG, CONTRATO], {
    cwd: RAIZ,
    stdio: "pipe",
    env: { ...process.env, NO_COLOR: "1" },
  });
});

test("objetos públicos de saúde e preços recusam propriedades desconhecidas", () => {
  const documento = parse(readFileSync(CONTRATO, "utf8"));
  for (const caminho of ["/saude", "/v1/precos"]) {
    const schema = documento.paths[caminho].get.responses["200"].content["application/json"].schema;
    exigirObjetosFechados(documento, schema, `GET ${caminho} 200`);
  }
});

test("saúde e preços exigem somente as chaves estáveis observadas", () => {
  const schemas = parse(readFileSync(CONTRATO, "utf8")).components.schemas;
  const obrigatorias = [
    [schemas.Saude, ["versao", "estado", "versao_snapshot", "contagens", "cargas", "execucoes"]],
    [schemas.Saude.properties.contagens, ["cadastro", "pmqc", "preco", "atendimento"]],
    [schemas.Saude.properties.cargas.items, ["fonte", "carga_id", "coletado_em", "cargas", "linhas_carregadas"]],
    [schemas.Saude.properties.execucoes.items, ["fonte", "ultima_execucao", "acao"]],
    [schemas.PaginaPrecos, ["itens", "proximo_cursor", "as_of", "versao_snapshot", "limite", "filtros"]],
    [schemas.PrecoSemanal, ["posto_id", "produto", "valor_venda", "unidade", "bandeira", "municipio", "uf", "regiao", "semana_inicio", "semana_fim", "fonte", "localizador"]],
    [schemas.FiltrosPrecos, ["produto", "uf", "municipio", "semana", "semana_de", "semana_ate"]],
  ];

  for (const [schema, esperado] of obrigatorias) {
    assert.deepEqual([...schema.required].sort(), [...esperado].sort());
  }
  assert.deepEqual(schemas.Saude.properties.estado.enum, ["pronto"]);
});

test("ficha pública exige PMQC estruturado, derivado, fechado e tri-state", () => {
  const documento = parse(readFileSync(CONTRATO, "utf8"));
  const schemas = documento.components.schemas;
  exigirObjetosFechados(documento, schemas.Posto, "Posto");

  assert.ok(schemas.Posto.required.includes("qualidade_combustivel"));
  assert.equal(
    documento.paths["/v1/postos/{posto_id}"].get["x-schema-promocao"]
      .qualidade_combustivel,
    "candidate-local",
  );
  assert.equal(schemas.QualidadeCombustivel["x-promocao"], "candidate-local");
  assert.deepEqual(
    [...schemas.QualidadeCombustivel.required].sort(),
    ["agrupamentos", "identidade_agrupamento", "limite", "truncado"],
  );
  assert.deepEqual(
    schemas.QualidadeCombustivel.properties.identidade_agrupamento.enum,
    ["derivada"],
  );
  assert.deepEqual(schemas.QualidadeCombustivel.properties.limite.enum, [8]);
  assert.equal(schemas.QualidadeCombustivel.properties.truncado.type, "boolean");
  assert.equal(schemas.QualidadeCombustivel.properties.agrupamentos.maxItems, 8);
  assert.deepEqual(
    [...schemas.ContagensPMQC.required].sort(),
    ["conforme", "nao_classificado", "nao_conforme"],
  );
  assert.deepEqual(schemas.EnsaioPMQC.properties.conforme.type, ["boolean", "null"]);
  assert.deepEqual(schemas.EnsaioPMQC.properties.classificacao.enum, [
    "conforme",
    "não conforme",
    "não classificado",
  ]);
  for (const campo of ["amostra_id", "sequencia", "localizador", "coordenadas"]) {
    assert.equal(campo in schemas.AgrupamentoPMQC.properties, false);
    assert.equal(campo in schemas.EnsaioPMQC.properties, false);
  }
});

test("gate recusa ref ausente, operationId duplicado e exemplo incompatível", async () => {
  const pasta = await mkdtemp(join(tmpdir(), "pic-openapi-"));
  try {
    const casos = [
      [
        "ref-ausente.json",
        contratoMinimo({ ref: "#/components/schemas/Ausente", exemplo: 1 }),
        "no-unresolved-refs",
      ],
      [
        "operation-id-duplicado.json",
        {
          ...contratoMinimo({ exemplo: 1 }),
          paths: {
            ...contratoMinimo({ exemplo: 1 }).paths,
            "/outro": contratoMinimo({ exemplo: 1 }).paths["/teste"],
          },
        },
        null,
      ],
      [
        "exemplo-invalido.json",
        contratoMinimo({ exemplo: "não é inteiro" }),
        "no-invalid-media-type-examples",
      ],
    ];
    for (const [nome, documento, regra] of casos) {
      const caminho = join(pasta, nome);
      writeFileSync(caminho, JSON.stringify(documento));
      if (nome === "operation-id-duplicado.json") {
        assert.throws(() => preflight(caminho), /duplicado/);
      } else {
        const resultado = lint(caminho);
        assert.notEqual(resultado.status, 0, `${nome} deveria falhar no lint`);
        assert.match(
          `${resultado.stdout}\n${resultado.stderr}`,
          new RegExp(regra),
          `${nome} deveria falhar pela regra esperada`,
        );
      }
    }
  } finally {
    await rm(pasta, { recursive: true, force: true });
  }
});

test("preflight recusa referência remota antes de qualquer resolução", async () => {
  const pasta = await mkdtemp(join(tmpdir(), "pic-openapi-ref-"));
  try {
    const caminho = join(pasta, "remoto.json");
    writeFileSync(caminho, JSON.stringify(contratoMinimo({ ref: "https://canario.invalid/schema.json" })));
    assert.throws(() => preflight(caminho), /externo\/remoto/);
  } finally {
    await rm(pasta, { recursive: true, force: true });
  }
});

test("workflow é read-only, pinado e executa o lockfile e o gate", () => {
  // O gate mudou de forja: o CI agora é o Woodpecker, e este teste passou a
  // ler `.woodpecker/contrato-openapi.yml`. A PROPRIEDADE vigiada é a mesma —
  // a configuração do CI não pode ganhar escapatória sem revisão — mas três
  // asserções não têm equivalente e uma trocou de forma:
  //
  //  - `permissions: contents: read` era do GITHUB_TOKEN, que só existe no
  //    Actions. O Woodpecker não injeta token de forja no pipeline: não há
  //    permissão a restringir porque não há credencial a vazar. Some.
  //  - `persist-credentials: false` era do `actions/checkout`. O clone do
  //    Woodpecker não deixa credencial no .git/config. Some.
  //  - PINAGEM: no Actions eram `uses:` fixados por SHA de 40 hex. Aqui não há
  //    ação de terceiro; o que executa é uma IMAGEM. Então a pinagem que este
  //    teste cobra é de imagem com VERSÃO EXATA — `latest` e tag flutuante
  //    reabrem exatamente o buraco que o SHA fechava.
  const workflow = parse(readFileSync(WORKFLOW, "utf8"));

  // Dispara em push e em pull_request, e só em main — igual ao `on:` antigo.
  const gatilhos = workflow.when;
  assert.ok(Array.isArray(gatilhos) && gatilhos.length > 0, "workflow precisa declarar `when`");
  for (const gatilho of gatilhos) {
    assert.equal(gatilho.branch, "main", "gate só pode disparar em main");
  }
  assert.deepEqual(
    gatilhos.map((gatilho) => gatilho.event).sort(),
    ["pull_request", "push"],
    "gate precisa cobrir push E pull_request",
  );

  const passos = workflow.steps;
  assert.ok(Array.isArray(passos) && passos.length > 0, "workflow precisa ter passos");

  for (const passo of passos) {
    // `when` no passo é o equivalente do `if:` do Actions: condição que faz o
    // gate deixar de rodar sem ninguém notar.
    assert.equal(passo.when, undefined, `passo ${passo.name} não pode ter condição sem revisão do gate`);
    // `failure: ignore` é o `continue-on-error`: o passo fica vermelho e o
    // pipeline segue verde.
    assert.equal(passo.failure, undefined, `passo ${passo.name} não pode ignorar erro`);
    // Imagem com versão exata. Recusa `node`, `node:latest` e `node:24`.
    assert.match(
      passo.image,
      /^[a-z0-9./-]+:\d+\.\d+\.\d+$/,
      `passo ${passo.name} precisa de imagem pinada em versão exata (veio "${passo.image}")`,
    );
  }

  const comandos = passos.flatMap((passo) => passo.commands ?? []).join("\n");
  assert.match(comandos, /npm ci --ignore-scripts --no-audit/);
  assert.match(comandos, /npm run check/);
});
