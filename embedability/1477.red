
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
neq0 := k(k(k(k(v2,v1),v2),k(v0,v1)),k(k(k(v2,v1),v2),v0)); 
neq1 := k(k(k(k(v2,v1),v2),k(v0,v1)),k(v2,v1)); 
neq2 := k(k(k(k(v2,v1),v2),k(v0,v1)),v2); 
neq3 := k(k(k(k(v2,v1),v2),k(v0,v1)),k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),k(v0,v1))); 
neq4 := k(k(k(k(v2,v1),v2),k(v0,v1)),k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)))); 
neq5 := k(k(k(k(v2,v1),v2),k(v0,v1)),v0); 
neq6 := k(k(k(k(v2,v1),v2),k(v0,v1)),k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1))),v2)); 
neq7 := k(k(k(k(v2,v1),v2),k(v0,v1)),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))); 
neq8 := k(k(k(k(v2,v1),v2),k(v0,v1)),k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1)); 
neq9 := k(k(k(k(v2,v1),v2),k(v0,v1)),v1); 
neq10 := k(k(k(k(v2,v1),v2),v0),k(v2,v1)); 
neq11 := k(k(k(k(v2,v1),v2),v0),v2); 
neq12 := k(k(k(k(v2,v1),v2),v0),k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),k(v0,v1))); 
neq13 := k(k(k(k(v2,v1),v2),v0),k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)))); 
neq14 := k(k(k(k(v2,v1),v2),v0),k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1)))); 
neq15 := k(k(k(k(v2,v1),v2),v0),k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1))),v2)); 
neq16 := k(k(k(k(v2,v1),v2),v0),k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1)); 
neq17 := k(k(k(k(v2,v1),v2),v0),k(v0,v1)); 
neq18 := k(k(k(k(v2,v1),v2),v0),v1); 
neq19 := k(k(v2,v1),k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),k(v0,v1))); 
neq20 := k(k(v2,v1),k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)))); 
neq21 := k(k(v2,v1),v0); 
neq22 := k(k(v2,v1),k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1)))); 
neq23 := k(k(v2,v1),k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1))),v2)); 
neq24 := k(k(v2,v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))); 
neq25 := k(k(v2,v1),k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1)); 
neq26 := k(k(v2,v1),k(v0,v1)); 
neq27 := k(v2,k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),k(v0,v1))); 
neq28 := k(v2,k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)))); 
neq29 := k(v2,v0); 
neq30 := k(v2,k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1)))); 
neq31 := k(v2,k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))); 
neq32 := k(v2,k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1)); 
neq33 := k(v2,k(v0,v1)); 
neq34 := k(v2,v1); 
neq35 := k(k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),k(v0,v1)),v0); 
neq36 := k(k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),k(v0,v1)),k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1)))); 
neq37 := k(k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),k(v0,v1)),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))); 
neq38 := k(k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),k(v0,v1)),k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1)); 
neq39 := k(k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),k(v0,v1)),v1); 
neq40 := k(k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),k(v0,v1)),k(k(v2,v1),v2)); 
neq41 := k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),v0); 
neq42 := k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1)))); 
neq43 := k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1))),v2)); 
neq44 := k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),k(v0,v1)); 
neq45 := k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),v1); 
neq46 := k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),k(k(v2,v1),v2)); 
neq47 := k(v0,k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1)))); 
neq48 := k(v0,k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1))),v2)); 
neq49 := k(v0,k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))); 
neq50 := k(v0,k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1)); 
neq51 := k(v0,k(k(v2,v1),v2)); 
neq52 := k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1))),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))); 
neq53 := k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1))),k(v0,v1)); 
neq54 := k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1))),v1); 
neq55 := k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1))),k(k(v2,v1),v2)); 
neq56 := k(k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1))),v2),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))); 
neq57 := k(k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1))),v2),k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1)); 
neq58 := k(k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1))),v2),k(v0,v1)); 
neq59 := k(k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1))),v2),v1); 
neq60 := k(k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1))),v2),k(k(v2,v1),v2)); 
neq61 := k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),k(v0,v1)); 
neq62 := k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1); 
neq63 := k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(v0,v1)); 
neq64 := k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(v2,v1),v2)); 
neq65 := k(k(v0,v1),k(k(v2,v1),v2)); 
neq66 := k(v1,k(k(v2,v1),v2)); 
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
       (first neq29 neq 0 or
        second neq29 neq 0 or
        third neq29 neq 0) and 
       (first neq30 neq 0 or
        second neq30 neq 0 or
        third neq30 neq 0) and 
       (first neq31 neq 0 or
        second neq31 neq 0 or
        third neq31 neq 0) and 
       (first neq32 neq 0 or
        second neq32 neq 0 or
        third neq32 neq 0) and 
       (first neq33 neq 0 or
        second neq33 neq 0 or
        third neq33 neq 0) and 
       (first neq34 neq 0 or
        second neq34 neq 0 or
        third neq34 neq 0) and 
       (first neq35 neq 0 or
        second neq35 neq 0 or
        third neq35 neq 0) and 
       (first neq36 neq 0 or
        second neq36 neq 0 or
        third neq36 neq 0) and 
       (first neq37 neq 0 or
        second neq37 neq 0 or
        third neq37 neq 0) and 
       (first neq38 neq 0 or
        second neq38 neq 0 or
        third neq38 neq 0) and 
       (first neq39 neq 0 or
        second neq39 neq 0 or
        third neq39 neq 0) and 
       (first neq40 neq 0 or
        second neq40 neq 0 or
        third neq40 neq 0) and 
       (first neq41 neq 0 or
        second neq41 neq 0 or
        third neq41 neq 0) and 
       (first neq42 neq 0 or
        second neq42 neq 0 or
        third neq42 neq 0) and 
       (first neq43 neq 0 or
        second neq43 neq 0 or
        third neq43 neq 0) and 
       (first neq44 neq 0 or
        second neq44 neq 0 or
        third neq44 neq 0) and 
       (first neq45 neq 0 or
        second neq45 neq 0 or
        third neq45 neq 0) and 
       (first neq46 neq 0 or
        second neq46 neq 0 or
        third neq46 neq 0) and 
       (first neq47 neq 0 or
        second neq47 neq 0 or
        third neq47 neq 0) and 
       (first neq48 neq 0 or
        second neq48 neq 0 or
        third neq48 neq 0) and 
       (first neq49 neq 0 or
        second neq49 neq 0 or
        third neq49 neq 0) and 
       (first neq50 neq 0 or
        second neq50 neq 0 or
        third neq50 neq 0) and 
       (first neq51 neq 0 or
        second neq51 neq 0 or
        third neq51 neq 0) and 
       (first neq52 neq 0 or
        second neq52 neq 0 or
        third neq52 neq 0) and 
       (first neq53 neq 0 or
        second neq53 neq 0 or
        third neq53 neq 0) and 
       (first neq54 neq 0 or
        second neq54 neq 0 or
        third neq54 neq 0) and 
       (first neq55 neq 0 or
        second neq55 neq 0 or
        third neq55 neq 0) and 
       (first neq56 neq 0 or
        second neq56 neq 0 or
        third neq56 neq 0) and 
       (first neq57 neq 0 or
        second neq57 neq 0 or
        third neq57 neq 0) and 
       (first neq58 neq 0 or
        second neq58 neq 0 or
        third neq58 neq 0) and 
       (first neq59 neq 0 or
        second neq59 neq 0 or
        third neq59 neq 0) and 
       (first neq60 neq 0 or
        second neq60 neq 0 or
        third neq60 neq 0) and 
       (first neq61 neq 0 or
        second neq61 neq 0 or
        third neq61 neq 0) and 
       (first neq62 neq 0 or
        second neq62 neq 0 or
        third neq62 neq 0) and 
       (first neq63 neq 0 or
        second neq63 neq 0 or
        third neq63 neq 0) and 
       (first neq64 neq 0 or
        second neq64 neq 0 or
        third neq64 neq 0) and 
       (first neq65 neq 0 or
        second neq65 neq 0 or
        third neq65 neq 0) and 
       (first neq66 neq 0 or
        second neq66 neq 0 or
        third neq66 neq 0) and 
       d(k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2))),k(v0,v1)),k(k(k(k(k(k(k(v2,v1),v2),v0),k(k(v2,v1),v2)),v1),k(k(k(v2,v1),v2),k(v0,v1))),v2)) = 0 and 
        true;
rlqe 
     ex(v2c3,
     ex(v2c2,
     ex(v2c1,phi)));
off echo