CGPS-Kleborate
--------------

Docker wrapper of Kat Holt's Kleborate for integration with Pathogenwatch.

Takes a FASTA file streamed to SDTIN and writes a JSON blob to STDOUT

Test with:
```
cd test_data
cat test_data/Klebs_HS11286.fasta | docker run --rm  -i registry.gitlab.com/cgps/cgps-kleborate:v2.0.0
{
  "species": "Klebsiella pneumoniae",
  "ST": "ST11",
  "virulence_score": "1",
  "resistance_score": "3",
  "Yersiniabactin": "ybt 9; ICEKp3",
  "YbST": "15",
  "Colibactin": "-",
  "CbST": "0",
  "Aerobactin": "-",
  "AbST": "0",
  "Salmochelin": "-",
  "SmST": "0",
  "rmpA": "-",
  "rmpA2": "-",
  "wzi": "wzi74",
  "K_locus": "KL103",
  "K_locus_confidence": "Very high",
  "O_locus": "O2v1",
  "O_locus_confidence": "Very high",
  "AGly": "Aac3-IId*?;AadA2^;RmtB;StrA^;StrB",
  "Col": "PmrB-10%",
  "Fcyn": "-",
  "Flq": "GyrA-83I;ParC-80I",
  "Gly": "-",
  "MLS": "-",
  "Ntmdz": "-",
  "Phe": "-",
  "Rif": "-",
  "Sul": "SulII",
  "Tet": "TetG",
  "Tgc": "-",
  "Tmt": "DfrA12?",
  "Omp": "OmpK35-40%",
  "Bla": "TEM-1D^;TEM-1D^;TEM-1D^",
  "Bla_Carb": "KPC-2",
  "Bla_ESBL": "CTX-M-14;CTX-M-14",
  "Bla_ESBL_inhR": "-",
  "Bla_broad": "SHV-11",
  "Bla_broad_inhR": "-"
}
```