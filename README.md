CGPS-Kleborate
--------------

Docker wrapper of Kat Holt's Kleborate for integration with Pathogenwatch.

Takes a FASTA file streamed to SDTIN and writes a JSON blob to STDOUT

Test with:
```
cd test_data
gunzip -c NTUH-K2044.fasta.gz | docker run --rm  -i kleborate
{
    "strain": "query",
    "ST": "ST23",
    "virulence_score": "4",
    "Yersiniabactin": "ybt 2; ICEKp1",
    "YbST": "326",
    "Colibactin": "-",
    "CbST": "0",
    "Aerobactin": "iuc 2",
    "AbST": "1",
    "Salmochelin": "iro 5",
    "SmST": "18-1LV",
    "hypermucoidy": "rmpA;rmpA",
    "wzi": "wzi1",
    "K_locus": "KL1",
    "K_locus_confidence": "Perfect",
    "O_locus": "O1v2",
    "O_locus_confidence": "Very high"
}
```