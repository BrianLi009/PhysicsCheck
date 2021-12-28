```bash
├── approach 1
│   ├── canonicalsat_least.py: generate blocking clauses, where canonical is defined as lex-least
│   ├── canonicalsat_most.py: generate blocking clauses, where canonical is defined as lex-most
├── approach 2
│   ├── generate.py: generate blocking clauses
│   ├── find_canonical.py: given a graph, find its canonical representation
│   ├── helper functions...
├── canonical_subgraphs: all subgraphs with canonical repersentation up to certain order
├── run-subgraph-generation.sh (calling maplesat_ks)
└── .gitignore
```