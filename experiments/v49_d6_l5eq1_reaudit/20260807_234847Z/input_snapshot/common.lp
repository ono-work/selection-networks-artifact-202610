wire(1..N) :- n(N).
rank(1..T) :- t(T).
layer(1..D) :- depth(D).

pair(I,J) :- wire(I), wire(J), I < J.

{ selected(L,I,J) } :- layer(L), pair(I,J).

uses(L,W,I,J) :- selected(L,I,J), W = I.
uses(L,W,I,J) :- selected(L,I,J), W = J.
touched(L,W) :- uses(L,W,_,_).

:- layer(L), wire(W), 2 <= #count { I,J : uses(L,W,I,J) }.

active(L) :- selected(L,_,_).
:- layer(L), layer(L + 1), active(L + 1), not active(L).

one(Input,0,Wire) :- bit(Input,Wire,1).

one(Input,L,Wire) :-
    input(Input),
    layer(L),
    wire(Wire),
    one(Input,L - 1,Wire),
    not touched(L,Wire).

one(Input,L,I) :-
    input(Input),
    selected(L,I,J),
    one(Input,L - 1,I),
    one(Input,L - 1,J).

one(Input,L,J) :-
    input(Input),
    selected(L,I,J),
    one(Input,L - 1,I).

one(Input,L,J) :-
    input(Input),
    selected(L,I,J),
    one(Input,L - 1,J).
