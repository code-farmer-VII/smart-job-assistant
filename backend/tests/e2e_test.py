"""
PHASE 9 — End-to-End Test Script
Tests the complete Smart Job Assistant pipeline:
  Step 1: Feed a sample CV through the Extractor → saves to JSON data files
  Step 2: Feed a sample Job Description through the Extractor → saves to JSON data files
  Step 3: Verify the data was written correctly
  Step 4: Run the Job Analysis via MCP
  Step 5: Run the RAG pipeline for Interview Preparation
"""

import os
import sys
import json
import asyncio

# Ensure project root is on the path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

DIVIDER = "\n" + "=" * 60 + "\n"

async def run_test():
    print(DIVIDER)
    print("PHASE 9 — END-TO-END TEST")
    print(DIVIDER)

    # -------------------------------------------------------
    # STEP 1: Extract CV
    # -------------------------------------------------------
    print("STEP 1: Extracting sample CV...")
    print("-" * 40)

    cv_path = os.path.join(PROJECT_ROOT, "tests", "sample_cv.txt")
    with open(cv_path, "r", encoding="utf-8") as f:
        cv_text = f.read()

    from client.extractor import extract_and_save
    cv_result = await extract_and_save(cv_text)
    print(cv_result)

    # -------------------------------------------------------
    # STEP 2: Extract Job Description
    # -------------------------------------------------------
    print(DIVIDER)
    print("STEP 2: Extracting sample Job Description...")
    print("-" * 40)

    job_path = os.path.join(PROJECT_ROOT, "tests", "sample_job.txt")
    with open(job_path, "r", encoding="utf-8") as f:
        job_text = f.read()

    job_result = await extract_and_save(job_text)
    print(job_result)

    # -------------------------------------------------------
    # STEP 3: Verify Data Files
    # -------------------------------------------------------
    print(DIVIDER)
    print("STEP 3: Verifying data files...")
    print("-" * 40)

    data_dir = os.path.join(PROJECT_ROOT, "data")
    for fname in ["profile.json", "skills.json", "experience.json", "projects.json", "jobs.json"]:
        fpath = os.path.join(data_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                count = len([i for i in data if any(v for k, v in i.items() if k != "id" and v)])
                print(f"  [OK] {fname}: {count} populated entries")
            elif isinstance(data, dict):
                filled = sum(1 for v in data.values() if v)
                print(f"  [OK] {fname}: {filled} filled fields")
        else:
            print(f"  [FAIL] {fname}: NOT FOUND")

    # -------------------------------------------------------
    # STEP 4: Job Analysis
    # -------------------------------------------------------
    print(DIVIDER)
    print("STEP 4: Running Job Analysis...")
    print("-" * 40)

    # Find the first job with a title
    jobs_path = os.path.join(data_dir, "jobs.json")
    with open(jobs_path, "r", encoding="utf-8") as f:
        jobs_data = json.load(f)

    target_job_id = None
    for job in jobs_data:
        if job.get("title"):
            target_job_id = job["id"]
            print(f"  Analyzing job: {job['title']} ({target_job_id})")
            break

    if target_job_id:
        from client.analysis import analyze_job
        analysis_result = await analyze_job(target_job_id)
        # Print first 500 chars to keep output manageable
        print(analysis_result[:500] + ("..." if len(analysis_result) > 500 else ""))
    else:
        print("  [WARN] No populated job found to analyze. Skipping.")

    # -------------------------------------------------------
    # STEP 5: RAG Interview Prep
    # -------------------------------------------------------
    print(DIVIDER)
    print("STEP 5: Running RAG Interview Preparation...")
    print("-" * 40)

    from rag.pipeline import run_interview_prep
    rag_result = run_interview_prep("Prepare me for a senior full stack developer interview focusing on React, Python, and system design.")
    print(rag_result[:500] + ("..." if len(rag_result) > 500 else ""))

    # -------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------
    print(DIVIDER)
    print("END-TO-END TEST COMPLETE")
    print(DIVIDER)
    print("All 5 steps executed. Review the output above for results.")

if __name__ == "__main__":
    asyncio.run(run_test())
