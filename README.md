Run with no extra options to just the virulence predictions.

```
cd test_data
docker run --rm -it -v $PWD:/data registry.gitlab.com/cgps/docker-kleborate python3 kleborate-runner.py -a /data/MGH78578.fasta.gz /data/Klebs_HS11286.fasta.gz /data/NTUH-K2044.fasta.gz -o /data/kleborate.out
```