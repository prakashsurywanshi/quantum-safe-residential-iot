# IEEE Submission Package

Manuscript: **A Sustainable Hybrid QKD–PQC Security Architecture for
Quantum-Resilient Residential IoT**
Author: Prakash Suryawanshi (Qodeigence Infocircle Private Limited)

Target venue: IEEE (generic `IEEEtran` journal template; intended for the
*IEEE Internet of Things Journal* / *IEEE Internet of Things Magazine* — the
addressee line in the cover letter can be adjusted once the venue is fixed).

## Contents

```
IEEE Submission/
├── manuscript/
│   ├── main.tex                 # IEEEtran manuscript (source)
│   ├── main.pdf                 # compiled manuscript (9 pp, two-column)
│   ├── Fig1.png                 # architecture figure
│   ├── Fig_Energy_Scalability.png
│   ├── Fig_Energy_Per_MB.png
│   └── Fig_Sensitivity.png
├── cover-letter/
│   ├── IEEE-cover-letter.tex    # cover letter (source)
│   └── IEEE-cover-letter.pdf    # compiled cover letter (2 pp)
├── keypoints/
│   └── keypoints.txt            # key points for editor reference
├── figures/                     # high-resolution figure exports (PNG + PDF)
│   ├── Fig1.png
│   ├── Fig_Energy_Scalability.pdf / .png
│   ├── Fig_Energy_Per_MB.pdf / .png
│   └── Fig_Sensitivity.pdf / .png
├── graphical-abstract/
│   ├── Graphical_Abstract.png   # Graphical Abstract (upload separately)
│   └── Graphical_Abstract.pdf
└── README.md                    # this file
```

## Compilation

The manuscript uses the standard IEEE `IEEEtran` class:

```bash
cd manuscript
pdflatex main.tex
pdflatex main.tex
pdflatex main.tex
```

The cover letter uses a plain `article` class:

```bash
cd cover-letter
pdflatex IEEE-cover-letter.tex
pdflatex IEEE-cover-letter.tex
```

Verified: main manuscript compiles with 0 errors and 0 undefined
references/citations; cover letter compiles clean.

## Artifact / Data Availability

All code, datasets, models, and scripts that reproduce the results are archived
in the public GitHub repository:

- Repository: https://github.com/prakashsurywanshi/quantum-safe-residential-iot
- Branch: `ieee-submission`
- Tag: `ieee-v1.0`

## Notes for submission

1. **Manuscript:** upload `manuscript/main.pdf` (or the `main.tex` source plus
   the four PNG figures if the portal requests source files).
2. **Cover letter:** upload `cover-letter/IEEE-cover-letter.pdf`. Update the
   addressee to the exact journal (Journal vs. Magazine) before submission.
3. **Graphical Abstract:** upload `graphical-abstract/Graphical_Abstract.png`
   as a separate file (not embedded in the manuscript).
4. **Key points:** paste or attach `keypoints/keypoints.txt` for the editor.
5. **Suggested reviewers / declarations:** follow the portal prompts; the
   competing-interest declaration is included at the end of the manuscript.
