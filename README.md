# bazel vs buck2 test

I think the rule of thumb is: Don't use bazel/buck2 unless you have to, and the project literally cannot be functional without trying it

https://news.ycombinator.com/item?id=32828584

My take away
- bazel with well supported languages are easy to set up
- jupyter with bazel is still a bit weird, 
- buck2 is not well supported, documents are lacking

In the repo:
- set up on different language
- build speed test, ease of use test
- jupyter lab support 
- set up a remote executor (don't really work for buck2, prob some problems with the docker images used in executor not aligning with the buck2's remote?)
- TODO: ipc benchmarks between languages

## Set up

### Bazel
Install bazel via bazelisk

npm install -g @bazel/bazelisk

```bash
bazelisk run //:deps
bazelisk build //...
bazelisk test //...
```

To run jupyter

```bash
bazelisk run //tools:lab
```

### Buck2

Pretty much the same

```bash
buck2 run //third_party:update_deps
buck2 build //...

# Something something with lab
```
