:- input(Input), zero_count(Input,Z), t(T), depth(D), Z < T,
   T - Z != #count { R : rank(R), one(Input,D,R) }.

:- input(Input), zero_count(Input,Z), t(T), depth(D), Z >= T,
   0 != #count { R : rank(R), one(Input,D,R) }.

#show selected/3.
