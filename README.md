# CFC
 Compiler for the CAPPUS processor

## Errors
General format: XXX

### Errors 1XX: Lexing errors

### Errors 2XX: Syntactic parsing errors

#### Errors 20X: General errors

#### Errors 21X: Recursion errors

Error 210: End of recursion <br/>
Recursion continues until a syntax error appears. This error denotes the end of a such recursion, which has failed.

#### Errors 22X: Cache errors

Error 220: Cached invalid path for "rule": <br/>
Attempting to generate a node for this rule at this position has resulted in an error before, which has been cached and is being rereturned.

### Errors 3XX: Codegen errors

### Errors 4XX: Assembly errors

### Errors 5XX: Linking errors