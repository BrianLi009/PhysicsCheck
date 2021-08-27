
load_package redlog;
rlset R;
procedure d(x,y);
    (first x) * (first y) +
    (second x) * (second y) +
    (third x) * (third y);
procedure k(x,y);
    {(second x)*(third y) - (third x)*(second y),
     (third x)*(first y) - (first x)*(third y),
     (first x)*(second y) - (second x)*(first y)};
v0c1 := 1; v0c2 := 0; v0c3 := 0;
v1c1 := 0; v1c2 := 1; v1c3 := 0;

v0 := {v0c1, v0c2, v0c3}; 
v1 := {v1c1, v1c2, v1c3}; 
v2 := {v2c1, v2c2, v2c3}; 
neq0 := k(v0,k(v2,v1)); 
neq1 := k(v0,v2); 
neq2 := k(v0,k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),k(v2,v0))); 
neq3 := k(v0,k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1)); 
neq4 := k(v0,k(k(v2,v1),v2)); 
neq5 := k(v0,k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))); 
neq6 := k(v1,k(v2,v0)); 
neq7 := k(v1,v2); 
neq8 := k(v1,k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),k(v2,v0))); 
neq9 := k(v1,k(k(k(v2,v1),v2),v0)); 
neq10 := k(v1,k(k(v2,v1),v2)); 
neq11 := k(v1,k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))); 
neq12 := k(k(v2,v0),k(v2,v1)); 
neq13 := k(k(v2,v0),k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1)); 
neq14 := k(k(v2,v0),k(k(k(v2,v1),v2),v0)); 
neq15 := k(k(v2,v0),k(k(v2,v1),v2)); 
neq16 := k(k(v2,v0),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))); 
neq17 := k(k(v2,v1),k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),k(v2,v0))); 
neq18 := k(k(v2,v1),k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1)); 
neq19 := k(k(v2,v1),k(k(k(v2,v1),v2),v0)); 
neq20 := k(k(v2,v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))); 
neq21 := k(v2,k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),k(v2,v0))); 
neq22 := k(v2,k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1)); 
neq23 := k(v2,k(k(k(v2,v1),v2),v0)); 
neq24 := k(v2,k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))); 
neq25 := k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),k(v2,v0)),k(k(k(v2,v1),v2),v0)); 
neq26 := k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),k(v2,v0)),k(k(v2,v1),v2)); 
neq27 := k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),v0)); 
neq28 := k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(v2,v1),v2)); 
phi := 
       (first neq0 neq 0 or
        second neq0 neq 0 or
        third neq0 neq 0) and 
       (first neq1 neq 0 or
        second neq1 neq 0 or
        third neq1 neq 0) and 
       (first neq2 neq 0 or
        second neq2 neq 0 or
        third neq2 neq 0) and 
       (first neq3 neq 0 or
        second neq3 neq 0 or
        third neq3 neq 0) and 
       (first neq4 neq 0 or
        second neq4 neq 0 or
        third neq4 neq 0) and 
       (first neq5 neq 0 or
        second neq5 neq 0 or
        third neq5 neq 0) and 
       (first neq6 neq 0 or
        second neq6 neq 0 or
        third neq6 neq 0) and 
       (first neq7 neq 0 or
        second neq7 neq 0 or
        third neq7 neq 0) and 
       (first neq8 neq 0 or
        second neq8 neq 0 or
        third neq8 neq 0) and 
       (first neq9 neq 0 or
        second neq9 neq 0 or
        third neq9 neq 0) and 
       (first neq10 neq 0 or
        second neq10 neq 0 or
        third neq10 neq 0) and 
       (first neq11 neq 0 or
        second neq11 neq 0 or
        third neq11 neq 0) and 
       (first neq12 neq 0 or
        second neq12 neq 0 or
        third neq12 neq 0) and 
       (first neq13 neq 0 or
        second neq13 neq 0 or
        third neq13 neq 0) and 
       (first neq14 neq 0 or
        second neq14 neq 0 or
        third neq14 neq 0) and 
       (first neq15 neq 0 or
        second neq15 neq 0 or
        third neq15 neq 0) and 
       (first neq16 neq 0 or
        second neq16 neq 0 or
        third neq16 neq 0) and 
       (first neq17 neq 0 or
        second neq17 neq 0 or
        third neq17 neq 0) and 
       (first neq18 neq 0 or
        second neq18 neq 0 or
        third neq18 neq 0) and 
       (first neq19 neq 0 or
        second neq19 neq 0 or
        third neq19 neq 0) and 
       (first neq20 neq 0 or
        second neq20 neq 0 or
        third neq20 neq 0) and 
       (first neq21 neq 0 or
        second neq21 neq 0 or
        third neq21 neq 0) and 
       (first neq22 neq 0 or
        second neq22 neq 0 or
        third neq22 neq 0) and 
       (first neq23 neq 0 or
        second neq23 neq 0 or
        third neq23 neq 0) and 
       (first neq24 neq 0 or
        second neq24 neq 0 or
        third neq24 neq 0) and 
       (first neq25 neq 0 or
        second neq25 neq 0 or
        third neq25 neq 0) and 
       (first neq26 neq 0 or
        second neq26 neq 0 or
        third neq26 neq 0) and 
       (first neq27 neq 0 or
        second neq27 neq 0 or
        third neq27 neq 0) and 
       (first neq28 neq 0 or
        second neq28 neq 0 or
        third neq28 neq 0) and 
       d(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),k(v2,v0))) = 0 and 
        true;
rlqe 
     ex(v2c3,
     ex(v2c2,
     ex(v2c1,phi)));
off echo