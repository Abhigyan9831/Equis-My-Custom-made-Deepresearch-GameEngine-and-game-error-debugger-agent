import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

# Ensure LangSmith environment variables are set
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "gameengine-doctor")

from langsmith import Client, evaluate
from app.services.agent_service import run_agent

DATASET_NAME = "gameengine-doctor-eval"

# Benchmark evaluation dataset with diverse Vulkan, UE5, and Game bug scenarios
EVAL_DATA = [
    {
        "inputs": {"query": "VK_ERROR_OUT_OF_DEVICE_MEMORY on vkAllocateMemory when loading 4K textures"},
        "outputs": {
            "expected_category": "Vulkan",
            "expected_keywords": ["memory", "allocate", "heap", "vulkan"],
        },
    },
    {
        "inputs": {"query": "Vulkan pipeline barrier error: SYNC-HAZARD-WRITE-AFTER-WRITE on compute queue"},
        "outputs": {
            "expected_category": "Vulkan",
            "expected_keywords": ["barrier", "hazard", "synchronization", "dependency"],
        },
    },
    {
        "inputs": {"query": "UE5 Nanite mesh cluster culling crash with DXGI_ERROR_DEVICE_REMOVED on RTX 4080"},
        "outputs": {
            "expected_category": "UE5",
            "expected_keywords": ["nanite", "dxgi", "driver", "culling"],
        },
    },
    {
        "inputs": {"query": "Unreal Engine Lumen reflections flickering and ghosting on translucent water surfaces"},
        "outputs": {
            "expected_category": "UE5",
            "expected_keywords": ["lumen", "reflection", "translucent", "roughness"],
        },
    },
    {
        "inputs": {"query": "Low FPS drop and stutter after latest game patch in Cyberpunk on DX12 RTX 3060"},
        "outputs": {
            "expected_category": "GameBug",
            "expected_keywords": ["fps", "cache", "driver", "patch"],
        },
    },
]


def ensure_dataset(client: Client):
    """Create or update evaluation dataset in LangSmith."""
    if not client.has_dataset(dataset_name=DATASET_NAME):
        dataset = client.create_dataset(
            dataset_name=DATASET_NAME,
            description="Golden evaluation dataset for GameEngine-Doctor multi-agent system",
        )
        for item in EVAL_DATA:
            client.create_example(
                inputs=item["inputs"],
                outputs=item["outputs"],
                dataset_id=dataset.id,
            )
        print(f"Created LangSmith dataset '{DATASET_NAME}' with {len(EVAL_DATA)} examples.")
    else:
        print(f"Using existing LangSmith dataset: '{DATASET_NAME}'")


# ── Evaluator Functions ──
def check_diagnosis_non_empty(run, example) -> dict:
    """Evaluate that the diagnosis is populated and detailed."""
    diagnosis = run.outputs.get("diagnosis", "")
    score = 1.0 if (diagnosis and len(diagnosis) > 20 and "timed out" not in diagnosis.lower()) else 0.0
    return {"key": "diagnosis_completeness", "score": score}


def check_structured_fields(run, example) -> dict:
    """Evaluate that affected_systems and console_commands/code_fix are present."""
    affected = run.outputs.get("affected_systems", [])
    commands = run.outputs.get("console_commands", [])
    code = run.outputs.get("code_fix", "")
    has_structure = bool(affected) and (bool(commands) or bool(code))
    return {"key": "structured_fields_populated", "score": 1.0 if has_structure else 0.0}


def check_keyword_relevance(run, example) -> dict:
    """Evaluate domain keyword coverage between expected answers and synthesized diagnosis."""
    expected_kw = example.outputs.get("expected_keywords", [])
    diagnosis_text = (run.outputs.get("diagnosis", "") + " " + run.outputs.get("root_cause", "")).lower()
    matches = sum(1 for kw in expected_kw if kw.lower() in diagnosis_text)
    score = matches / len(expected_kw) if expected_kw else 1.0
    return {"key": "keyword_relevance", "score": round(score, 2)}


async def target_pipeline(inputs: dict) -> dict:
    """Adapter invoking run_agent for LangSmith evaluate."""
    query = inputs["query"]
    result = await run_agent(query)
    return {
        "diagnosis": result.diagnosis,
        "root_cause": result.root_cause,
        "affected_systems": result.affected_systems,
        "console_commands": result.console_commands,
        "code_fix": result.code_fix,
        "confidence": result.confidence,
    }


def main():
    client = Client()
    ensure_dataset(client)

    print("\nRunning LangSmith Automated Evaluation...")
    results = evaluate(
        target_pipeline,
        data=DATASET_NAME,
        evaluators=[check_diagnosis_non_empty, check_structured_fields, check_keyword_relevance],
        experiment_prefix="eval-v2-groq",
        max_concurrency=2,
    )
    print("\nEvaluation Completed!")
    print(f"Results viewable at: https://smith.langchain.com/o/{client.default_workspace_id}/datasets")


if __name__ == "__main__":
    main()
