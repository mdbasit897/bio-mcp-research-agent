"""
Bio MCP Research Agent - Kaggle Benchmark Task
Evaluates AI model capabilities in biomedical literature review and research gap analysis.

This task tests the model's ability to:
1. Formulate effective search strategies for biomedical databases
2. Critically analyze research methodologies
3. Identify limitations and research gaps
4. Propose actionable future research directions
"""

import json
from typing import Dict, Any, List


def get_task_prompt() -> str:
    """Return the prompt that will be sent to models for evaluation."""
    return """
Act as an expert biomedical AI researcher conducting a systematic literature review on non-invasive glucose monitoring.

CONTEXT:
Non-invasive glucose monitoring using photoplethysmography (PPG) and machine learning is an active area of research. 
Despite decades of work, no commercially viable solution exists due to various technical and methodological challenges.

YOUR TASK:

1. SEARCH STRATEGY (25 points)
   Describe your search strategy for finding relevant literature. Include:
   - Specific search terms and Boolean operators you would use
   - Databases you would search (PubMed, IEEE Xplore, etc.)
   - Inclusion/exclusion criteria (year range, study types, etc.)

2. METHODOLOGICAL ANALYSIS (25 points)
   Based on your knowledge of the field, identify and describe:
   - At least 3 different ML approaches used in PPG-based glucose estimation
   - The key features extracted from PPG signals
   - Common preprocessing techniques

3. CRITICAL LIMITATIONS (25 points)
   Analyze and explain at least 4 major limitations in current research:
   - Technical challenges (signal quality, calibration, etc.)
   - Methodological issues (study design, validation, etc.)
   - Clinical barriers (regulatory, adoption, etc.)

4. FUTURE DIRECTIONS (25 points)
   Propose 2-3 specific, actionable research directions that could advance the field.
   For each direction, explain:
   - What problem it addresses
   - Why it's promising
   - How it could be implemented

FORMAT REQUIREMENTS:
Structure your response as a markdown report with these exact section headers:
- ## Search Strategy
- ## Methodological Approaches  
- ## Critical Limitations
- ## Future Research Directions

EVALUATION CRITERIA:
- Specificity and depth of analysis (not generic statements)
- Technical accuracy and understanding of the domain
- Clear identification of concrete research gaps
- Actionable and well-justified future directions
- Proper structure and organization

Be thorough and demonstrate deep understanding of both the technical and clinical aspects.
"""


def evaluate_model(response: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Evaluate the model's response against defined criteria.
    
    Args:
        response: The model's generated response (string)
        context: Optional additional context about the task execution
    
    Returns:
        dict: Evaluation results with scores and detailed metrics
    """
    if not response or not isinstance(response, str):
        return {
            "score": 0,
            "max_score": 100,
            "normalized_score": 0.0,
            "metrics": {
                "search_strategy": 0,
                "methodological_analysis": 0,
                "critical_limitations": 0,
                "future_directions": 0
            },
            "feedback": "No valid response provided"
        }
    
    score = 0
    max_score = 100
    metrics = {}
    feedback_items = []
    
    # Normalize response for easier checking
    response_lower = response.lower()
    
    # === CRITERION 1: Search Strategy (25 points) ===
    search_score = 0
    
    # Check for required section
    if "## search strategy" in response_lower or "# search strategy" in response_lower:
        search_score += 5
        feedback_items.append("✓ Has Search Strategy section")
    
    # Check for database mentions
    databases = ["pubmed", "ieee", "scopus", "web of science", "google scholar"]
    db_count = sum(1 for db in databases if db in response_lower)
    if db_count >= 1:
        search_score += min(10, db_count * 3)
        feedback_items.append(f"✓ Mentions {db_count} database(s)")
    
    # Check for search terms/Boolean operators
    boolean_terms = ["AND", "OR", "NOT", "\"", "boolean", "search term"]
    if any(term.lower() in response_lower for term in boolean_terms):
        search_score += 5
        feedback_items.append("✓ Describes search terms/operators")
    
    # Check for inclusion/exclusion criteria
    criteria_terms = ["inclusion", "exclusion", "criteria", "year", "202", "review article"]
    if any(term in response_lower for term in criteria_terms):
        search_score += 5
        feedback_items.append("✓ Specifies inclusion/exclusion criteria")
    
    metrics["search_strategy"] = min(25, search_score)
    score += metrics["search_strategy"]
    
    # === CRITERION 2: Methodological Analysis (25 points) ===
    method_score = 0
    
    # Check for required section
    if "## methodological" in response_lower or "# methodological" in response_lower or \
       "## methodological approaches" in response_lower or "approaches" in response_lower:
        method_score += 5
        feedback_items.append("✓ Has Methodological Analysis section")
    
    # Check for ML approach mentions
    ml_approaches = [
        "regression", "svm", "random forest", "neural network", "deep learning",
        "cnn", "rnn", "lstm", "ensemble", "xgboost", "gradient boosting",
        "plsr", "partial least squares", "support vector"
    ]
    ml_count = sum(1 for ml in ml_approaches if ml in response_lower)
    if ml_count >= 1:
        method_score += min(10, ml_count * 3)
        feedback_items.append(f"✓ Identifies {ml_count} ML approach(es)")
    
    # Check for feature extraction mentions
    features = ["feature", "ppg", "peak", "valley", "morphological", "time-domain", "frequency"]
    if any(feat in response_lower for feat in features):
        method_score += 5
        feedback_items.append("✓ Discusses feature extraction")
    
    # Check for preprocessing mentions
    preprocessing = ["preprocess", "filter", "normaliz", "artifact", "noise", "baseline"]
    if any(pp in response_lower for pp in preprocessing):
        method_score += 5
        feedback_items.append("✓ Mentions preprocessing techniques")
    
    metrics["methodological_analysis"] = min(25, method_score)
    score += metrics["methodological_analysis"]
    
    # === CRITERION 3: Critical Limitations (25 points) ===
    limit_score = 0
    
    # Check for required section
    if "## critical limitation" in response_lower or "# critical limitation" in response_lower or \
       "## limitations" in response_lower or "limitation" in response_lower:
        limit_score += 5
        feedback_items.append("✓ Has Critical Limitations section")
    
    # Count distinct limitations mentioned
    limitation_types = [
        "calibration", "accuracy", "error", "motion artifact", "skin", 
        "temperature", "humidity", "individual", "population", "dataset",
        "sample size", "validation", "clinical trial", "regulatory", "fda"
    ]
    limit_count = sum(1 for lim in limitation_types if lim in response_lower)
    if limit_count >= 4:
        limit_score += 15
        feedback_items.append(f"✓ Identifies {limit_count} limitation types")
    elif limit_count >= 2:
        limit_score += 10
        feedback_items.append(f"✓ Identifies {limit_count} limitation types")
    elif limit_count >= 1:
        limit_score += 5
        feedback_items.append(f"✓ Identifies {limit_count} limitation type(s)")
    
    # Check for depth of analysis
    if any(word in response_lower for word in ["because", "due to", "caused by", "results in"]):
        limit_score += 5
        feedback_items.append("✓ Provides causal explanations for limitations")
    
    metrics["critical_limitations"] = min(25, limit_score)
    score += metrics["critical_limitations"]
    
    # === CRITERION 4: Future Directions (25 points) ===
    future_score = 0
    
    # Check for required section
    if "## future" in response_lower or "# future" in response_lower or \
       "## future research" in response_lower or "future direction" in response_lower:
        future_score += 5
        feedback_items.append("✓ Has Future Directions section")
    
    # Check for specific proposals
    future_indicators = [
        "propose", "suggest", "recommend", "should", "could", "would",
        "first", "second", "third", "one", "another", "additionally"
    ]
    if any(ind in response_lower for ind in future_indicators):
        future_score += 5
        feedback_items.append("✓ Makes specific proposals")
    
    # Check for justification
    justification_terms = ["because", "therefore", "thus", "hence", "important", "necessary", "promising"]
    if any(just in response_lower for just in justification_terms):
        future_score += 5
        feedback_items.append("✓ Justifies proposed directions")
    
    # Check for implementation details
    impl_terms = ["implement", "approach", "method", "technique", "framework", "system", "algorithm"]
    if any(impl in response_lower for impl in impl_terms):
        future_score += 5
        feedback_items.append("✓ Discusses implementation approach")
    
    # Check for multiple directions
    if response_lower.count("direction") >= 2 or response_lower.count("approach") >= 2:
        future_score += 5
        feedback_items.append("✓ Proposes multiple research directions")
    
    metrics["future_directions"] = min(25, future_score)
    score += metrics["future_directions"]
    
    # === Additional Quality Checks ===
    bonus_feedback = []
    
    # Check response length (adequate depth)
    word_count = len(response.split())
    if word_count >= 400:
        bonus_feedback.append(f"✓ Comprehensive response ({word_count} words)")
    elif word_count >= 200:
        bonus_feedback.append(f"✓ Adequate response length ({word_count} words)")
    else:
        bonus_feedback.append(f"⚠ Short response ({word_count} words), may lack depth")
    
    # Check for structured formatting
    if response.count("##") >= 3 or response.count("#") >= 3:
        bonus_feedback.append("✓ Well-structured with markdown headers")
    
    # Compile final feedback
    all_feedback = "\n".join(feedback_items + bonus_feedback)
    
    return {
        "score": score,
        "max_score": max_score,
        "normalized_score": round(score / max_score * 100, 2),
        "metrics": metrics,
        "word_count": word_count,
        "feedback": all_feedback,
        "evaluation_summary": {
            "excellent": score >= 80,
            "good": 60 <= score < 80,
            "adequate": 40 <= score < 60,
            "needs_improvement": score < 40
        }
    }


def run_evaluation(model_response: str) -> Dict[str, Any]:
    """
    Main entry point for running the evaluation.
    
    Args:
        model_response: The response from the AI model being evaluated
    
    Returns:
        dict: Complete evaluation results
    """
    result = evaluate_model(model_response)
    
    # Add metadata
    result["task_name"] = "bio-mcp-research-agent"
    result["task_version"] = "1.0.0"
    result["evaluation_type"] = "biomedical_literature_review"
    
    return result


if __name__ == "__main__":
    # Demo mode: Show the task prompt and test evaluation
    print("=" * 70)
    print("BIO MCP RESEARCH AGENT - KAGGLE BENCHMARK TASK")
    print("=" * 70)
    print("\n📋 TASK PROMPT:\n")
    print(get_task_prompt())
    
    print("\n" + "=" * 70)
    print("SAMPLE EVALUATION TEST")
    print("=" * 70)
    
    # Test with a sample response
    sample_response = """
## Search Strategy

I would search PubMed and IEEE Xplore using terms like "non-invasive glucose monitoring" AND "PPG" AND "machine learning" with filters for 2020-2024.

## Methodological Approaches

Common approaches include regression models, neural networks, and SVM. Features extracted from PPG include peak-to-peak intervals and morphological features.

## Critical Limitations

Key limitations include calibration drift, motion artifacts, and individual variability. These are caused by physiological differences and environmental factors.

## Future Research Directions

I propose developing adaptive calibration methods because this would address individual variability. Another direction is multi-modal sensing.
"""
    
    print("\n🧪 Testing with sample response...")
    result = run_evaluation(sample_response)
    
    print(f"\n📊 EVALUATION RESULTS:")
    print(f"   Score: {result['score']}/{result['max_score']} ({result['normalized_score']}%)")
    print(f"   Word Count: {result.get('word_count', 'N/A')}")
    print(f"\n📈 Metrics Breakdown:")
    for metric, score in result['metrics'].items():
        print(f"   - {metric.replace('_', ' ').title()}: {score}/25")
    print(f"\n💡 Feedback:\n{result['feedback']}")
    print("\n" + "=" * 70)
