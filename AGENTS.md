# Hespérides — Deep Learning practice

## Purpose and context

This repository provides Deep Learning class notebooks and voluntary practice material for Hespérides. It separates the student distribution from private teacher preparation. The academic notes and subject assignments belong to [Hespérides](/Users/alejandroprendes/Desktop/projects/hesperides/AGENTS.md).

## Key definitions

- **Student edition:** self-contained class material and unsolved exercises.
- **Teacher edition:** the corresponding material with solutions, guidance and narration.
- **Publication:** explicit release of a student edition, not creation of a private proposal.

## Repository map

- [practicas](practicas/): versioned student distribution, organized as `clases_sincronas/` and `tareas/`.
- [profesor](profesor/): unversioned teacher editions and preparation resources.
- `profesor/resources/notas/`, `fuentes_d2l/` and `medios/`: notes, source corpus and illustrations.
- [profesor/resources/documentacion](profesor/resources/documentacion/): class provenance, designs and historical versions.
- `profesor/resources/scripts/`: builders and validators; `cache_datos/`: private dataset cache.
- [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock): notebook environment.

## Planning and stakeholders

[Planning panel](https://github.com/users/aprendesc/projects/6)

- `aprendesc`: lecturer, author and repository maintainer.
- Paola Serracchiani: academic coordination and operational support.
- Students: users of the teaching materials.

## Methodologies and references

Choose contracts by the issue's main purpose, not by supporting scripts. Use [coding-contract-guidelines](/Users/alejandroprendes/.codex/skills/coding-contract-guidelines/SKILL.md) for software implementation, [documental-contract-guidelines](/Users/alejandroprendes/.codex/skills/documental-contract-guidelines/SKILL.md) for authored documents, and [general-contract-guidelines](/Users/alejandroprendes/.codex/skills/general-contract-guidelines/SKILL.md) for organization, administration and class preparation, recording, delivery or review without a principal manuscript. Each contract lives in `context/issues/<issue>/`; documentary prose and figures belong inside that issue. Preserve requirements, decisions, pauses and historical evidence. Real supporting validators may stay beside any task without turning it into a software feature. Global functional scenarios remain in `context/tests/`.

[`development-methodology`](/Users/alejandroprendes/.codex/skills/development-methodology/SKILL.md).
Use the local [sync_lesson_generator](profesor/resources/skills/sync_lesson_generator/SKILL.md) for teaching format, visual models, teacher scripts and validation.

Keep solutions and teacher guidance out of student editions. Preserve manual notebook edits during regeneration. Class duration, chapter order and publication status belong to each class record; historical builder versions do not define a universal class sequence.

Local clone safeguards and configuration: [.githooks/CLONE.md](.githooks/CLONE.md).
