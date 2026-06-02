
Act as an expert biomedical AI researcher specializing in non-invasive glucose monitoring.

Execute the following systematic review pipeline:
1. **Search**: Use `search_pubmed` to find papers from 2020-2024 matching: `("Blood Glucose"[Mesh] OR "non-invasive glucose") AND ("machine learning" OR "deep learning") AND ("PPG" OR "near-infrared")`. Limit to 10 results.
2. **Extract**: Use `fetch_pubmed_abstracts` to get the full abstracts of the returned PMIDs.
3. **Analyze**: Identify the sensor modality, ML model, reported MARD (Mean Absolute Relative Difference), and stated limitations (e.g., motion artifacts, hydration effects, inter-subject variability) for each paper.
4. **Persist**: Use the `filesystem` tool to write this analysis into a structured Markdown table saved as `research_outputs/literature_matrix.md`.
5. **Synthesize**: Based on the saved matrix, write a 300-word "Problem Statement" for a PhD proposal highlighting the top 2 unresolved methodological gaps.
