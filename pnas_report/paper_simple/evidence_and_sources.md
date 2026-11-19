# Evidence and sources

Initial source inventory. The linked paths have been checked. Claims, numerical consistency, and suitability for the new paper require review against the underlying outputs and code.

## Existing project materials

| Material | Location | Use during planning |
| --- | --- | --- |
| Existing question | [question.md](../notes/question.md) | Starting wording and hypothesis history |
| Combined findings notes | [findings.md](../notes/findings.md) | Text findings and limitations, with an outstanding H1 placeholder |
| Age-analysis summary | [Summary](../output/age_shuffle_outsideprem_toprem_summary.md) | Joining rates, permutation comparison, sensitivity analysis, and interpretation |
| Age-analysis results | [Saved results](../output/age_shuffle_outsideprem_toprem_results.json) | Numerical source for H1 |
| Age-analysis implementation | [Python script](../notebooks/age_shuffle_outsideprem_toprem.py) | Eligibility rules, statistic, and permutation procedure |
| Repeated-player sensitivity | [Methodology note](../notes/one_transfer_per_player_sampling_methodology.md) | Meaning and limits of the fixed one-transfer-per-player sample |
| NLP dataset overview | [README](../data/dataset_nlp/README.md) | Data selection, pipeline, and available materials |
| NLP decisions | [decisions.md](../data/dataset_nlp/decisions.md) | Validation, exclusions, and known limitations |
| NLP results | [Results directory](../data/dataset_nlp/results/) | Saved sentiment, coverage, and validation tables |
| NLP analysis code | [Sentiment directory](../data/dataset_nlp/sentiment/) | Implementations behind the text results |
| Degree distributions | [Recap](../output/degree_distribution_recap.md) | Candidate network context |
| Community comparison | [Comparison](../output/transfer_community_comparison/method_comparison.md) | Candidate network evidence and method comparison |
| Feeder routes | [Summary](../output/premier_league_feeder_summary.md) | Candidate recruitment-structure evidence |
| Feeder ownership | [Audit](../notes/premier_league_feeder_ownership_audit.md) | Evidence and qualifications for ownership interpretations |
| Transfer backbone | [Summary](../output/louvain_transfer_backbone_findings/backbone_summary.md) | Candidate evidence about concentrated transfer routes |
| Plotting conventions | [Style guide](../PLOTTING_STYLE.md) | Existing figure presentation choices |
| Text figure generation | [Plotting script](../notebooks/plot_guardian_text_findings.py) | Source tables and figure reproduction |
| Earlier paper | [Draft](../paper/main.tex) and [bibliography](../paper/references.bib) | Context and candidate references for review |
| Existing file guide | [FILE_GUIDE.md](../FILE_GUIDE.md) | Broader inventory whose paths need checking before use |

## Local requirements and template

- [Saved course brief](project_requirements/) provides the project requirements.
- [PNAS template ZIP](template/Template_for_preparing_your_research_report_submission_to_PNAS_using_Overleaf__2025_.zip) provides the requested publication files.

The ZIP contains a sample LaTeX document, sample bibliography and figure, example PDF, PNAS logo, class, styles, and bibliography abbreviation files. The eventual upload will need the paper source, its bibliography and selected figures, plus the template dependencies. The final file manifest will follow the agreed storyline.

## Evidence review to complete together

For each selected claim, record its exact result file, supporting analysis, sample, comparison, validation, limitation, and proposed figure. Check disagreements between notes and outputs against the implementation.

Verify candidate literature and original method references before citing them. Document the availability of inputs needed for reproduction, including any article text or caches held outside the repository.
