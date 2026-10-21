# Hespérides — Deep Learning practice

## Purpose and context

This repository provides Deep Learning class notebooks and voluntary practice material for Hespérides. It separates the student distribution from private teacher preparation. The academic notes and subject assignments belong to [Hespérides](../hesperides/AGENTS.md).

## Key definitions

- **Student edition:** self-contained class material and unsolved exercises.
- **Teacher edition:** the corresponding material with solutions, guidance and narration.
- **Publication:** explicit release of a student edition, not creation of a private proposal.

## Project map

- [workshop](workshop/): versioned student distribution, organized as `clases_sincronas/` and `tareas/`.
- [professor](professor/): unversioned teacher editions and preparation resources.
- `professor/resources/notas/`, `fuentes_d2l/` and `medios/`: notes, source corpus and illustrations.
- [professor/resources/documentacion](professor/resources/documentacion/): class provenance, designs and historical versions.
- `professor/resources/scripts/`: builders and validators; `cache_datos/`: private dataset cache.
- [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock): notebook environment.

## Planning and stakeholders

[Planning panel](https://github.com/users/aprendesc/projects/6)

- `aprendesc`: lecturer, author and repository maintainer.
- Paola Serracchiani: academic coordination and operational support.
- Students: users of the teaching materials.

## Methodologies and references

[`development-methodology`](/Users/alejandroprendes/.codex/skills/development-methodology/SKILL.md).
Use the local [sync_lesson_generator](professor/resources/skills/sync_lesson_generator/SKILL.md) for teaching format, visual models, teacher scripts and validation.

Keep solutions and teacher guidance out of student editions. Preserve manual notebook edits during regeneration. Class duration, chapter order and publication status belong to each class record; historical builder versions do not define a universal class sequence.
