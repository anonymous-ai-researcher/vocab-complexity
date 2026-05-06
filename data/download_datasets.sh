#!/bin/bash
# Download benchmark ontologies from SML-Bench and NCES suite.
# Usage: bash data/download_datasets.sh

set -e
mkdir -p data/ontologies

echo "Downloading SML-Bench datasets..."
SML_BASE="https://github.com/SmartDataAnalytics/SML-Bench/raw/master/learningtasks"

# SML-Bench datasets
for ds in family mutagenesis carcinogenesis hepatitis mammographic nctrer premierleague suramin; do
    echo "  Downloading ${ds}..."
    mkdir -p data/ontologies/${ds}
    wget -q -O data/ontologies/${ds}/${ds}.owl \
        "${SML_BASE}/${ds}/owl/${ds}.owl" 2>/dev/null || \
    echo "    Warning: Could not download ${ds}.owl (check URL manually)"
    
    # Download learning problems if available
    wget -q -O data/ontologies/${ds}/lp.json \
        "${SML_BASE}/${ds}/data/lp.json" 2>/dev/null || true
done

echo "Downloading NCES suite datasets..."
NCES_BASE="https://github.com/dice-group/Ontolearn/raw/develop/KGs"

for ds in semantic_bible vicodi; do
    echo "  Downloading ${ds}..."
    mkdir -p data/ontologies/${ds}
    wget -q -O data/ontologies/${ds}/${ds}.owl \
        "${NCES_BASE}/${ds}/${ds}.owl" 2>/dev/null || \
    echo "    Warning: Could not download ${ds}.owl (check URL manually)"
done

echo ""
echo "Download complete. Verify files in data/ontologies/"
echo ""
echo "If automatic download fails, manually download from:"
echo "  SML-Bench: https://github.com/SmartDataAnalytics/SML-Bench"
echo "  NCES/Ontolearn: https://github.com/dice-group/Ontolearn"
echo ""
echo "Expected ontology files:"
ls -la data/ontologies/*/*.owl 2>/dev/null || echo "  (no .owl files found yet)"
