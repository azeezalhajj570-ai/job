# Documentation Gap Report

## Gaps resolved in this submission pass

- The repository lacked a single submission-ready report path. The final editable report is now generated at `submission/Project_Report.docx`.
- UML images existed, but no editable source files were stored beside them. Mermaid source files are now provided under `docs/diagrams/sources/`.
- The documentation did not clearly separate verified implementation from future work. The new report and README use code-backed statements and isolate limitations explicitly.
- There was no repository-level checklist for final delivery. A submission checklist is now included.
- There was no reproducible screenshot workflow. A Playwright-based capture script is now added.

## Remaining documentation and implementation gaps

- The academic template includes questionnaire-oriented wording in Chapter 3, but the repository does not implement a questionnaire subsystem. The report now states this directly and maps the section to the actual CSV dataset workflow.
- The bundled datasets are very small. Any claim of real-world model performance would be overstated, so the report treats the current metrics as demonstration results only.
- The repository contains no research-paper bibliography manager, no citation database, and no literature review sources. Chapter 2 therefore remains a high-level contextual discussion rather than a source-heavy survey.
- The UI currently shows the dashboard navigation entry even to non-admin users, although route protection still blocks access. This is a UX gap rather than a security gap.
- There is no deployment automation, CI pipeline, or environment lockfile beyond `requirements.txt`.
- There is no live ingestion from recruitment platforms or external APIs.
- The system analyzes English text only and does not inspect images, links, attachments, or recruiter reputation signals.

## Risks for final academic submission

- If the professor expects a full references section with external citations, that content still needs faculty-approved sources.
- Student names, IDs, supervisor name, and committee signature lines should be checked before submission because the repository does not authoritatively store all academic metadata.
- Screenshots are environment-dependent and should be regenerated if the UI changes after this pass.
