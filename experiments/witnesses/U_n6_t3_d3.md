# U-type witness n=6, t=3, depth=3

This is one depth-optimal witness selected from a SAT model. It is not claimed to be canonical, comparator-count optimal, or minimum-size.

## Metadata

- kind: U
- n: 6
- t: 3
- depth: 3
- total comparator count: 9
- layer comparator counts: 3, 3, 3

Wire numbers increase from top to bottom. Layers progress left to right.

## Layers

- Layer 1: (1,3), (2,6), (4,5)
- Layer 2: (1,5), (2,3), (4,6)
- Layer 3: (1,6), (2,5), (3,4)

## Verification

- independent verifier result: True (verified all binary inputs)

## Exactness Provenance

- shorter depths checked UNSAT: 0, 1, 2
- depth 3: verified SAT

## Traces

### binary input with exactly t zeros: 010101

| step | values |
| --- | --- |
| input | 0, 1, 0, 1, 0, 1 |
| after layer 1 | 0, 1, 0, 0, 1, 1 |
| after layer 2 | 0, 0, 1, 0, 1, 1 |
| after layer 3 | 0, 0, 0, 1, 1, 1 |
| final output | 0, 0, 0, 1, 1, 1 |
| target satisfied | True |

### binary input with fewer than t zeros: 111010

| step | values |
| --- | --- |
| input | 1, 1, 1, 0, 1, 0 |
| after layer 1 | 1, 0, 1, 0, 1, 1 |
| after layer 2 | 1, 0, 1, 0, 1, 1 |
| after layer 3 | 1, 0, 0, 1, 1, 1 |
| final output | 1, 0, 0, 1, 1, 1 |
| target satisfied | True |

### distinct integer input: 9,2,7,1,5,3

| step | values |
| --- | --- |
| input | 9, 2, 7, 1, 5, 3 |
| after layer 1 | 7, 2, 9, 1, 5, 3 |
| after layer 2 | 5, 2, 9, 1, 7, 3 |
| after layer 3 | 3, 2, 1, 9, 7, 5 |
| final output | 3, 2, 1, 9, 7, 5 |
| target satisfied | True |
