:- input(Input), rank(R), zero_count(Input,Z), depth(D), Z >= R, one(Input,D,R).
:- input(Input), rank(R), zero_count(Input,Z), depth(D), Z < R, not one(Input,D,R).

#show selected/3.
