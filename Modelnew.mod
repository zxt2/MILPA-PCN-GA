
set N;

param r{a in N, b in N}, default 0;
param baseFee{a in N, b in N} >= 0, default 0;
param slope{a in N, b in N} >= 0, default 0;
param source in N;
param destination in N;
param P;

var flow{a in N, b in N} >= 0;

var used{a in N, b in N} binary; 

var fee{a in N, b in N} >= 0;

var payment{a in N, b in N} >= 0;


s.t. binary{a in N, b in N}:  flow[a,b] <= used[a,b] * r[a,b] ;
s.t. paybinary{a in N, b in N}:  payment[a,b] <= used[a,b] * r[a,b] ;
s.t. capcon{a in N, b in N}: flow[a,b] <= r[a,b];

s.t. feecal{a in N, b in N: r[a,b]>0}: fee[a,b] = used[a,b]*baseFee[a,b] + payment[a,b]*slope[a,b];

s.t. flowcon{a in N: a <> source and a <> destination}: sum{x in N} flow[x,a] =  sum{y in N}  (flow[a,y]+fee[a,y]); 

s.t. paycon{a in N: a <> source and a <> destination}: sum{x in N} payment[x,a] =  sum{y in N}payment[a,y]; 

s.t. endToEnd: sum{x in N: x <> source} flow[source,x]  - sum{x in N: x <> source} flow[x, source] = P + sum{x in N, y in N: x <> source} fee[x,y];  

s.t. endToEnd2: sum{x in N: x <> destination} flow[x, destination] -  sum{x in N} flow[destination, x]  = P;

s.t. end1: sum{x in N: x <> source} payment[source,x]  - sum{x in N: x <> source} payment[x, source] = P;  

s.t. end2: sum{x in N: x <> destination} payment[x, destination] -  sum{x in N} payment[destination, x]  = P;

s.t. descon{x in N: x <> destination}: payment[x,destination] = flow[x,destination] ;

minimize cost: sum{x in N, y in N} fee[x,y];

end;



