# Agent Evaluation

This directory contains evaluation datasets (evalsets) and criteria for measuring agent quality.

## Structure

```
evaluation/
├── evalsets/          # JSON evalsets with test cases
│   ├── fact_checker_evalset.json
│   ├── devils_advocate_evalset.json
│   └── argument_analyzer_evalset.json
├── criteria/          # Evaluation criteria configs
│   └── fact_checker_criteria.json
├── results/           # Evaluation results (gitignored)
└── run_evaluations.py # Evaluation runner script
```

## Running Evaluations

```bash
python -m evaluation.run_evaluations
```

## Evaluation Criteria

Based on Google ADK's evaluation framework, we use:

- **response_match_score**: Semantic similarity to reference responses
- **rubric_based_final_response_quality_v1**: Custom quality rubrics
- **hallucinations_v1**: Groundedness check

## Creating New Evalsets

Evalsets follow the ADK format:

```json
{
  "eval_set_id": "my_agent_evalset",
  "name": "My Agent Evaluation",
  "description": "Description",
  "eval_cases": [
    {
      "eval_id": "test_001",
      "conversation": [
        {
          "user_content": { "parts": [{"text": "Input"}], "role": "user" },
          "final_response": { "parts": [{"text": "Expected output"}] }
        }
      ]
    }
  ]
}
```

See [ADK Evaluation Docs](https://google.github.io/adk-docs/evaluate/) for more details.
