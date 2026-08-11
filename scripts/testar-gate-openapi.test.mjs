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
const WORKFLOW = resolve(RAIZ, ".github/workflows/contrato-openapi.yml");
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
  const workflow = parse(readFileSync(WORKFLOW, "utf8"));
  assert.deepEqual(workflow.permissions, { contents: "read" });
  assert.deepEqual(workflow.on.pull_request.branches, ["main"]);
  assert.deepEqual(workflow.on.push.branches, ["main"]);
  const jobs = Object.entries(workflow.jobs);
  assert.ok(jobs.length > 0, "workflow precisa ter ao menos um job");
  const passos = jobs.flatMap(([nome, job]) => {
    assert.equal(job.if, undefined, `job ${nome} não pode ter condição sem revisão do gate`);
    assert.ok(
      job.permissions === undefined || JSON.stringify(job.permissions) === JSON.stringify({ contents: "read" }),
      `job ${nome} não pode ampliar permissions`,
    );
    assert.ok(Array.isArray(job.steps) && job.steps.length > 0, `job ${nome} precisa ter steps`);
    for (const passo of job.steps) {
      assert.equal(
        passo["continue-on-error"],
        undefined,
        `step de ${nome} não pode ignorar erro`,
      );
      assert.equal(
        passo.if,
        undefined,
        `step de ${nome} não pode ter condição sem revisão do gate`,
      );
    }
    return job.steps;
  });
  const actions = passos.filter((passo) => passo.uses).map((passo) => passo.uses);
  assert.deepEqual(actions, [
    "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
    "actions/setup-node@249970729cb0ef3589644e2896645e5dc5ba9c38",
  ]);
  assert.ok(actions.every((action) => /@[0-9a-f]{40}$/.test(action)));
  for (const passo of passos.filter((item) => item.uses?.startsWith("actions/checkout@"))) {
    assert.equal(passo.with?.["persist-credentials"], false);
  }
  const comandos = passos.map((passo) => passo.run).filter(Boolean).join("\n");
  assert.match(comandos, /npm ci --ignore-scripts --no-audit/);
  assert.match(comandos, /npm run check/);
});
