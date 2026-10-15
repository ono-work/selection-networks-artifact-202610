# V-type witness n=6, t=3, depth=5

This is one depth-optimal witness selected from a SAT model. It is not claimed to be canonical, comparator-count optimal, or minimum-size.

## Metadata

- kind: V
- n: 6
- t: 3
- depth: 5
- total comparator count: 14
- layer comparator counts: 3, 3, 3, 3, 2

Wire numbers increase from top to bottom. Layers progress left to right.

## Layers

- Layer 1: (1,6), (2,3), (4,5)
- Layer 2: (1,2), (3,4), (5,6)
- Layer 3: (1,6), (2,3), (4,5)
- Layer 4: (1,2), (3,4), (5,6)
- Layer 5: (1,6), (2,3)

## Verification

- independent verifier result: True (verified all binary inputs)

## Exactness Provenance

- shorter depths checked UNSAT: 0, 1, 2, 3, 4
- depth 5: verified SAT

## Traces

### binary input with exactly t zeros: 010101

| step | values |
| --- | --- |
| input | 0, 1, 0, 1, 0, 1 |
| after layer 1 | 0, 0, 1, 0, 1, 1 |
| after layer 2 | 0, 0, 0, 1, 1, 1 |
| after layer 3 | 0, 0, 0, 1, 1, 1 |
| after layer 4 | 0, 0, 0, 1, 1, 1 |
| after layer 5 | 0, 0, 0, 1, 1, 1 |
| final output | 0, 0, 0, 1, 1, 1 |
| target satisfied | True |

### binary input with fewer than t zeros: 111010

| step | values |
| --- | --- |
| input | 1, 1, 1, 0, 1, 0 |
| after layer 1 | 0, 1, 1, 0, 1, 1 |
| after layer 2 | 0, 1, 0, 1, 1, 1 |
| after layer 3 | 0, 0, 1, 1, 1, 1 |
| after layer 4 | 0, 0, 1, 1, 1, 1 |
| after layer 5 | 0, 0, 1, 1, 1, 1 |
| final output | 0, 0, 1, 1, 1, 1 |
| target satisfied | True |

### distinct integer input: 9,2,7,1,5,3

| step | values |
| --- | --- |
| input | 9, 2, 7, 1, 5, 3 |
| after layer 1 | 3, 2, 7, 1, 5, 9 |
| after layer 2 | 2, 3, 1, 7, 5, 9 |
| after layer 3 | 2, 1, 3, 5, 7, 9 |
| after layer 4 | 1, 2, 3, 5, 7, 9 |
| after layer 5 | 1, 2, 3, 5, 7, 9 |
| final output | 1, 2, 3, 5, 7, 9 |
| target satisfied | True |
