# F01 Checkpoint

Status: PASS
Recorded at: `2026-07-29T14:58:08.7185413-03:00`
Authority: `docs/SKILL-TEAM-SDD-IMPROVEMENT-PLAN.md`, Section 18.4

## Qualified Evidence

- `baseline/validator-runs/F01-001.md`
- `baseline/validator-runs/F01-002.md`
- `baseline/validator-runs/F01-003.md`
- `baseline/validator-runs/F01-004.md`
- `baseline/validator-runs/F01-005.md`
- `baseline/validator-runs/F01-006.md`

The F01-006 task command and repository validation both exited `0`. Recovery content remains at `baseline/checkpoints/F01-prechange/`.

## Final Gate Hashes

```text
b76e758215c8155d7694890918dbcfd61df33bcf1ea28555f178627cf86482e2  scripts/validate_repository.py
9227825b54b0db93102a21b661419a06247c3921ca932abee490e84216e513e4  scripts/validate_catalog.py
ef61cea26c2797bb104a0085b0c096b36d4f15096fd8330c62026c2e7498dbd3  catalog/skills.json
047dfc28880a8f4aaf4f2a1609fe783b0ebc217701b5c1318b8899cfa570b154  catalog/compatibility.json
1cecf50f5ba524ef21868a92f0ffa420525b1a42ca2b2ae8b5f2e82c212a2022  docs/migration/advisor-planner-map.md
922e5019dbe60407c81cb41925dd7039496fe512ddf5ba16e78f2fc48fbd60b1  README.md
97260191ce419f998c57bd074bc4ec783a6f5ca582ad0b00eb5b85d0506087f0  AGENTS.md
b9902d8a71232e5a3eeb3e2a08444025c4333781d95f04f3d28840c01cda32db  tests/integration/test_flow_fixtures.py
a05a688f602f63f4f205094947678761470e02cea3243040fe4921a599d264b9  tests/integration/test_repository_contract_gate.py
82de98770c3b6762c26c9ebab3ecee09055032dcb74176485265ed964f254c86  tests/fixtures/greenfield-product/PROGRESS.md
cbfa9a89a3067259cb0e3eff6ba19bb22deceb54dd39571bb0eb4a61f4ba60cc  tests/fixtures/existing-code-bug/PROGRESS.md
6001a3934edef0f29019c38c6bf3111f247a47c12230d0fb9ab0e1f764c8ee57  tests/fixtures/ux-audit-to-plan/PROGRESS.md
35201087a26a4886a0ba7a6ff69697c52868a982b6973ea5fb6da34bc1ea481b  tests/fixtures/compact-plan/PROGRESS.md
fddb223cf2d900cc0cf91ee318bfb048b8a7c2f44b277735a52dbad7aeb7aef7  tests/fixtures/invalid-workflows/two-writers/PROGRESS.md
e2197cb7c86b956dbe5c687a4f912a8f49884f3012d69de7fa8a561420b02592  tests/fixtures/invalid-workflows/stale-revision/PROGRESS.md
54b5b6da2ec970750362346079f2909fa2af54419bd004a53b2224ca6cf70119  tests/fixtures/invalid-workflows/legacy-alias/PROGRESS.md
d0ebf42b59282dc54a08d0b4a2d24e21a2f78babd6feffae4c5241a550d97f36  tests/fixtures/invalid-workflows/placeholder-handoff/PLAN-TO-ROUTING.md
```

The prior F01 contract, validator, template, discovery, and post-plan artifacts remain qualified by their task evidence records above. Regenerate this checkpoint only as a coordinated F01 set.
