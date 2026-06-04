"""
Test data fixtures and mock data for biomedical research agent tests
"""
import pytest
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid


class MockPubMedResponse:
    """Mock PubMed API response data"""
    
    @staticmethod
    def search_response(count: int = 5) -> Dict[str, Any]:
        """Generate mock PubMed search results"""
        papers = []
        for i in range(count):
            papers.append({
                "pubmed_id": f"{i+1:07d}",
                "title": f"Non-invasive glucose monitoring using machine learning: Paper {i+1}",
                "authors": [f"Author {j+1}" for j in range(3)],
                "journal": "Journal of Biomedical Informatics",
                "publication_date": (datetime.now() - timedelta(days=365*i)).strftime("%Y-%m-%d"),
                "doi": f"10.1000/paper{i+1}",
                "abstract": f"This paper presents a novel approach to non-invasive glucose monitoring using machine learning techniques. We demonstrate accuracy improvements over traditional methods.",
                "keywords": ["glucose monitoring", "machine learning", "non-invasive", "PPG"],
                "cited_by_count": 45 + i * 10,
                "is_open_access": i % 2 == 0
            })
        
        return {
            "count": count,
            "papers": papers
        }

    @staticmethod
    def abstract_response(pmids: List[str]) -> Dict[str, Any]:
        """Generate mock PubMed abstract response"""
        abstracts = []
        for pmid in pmids:
            abstracts.append({
                "pubmed_id": pmid,
                "title": f"Research Paper {pmid}",
                "abstract": f"Comprehensive abstract for paper {pmid}. This research investigates novel methodologies for biomedical data analysis and machine learning applications in healthcare.",
                "methods": "We employed deep learning models trained on multi-modal datasets including photoplethysmography signals and demographic data.",
                "results": "Our model achieved 95.2% accuracy in glucose prediction with a mean absolute deviation of 8.7 mg/dL.",
                "conclusions": "The proposed method shows significant promise for clinical deployment in non-invasive glucose monitoring systems.",
                "limitations": "Limited sample size and need for validation in diverse populations.",
                "future_work": "Further validation studies and integration with existing clinical systems.",
                "mard_score": 8.7 + (int(pmid) % 3) * 0.5,  # Simulated MARD scores
                "sensitivity": 0.92 + (int(pmid) % 5) * 0.01,
                "specificity": 0.94 + (int(pmid) % 4) * 0.01
            })
        
        return {
            "count": len(abstracts),
            "abstracts": abstracts
        }


class MockSemanticScholarResponse:
    """Mock Semantic Scholar API response data"""
    
    @staticmethod
    def search_response(query: str, count: int = 5) -> Dict[str, Any]:
        """Generate mock Semantic Scholar search results"""
        papers = []
        for i in range(count):
            papers.append({
                "paper_id": f"semantic_scholar_{uuid.uuid4()}",
                "title": f"AI-powered {query} research: Paper {i+1}",
                "authors": [
                    {
                        "name": f"Author {j+1}",
                        "authorId": f"author_{j+1}"
                    } for j in range(3)
                ],
                "year": 2024 - i,
                "citationCount": 150 + i * 25,
                "influentialCitationCount": 75 + i * 12,
                "openAccessPdf": {
                    "url": f"https://arxiv.org/pdf/{i+1:04d}.1234.pdf"
                } if i % 2 == 0 else None,
                "venue": f"Conference on {query} Research",
                "journal": f"Journal of {query} Applications",
                "abstract": f"Advanced research in {query} using artificial intelligence and machine learning methodologies.",
                "fieldsOfStudy": ["Computer Science", "Medicine", "Biology"],
                "publicationTypes": ["Journal Article", "Conference Paper"],
                "externalIds": {
                    "PubMed": f"{i+1:07d}",
                    "ArXiv": f"{i+1:04d}.1234"
                },
                "s2FieldsOfStudy": [
                    {"field": "Computer Science", "score": 0.8},
                    {"field": "Medicine", "score": 0.15},
                    {"field": "Biology", "score": 0.05}
                ]
            })
        
        return {
            "total": count,
            "papers": papers
        }


class MockFileSystemResponse:
    """Mock Filesystem operations for testing"""
    
    @staticmethod
    def research_output_template() -> Dict[str, Any]:
        """Generate mock research output template"""
        return {
            "metadata": {
                "study_title": "Non-invasive Glucose Monitoring Research Analysis",
                "date_generated": datetime.now().isoformat(),
                "total_papers_analyzed": 0,
                "search_terms": [],
                "time_range": "2020-2024"
            },
            "summary": {
                "key_findings": [],
                "methodological_approaches": [],
                "performance_metrics": {},
                "limitations": [],
                "future_directions": []
            },
            "detailed_analysis": {
                "papers_by_year": {},
                "technologies_used": {},
                "accuracy_trends": [],
                "comparison_table": []
            },
            "recommendations": {
                "phd_proposal_gaps": [],
                "clinical_applications": [],
                "technical_improvements": []
            }
        }

    @staticmethod
    def comparison_table_data() -> List[Dict[str, Any]]:
        """Generate mock comparison table data"""
        return [
            {
                "paper_id": "123456",
                "title": "Deep Learning for PPG-based Glucose Monitoring",
                "year": 2024,
                "method": "CNN + LSTM",
                "dataset_size": "1,200 patients",
                "accuracy": "95.2%",
                "mard": "8.7 mg/dL",
                "sensitivity": "92.3%",
                "specificity": "94.1%",
                "limitations": ["Small cohort", "Single ethnicity"],
                "clinical_validation": "Prospective study"
            },
            {
                "paper_id": "789012",
                "title": "Multi-modal Sensor Fusion for Glucose Prediction",
                "year": 2023,
                "method": "Transformer + Ensemble",
                "dataset_size": "850 patients",
                "accuracy": "93.8%",
                "mard": "9.2 mg/dL",
                "sensitivity": "91.1%",
                "specificity": "95.3%",
                "limitations": ["Limited device variety", "Short follow-up"],
                "clinical_validation": "Retrospective analysis"
            }
        ]


class TestPrompts:
    """Test prompt templates and examples"""
    
    @staticmethod
    def glucose_monitoring_research_prompt() -> str:
        """Example glucose monitoring research prompt"""
        return """
        Act as an expert biomedical AI researcher specializing in non-invasive glucose monitoring.
        
        Execute the following systematic review:
        1. Use `search_pubmed` to find 10 recent papers (2020-2024) on "non-invasive glucose monitoring PPG machine learning"
        2. Fetch their abstracts using `fetch_pubmed_abstracts`
        3. Use the `filesystem` tool to save a comprehensive analysis to `research_outputs/glucose_monitoring_analysis.md` including:
           - MARD scores and accuracy metrics
           - Methodological approaches used
           - Dataset sizes and demographics
           - Key limitations identified
           - Clinical validation status
        4. Generate a 500-word executive summary highlighting the top 3 breakthroughs and 2 major challenges
        5. Identify the most promising approach for PhD research and explain why
        """

    @staticmethod
    def oncology_ai_research_prompt() -> str:
        """Example oncology AI research prompt"""
        return """
        Act as an expert oncology AI researcher.
        
        Conduct a comprehensive analysis of AI in cancer diagnosis:
        1. Use `search_pubmed` to find 8 papers (2020-2024) on "deep learning cancer diagnosis radiomics"
        2. Use `search_semantic_scholar` to find 5 papers on "AI cancer prognosis biomarkers"
        3. Fetch abstracts from both sources
        4. Use the `filesystem` tool to create a comparative analysis in `research_outputs/cancer_ai_comparison.md`
        5. Generate insights on current trends, gaps, and future directions
        """

    @staticmethod
    def cardiovascular_ai_prompt() -> str:
        """Example cardiovascular AI research prompt"""
        return """
        Act as an expert cardiovascular AI researcher.
        
        Analyze AI applications in cardiovascular medicine:
        1. Use `search_pubmed` to find 6 papers on "ECG arrhythmia detection deep learning"
        2. Use `search_semantic_scholar` to find 4 papers on "AI cardiovascular imaging"
        3. Compare methodologies and performance metrics
        4. Save structured analysis to `research_outputs/cardiovascular_ai_summary.md`
        5. Provide recommendations for clinical implementation
        """


class PerformanceTestData:
    """Performance test data and scenarios"""
    
    @staticmethod
    def large_dataset_scenarios() -> List[Dict[str, Any]]:
        """Test scenarios with large datasets"""
        return [
            {
                "name": "Large PubMed Search",
                "query": "machine learning biomedical applications",
                "limit": 100,
                "expected_time_seconds": 30
            },
            {
                "name": "Multi-source Search",
                "query": "artificial intelligence healthcare",
                "pubmed_limit": 50,
                "semantic_limit": 30,
                "expected_time_seconds": 45
            },
            {
                "name": "Complex Analysis Task",
                "query": "non-invasive glucose monitoring",
                "analysis_depth": "comprehensive",
                "expected_time_seconds": 60
            }
        ]

    @staticmethod
    def stress_test_scenarios() -> List[Dict[str, Any]]:
        """Stress test scenarios"""
        return [
            {
                "name": "High Frequency Requests",
                "requests_per_minute": 60,
                "duration_minutes": 5,
                "concurrent_users": 10
            },
            {
                "name": "Large Result Processing",
                "result_size_mb": 100,
                "concurrent_processing": 5,
                "timeout_seconds": 120
            }
        ]


class SecurityTestData:
    """Security test data and attack vectors"""
    
    @staticmethod
    def malicious_inputs() -> List[str]:
        """List of potentially malicious inputs for security testing"""
        return [
            # SQL Injection attempts
            "SELECT * FROM papers; DROP TABLE users;",
            "1' OR '1'='1",
            "'; DROP TABLE papers; --",
            
            # XSS attempts
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            
            # Command injection
            "glucose monitoring; rm -rf /",
            "diabetes research && cat /etc/passwd",
            
            # Path traversal
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\drivers\\etc\\hosts",
            
            # Buffer overflow attempts
            "A" * 10000,
            "glucose" + "A" * 5000,
            
            # API abuse
            "diabetes" * 1000,
            "glucose monitoring" + " " * 1000
        ]

    @staticmethod
    def valid_inputs() -> List[str]:
        """List of valid inputs for testing"""
        return [
            "non-invasive glucose monitoring",
            "machine learning cancer diagnosis",
            "AI cardiovascular imaging",
            "deep learning biomedical applications",
            "artificial intelligence healthcare"
        ]


@pytest.fixture
def mock_pubmed_response():
    """Fixture providing mock PubMed response data"""
    return MockPubMedResponse.search_response(5)


@pytest.fixture
def mock_semantic_scholar_response():
    """Fixture providing mock Semantic Scholar response data"""
    return MockSemanticScholarResponse.search_response("machine learning", 5)


@pytest.fixture
def mock_research_output():
    """Fixture providing mock research output template"""
    return MockFileSystemResponse.research_output_template()


@pytest.fixture
def test_prompts():
    """Fixture providing test prompt templates"""
    return TestPrompts()


@pytest.fixture
def performance_scenarios():
    """Fixture providing performance test scenarios"""
    return PerformanceTestData.large_dataset_scenarios()


@pytest.fixture
def security_test_data():
    """Fixture providing security test data"""
    return {
        "malicious": SecurityTestData.malicious_inputs(),
        "valid": SecurityTestData.valid_inputs()
    }


@pytest.fixture
def temp_research_outputs():
    """Fixture for temporary research output directory"""
    temp_dir = "temp_test_outputs"
    os.makedirs(temp_dir, exist_ok=True)
    yield temp_dir
    # Cleanup
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_pmid_list():
    """Fixture providing sample PMIDs for testing"""
    return ["1234567", "2345678", "3456789", "4567890", "5678901"]


@pytest.fixture
def sample_search_queries():
    """Fixture providing sample search queries"""
    return [
        "non-invasive glucose monitoring PPG machine learning",
        "deep learning cancer diagnosis radiomics",
        "AI cardiovascular imaging ECG arrhythmia",
        "artificial intelligence healthcare applications"
    ]


# Test data directory setup
@pytest.fixture(scope="session")
def test_data_dir():
    """Create and manage test data directory"""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Create sample data files
    pubmed_data = MockPubMedResponse.search_response(10)
    with open(os.path.join(data_dir, "mock_pubmed.json"), "w") as f:
        json.dump(pubmed_data, f, indent=2)
    
    semantic_data = MockSemanticScholarResponse.search_response("machine learning", 8)
    with open(os.path.join(data_dir, "mock_semantic_scholar.json"), "w") as f:
        json.dump(semantic_data, f, indent=2)
    
    yield data_dir
    
    # Cleanup
    import shutil
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)