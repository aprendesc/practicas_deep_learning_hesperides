# Project organization

This repository contains materials for four 90-minute Deep Learning practical classes at Universidad de las Hespérides. Base the content strongly on the complete course notes and available notebooks.

## Main separation

The project has two parallel areas:

- `workshop/` is the public distribution for students. Git tracks it. It must never contain solutions, private teacher hints, or information to lead the class.
- `professor/` is the teacher's private area. Git excludes it. It is a solved and enriched clone of `workshop/`.

Do not recreate the former `data/`, `laboratorio/`, `locked/`, `recursos/`, or `scripts/` folders at the root. Their contents were classified into the areas described below.

## Student workshop

`workshop/` contains:

- `clases_sincronas/`: unlocked materials for synchronous classes. It currently contains only `capitulo_1.ipynb`. Chapters 2–5 remain exclusively in `professor/` until publication.
- `tareas/`: practical assignments for students to solve. Exercise statements must contain no solutions.
- The notebooks are self-contained. The build embeds the necessary Python support and images.

Put no content in `workshop/` outside the two folders above. Notebooks must run with the environment defined at the root by `pyproject.toml` and `uv.lock`. Store downloadable datasets in the user cache.

## Private teacher area

`professor/` preserves the course's complete executable structure:

- `clases_sincronas/`: the five course notebooks, enriched with `Guía docente y soluciones` and, when prepared, a `Guion docente`. Copy only the unlocked chapter to workshop. Tag private sections `professor-only`. Add `teacher-guide` to the script.
- `tareas/`: solved or enriched versions of student assignments.
Teacher copies may contain solutions, graduated hints, frequent errors, session questions, expected times, and any information that must remain unavailable to students.

Besides `clases_sincronas/` and `tareas/`, `professor/` contains `resources/`. This folder holds all teaching and build materials outside the deliverable clone.
After a teacher notebook receives manual additions, edit it directly in `professor/`. Before regenerating it from workshop, preserve those additions.

## Teaching resources and build

All materials used to design, generate, or validate notebooks reside in `professor/resources/`:

- `notas/`: the course index and complete notes. The five original sessions and index still need recovery. This folder's README lists the expected files.
- `fuentes_d2l/`: the complete original Dive into Deep Learning corpus previously stored in `locked/`.
- `medios/`: master copy of illustrations, original figures, and licenses.
- `scripts/`: builders, editorial transformations, manifests, and validator.
- `documentacion/`: provenance, editorial decisions, and validation evidence.
- `cache_datos/`: previously downloaded datasets to accelerate local tests. This is a private cache, not a tracked dependency.

## Update workflow

The student version is the canonical source for published content. Locked chapters reside only in `professor/`. Do not manually edit the same public cells in parallel in both areas.

After modifying the material:

1. When applicable, rebuild public notebooks with `professor/resources/scripts/build_laboratorios.py`.
2. Make them self-contained with `professor/resources/scripts/make_workshop_self_contained.py`.
3. Rebuild the combined solution guides with `professor/resources/results/build_respuestas.py`.
4. Regenerate the teacher mirror with `professor/resources/scripts/build_professor_materials.py`.
5. Merge each chapter into one class with `professor/resources/scripts/fusionar_clases_sincronas.py`.
6. Verify that notebooks in `workshop/` contain no `professor-only` cells.
7. Verify that each notebook in `professor/clases_sincronas/` retains its private sections.
   Verify that prepared chapters include their teacher script.
8. Check affected notebooks from their final location.
   Verify that no dependencies on external files remain.

Run commands from the root with `uv run python <ruta-del-script>`.

## Content criteria

### Local class generation skill

- When creating or refining synchronous class notebooks, read and use `sync_lesson_generator` at `professor/resources/skills/sync_lesson_generator/SKILL.md`.
  This private project resource is reusable for other chapters and courses. It is not a global installation.
- It covers narrative without redundancy, academic theory for students, and red bullets with bold microexplanations and natural first-person-plural speech.
  It also covers interactive demos with smooth Play, validation, and separation of editions.
- Its chapter 1 references are examples, not a mandatory sequence for other courses.
  The skill does not authorize publication, commit, or push without a request.

For chapter 1, run the required final pass `professor/resources/scripts/ordenar_relato.py` after `integrar_mlp.py` and `integrar_regresion.py`.
The current order is: data/features/transformations → classical regression → McCulloch–Pitts → activations/logistic regression/discrimination → composition/ReLU/width → hidden representation/MLP → loss/learning/generalization.
It renumbers 21 blocks and synchronizes transitions and the agenda.
The proposed core takes 90 min. Detailed classical diagnostics (5) and two MLP extensions (6+6) add 17 optional minutes, giving 107 min in total.

These durations replace the previous 105/117 min estimates. `neurona_umbral.html` replaces the main neuron demo with a binary model, veto inhibition, and an explicitly generalized continuous mode.
The original internal identifiers remain unchanged. `sequence_order` indicates the visible order. Before running any builder, preserve manual edits.

Chapter 1 in `professor` is a proposed 16-block, 90-minute class with 15 laboratories and a closing section without another demo.
Each block has black theory and a red narrative script marked `professor-only`.
Its current builder is `professor/resources/scripts/reorganizar_cadencia.py`. It starts from the private snapshot `capitulo_1_30_unidades_academicas.ipynb` and preserves the original embedded demos.
Variants of the same concept are grouped as optional references. Do not go through all variants in class.

It adds `insights_composicion.html` with affine/nonlinear composition, sums of ReLU functions, and parameter/loss space.
The cells are self-contained and reproduce the laboratories without external file dependencies.
The old training runs retain precalculated results and their source in the snapshot.
The narrative starts with sampling and representation, then covers transformations, neuron, activations, XOR, MLP, and learning.
Previous versions remain in `professor/resources/documentacion/versiones/`. Do not run the old builders on this proposal.

Without an explicit request, do not publish it in workshop. Before rebuilding, preserve all subsequent manual edits.

- Make classes practical: brief explanation, student prediction, execution, modification, and comparison of the result.
- Chapter 1 includes the recurring graphical laboratory `mlp_explorer.html` through `integrar_mlp.py`.
  12A replaces the old forward pass. 12B and 12C are optional extensions of 6 minutes each.
  The core remains 90 minutes; both extensions increase it to 102.

  After rebuilding with `reorganizar_cadencia.py`, run `integrar_mlp.py` to retain this extension.
  Before regenerating, preserve subsequent edits.
  The three instances have independent configurations transferable through JSON.
  Do not describe any parameter animation as training.
  Validate calculations with `node professor/resources/scripts/validar_mlp.cjs`.
- Make training feasible on CPU within class time. Use fast mode by default.
- Chapter 1 adds 4R1–4R3 after block 4 through `integrar_regresion.py` and `regresion_lineal.html`.
  They cover the classical model, residuals/MSE/OLS, and assumptions/diagnostics.
  These add approximately 15 minutes: 105 min without MLP extensions, or 117 with them.
  They do not automatically fit within the original 90 minutes.
  If rebuilding, apply it after the MLP integration.

  `validar_regresion.cjs` checks OLS, residual orthogonality, and gradient convergence.
  Play performs real updates. Scenarios keep data fixed during fitting.
- Show calculated values in visual explorers. Do not use illustrations to simulate results.
- Clearly distinguish conceptual illustrations from quantitative results.
- Keep comparable splits, seeds, and budgets in experimental comparisons.
- Do not use the final test to select hyperparameters.
- Except for deliberately generated public elements, do not copy private content from `professor/` to `workshop/`.
