# CGPS-Kleborate

Docker wrapper of Kat Holt's Kleborate for integration with Pathogenwatch.

Takes a FASTA file streamed to SDTIN and writes a JSON blob to STDOUT

## Testing

```
cat examples/kpsc_example.fasta | docker run --rm  -i registry.gitlab.com/cgps/cgps-kleborate:v2.0.0
```

## Building

Support is provided for running Kleborate in 3 different modes:
1. kpsc - K. pnuemoniae species complex
2. kosc - K. ocytoca species complex
3. other - The species module only. Intended for Klebsiella species validation.

### Building all the images
```
./build.sh {Kleborate version e.g. 3.1.0}
```

### Building individual images

The `prod` target in the Dockerfile can be used to generate a scheme-specific image.

```
docker build --rm --build-arg KLEBORATE_VERSION=v3.1.0 --build-arg SPECIES=kpsc -t registry.gitlab.com/cgps/pathogenwatch-tasks/kleborate:v3.1.0 .
```

### Building a dev image for wrapper code

The `dev` targe can be used to build an image that includes all dependencies for testing or fixing the dev wrapper.

```
docker build --rm --target dev --build-arg KLEBORATE_VERSION=v3.1.0 -t kleborate-dev .
```

### Building Kleborate

The `kleborate` target can be used to create an image that runs Kleborate without the wrapper script.

```
docker build --rm --target kleborate --build-arg KLEBORATE_VERSION=v3.1.0 -t kleborate:v3.1.0 .
```

