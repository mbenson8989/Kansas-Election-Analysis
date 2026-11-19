#!/bin/bash
# Full pipeline. Pass A and pass B are independent programs; compare_passes.py must be CLEAN before anything else runs.
set -e
cd /workspace/kansas-wiki
python3 scripts/pass_a.py > verification/passA_stdout.txt
python3 scripts/pass_b.py > verification/passB_stdout.txt
python3 scripts/compare_passes.py > verification/compare_stdout.txt
python3 scripts/analysis.py > verification/analysis_stdout.txt
python3 scripts/charts.py > /dev/null
python3 scripts/build_wiki.py
python3 scripts/verify_wiki.py > verification/wiki_number_check_stdout.txt
python3 -c "import json,sys; r=json.load(open('verification/wiki_number_check.json')); sys.exit(0 if r['PASS'] else 1)"
echo ALL CLEAN
