---
name: sync_lesson_generator
description: Generate or refine interactive synchronous-class notebooks across chapters and subjects, matching the project's academic student theory, natural spoken teacher notes, manipulable demonstrations and private/public structure. Use for lesson authoring, not ordinary notebook analysis.
---

# Context

Reproduce the teaching quality developed in this project, not its particular Deep Learning examples. Deliver one self-contained notebook per class, with a private teacher edition and an equivalent student edition when publication is requested. The established language is Spanish and the session length is 90 minutes; adapt these to the requested course. The exact skill name, including underscores, was requested by the user.

# Rules

## Grounding and narrative

- **Use the course sources.** Read the relevant notes, including LaTeX when available, and existing notebooks. Extract concepts, prerequisites, current coverage and missing insights before adding material. Identify unavailable sources rather than claiming to have read them.
- **Preserve what works.** Retain valuable existing cells and demos. Before running a builder, inspect its scope and preserve manual additions. A revision is not permission to reconstruct unrelated material.
- **Plan distinct insights.** For each block identify its central claim, prerequisite, representation, manipulation, expected observation and teaching time. Order blocks so each prepares the next question. Give each explanation cell a distinct purpose and group variants of the same concept within one explorer.
- **Match the audience.** Teach substantive concepts at the level of the notes, not incidental programming operations or repeated prerequisite drills. The earlier request for thirty cells expressed a need for substance, not a permanent minimum cell count.
- **Preserve cadence.** Budget explanation, student prediction, execution, manipulation and discussion within the requested duration. Give extensions separate timings. Make it possible to skip them without breaking the narrative. Do not silently stretch a 90-minute core.
- **Revisit with purpose.** A complex graphical object may recur across cells when each studies a different question, as with MLP forward propagation, parameter intervention and architecture. Cosmetic variations of a vector, rotation or point cloud do not constitute new insights.

> **Authoring sequence**
>
> Extract -> Sequence -> Author -> Validate -> Publish when requested

In Extract, inventory source concepts and existing coverage. In Sequence, choose distinct insights and their dependency order. In Author, develop theory, speech and demos together. In Validate, check calculations and classroom behavior. In Publish when requested, derive the student edition by filtering private content.

## Structure and spoken voice

- **One notebook per class.** Place `capitulo_N.ipynb` directly in `clases_sincronas/`, with an agenda, ordered blocks and synthesis. A block normally combines public theory, private teacher guidance and a demo; a conclusion need not introduce another visualization.
- **Student prose is theory.** Explain definitions, assumptions, equations and implications with academic precision and sufficient detail. Highlight key questions or insights selectively. Avoid slogans, infantilizing phrasing, excessive synthesis and repeated explanations. In this project's Deep Learning material use “features” rather than “vector de características”.
- **One teacher bullet per topic.** Start with a short bold explanation that communicates the idea, not a one-word topic title. Follow it with a colon and a paragraph that can be spoken literally. Include the explanation and answer needed if the lecturer loses their train of thought. Do not use instructions such as “explicar la matriz”.
- **Use natural classroom speech.** Prefer first-person plural expressions such as “nos fijamos”, “si movemos” and “aquí vemos”, connected to what the demo actually shows. Use longer linked sentences with relatively few full stops while retaining clarity. Avoid clipped declarations, theatrical filler and repeated stock openings. Do not mechanically give every paragraph the same syntax.
- **Make the bold text a memory cue.** Example: `<strong>Los parámetros cambian la regla para todos los ejemplos</strong>: Si tocamos este coeficiente vemos que se mueven muchos puntos a la vez porque no estamos colocando cada observación por separado sino cambiando una regla que aplicamos a todas, y esa idea de compartir parámetros es la que vamos a mantener cuando construyamos una capa.` Adapt the voice and claim to each topic.
- **Connect without recapping.** Transitions should lead from the unresolved question to the next concept, not repeat the previous explanation. Distinguish optional-route instructions from words intended to be spoken to students.
- **Separate privacy structurally.** Public theory is black on white. Teacher guidance and solutions are red on white with the existing `#b91c1c` treatment. Put them in separate Markdown cells tagged `professor-only`. Spoken guides also use `teacher-guide`. Preserve stable block identifiers and visible order metadata. Color alone is not a privacy marker.

## Visual interaction

- **Match the representation to the insight.** Link tables and points for observations, geometry for transformations, diagrams and numerical matrices for calculations, residual plots for diagnostics and surfaces for quantities where their dimensions help. Use 3D when it adds information. Transfer these principles across subjects rather than importing spirals, XOR or neurons indiscriminately.
- **Make controls central.** Use visible sliders, buttons and selectors for meaningful quantities without requiring code edits. Show current values, equations and consequences together. Linked views must represent the same state and calculation.
- **Provide a prepared Play demo.** Every interactive graph needs a preloaded route that demonstrates its intended insight. Also provide manual controls and pause/reset or equivalent actions. Check that the graph itself updates, not only the slider or label.
- **Animate continuous quantities smoothly.** Interpolate parameters and update linked values and visuals rather than jumping between endpoints. Keep discrete events discrete when appropriate, including binary inputs and sampling. Label crossfades of precalculated states as playback; intermediate images are not necessarily evaluated models.
- **Compute the displayed results.** Weights, activations, predictions, losses and other quantitative values must follow the represented calculation. Distinguish conceptual illustrations from results, parameter exploration from optimization and historical models from their generalizations.
- **Keep comparisons interpretable.** Preserve data, seeds, partitions and budgets when comparing models. Keep data fixed during fitting unless resampling is the topic. Explain whether explorer instances share state. Do not use test data for model selection.
- **Support classroom execution.** Reuse embedded browser-side HTML/JavaScript when appropriate for responsive controls without kernel round trips. Keep authoring assets private and embed required code and images in the final notebook. CPU execution must be viable. Use fast mode by default and store downloaded datasets in the user cache.

## Validation and delivery

- **Check execution and UI separately.** Validate notebook format and execute affected notebooks from their final location in the project environment. For text-only edits verify public cells, code and outputs are unchanged. Python execution alone does not establish that JavaScript works.
- **Exercise the controls.** In a browser check a meaningful slider change, Play progression, pause/reset and linked display agreement. Test representative numerical results and relevant edge cases. Report checks that could not be performed rather than claiming them.
- **Review the actual lesson.** Check prerequisite order, total time, distinct insights, visual variety, academic student prose and speakable teacher paragraphs. Verify that interpolation, playback and training are described accurately.
- **Publish by subtraction only when requested.** Keep public cells and demos identical while removing private teacher cells, metadata and assets. Inspect saved outputs and tags for private content leaks. Do not edit the same public content independently in both editions.
- **Respect the project surfaces.** `workshop/` contains only `clases_sincronas/` and `tareas/`; `professor/` mirrors these and adds `resources/`. Unreleased chapters remain private. Creating or refining a class does not authorize publication, commit or push.

## Local reference implementation

- **Inspect the living example.** Use `professor/clases_sincronas/capitulo_1.ipynb` for format and `professor/resources/scripts/guion_oral.py` for the current conversational voice. Check actual files rather than assuming they have not changed.
- **Find sources and components.** Notes live in `professor/resources/notas/` and relevant D2L sources in `professor/resources/fuentes_d2l/`. Within `professor/resources/scripts/`, `laboratorio_realidad.html`, `insights_composicion.html`, `neurona_umbral.html`, `regresion_lineal.html` and `mlp_explorer.html` demonstrate complementary interaction patterns. Associated `validar_*.cjs` scripts check their calculations.
- **Treat chapter details as examples.** Chapter 1 currently has 21 blocks, a 90-minute core and 17 optional minutes. Its order is data/features/transformations -> regression -> McCulloch–Pitts -> activations/logistic discrimination -> XOR/composition/ReLU/width -> hidden representation/MLP -> loss/learning/generalization. This order is not a template for unrelated subjects.
- **Preserve construction boundaries.** The chapter-specific sequence is `reorganizar_cadencia.py`, `integrar_mlp.py`, `integrar_regresion.py`, then `ordenar_relato.py`, whose last pass applies `guion_oral`. Inspect and back up before using builders; do not run them to create another chapter. `publicar_capitulo_1.py` illustrates authorized publication and `professor/resources/documentacion/versiones/` holds historical snapshots.
