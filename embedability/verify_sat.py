
from io import StringIO

def verify_sat(filename, g, output_unsat_f, output_sat_f):
    io = StringIO()
    io.write('        m = s.model() \n')
    for i in g:
        io.write("        f.write( " + " '" + "vertex " + str(i) + ":' + '\\n' ) " + "\n")
        io.write('        f.write(str(m.evaluate(ver' + str(i) + '[0])) + "\\n" )' + '\n')
        io.write('        f.write(str(m.evaluate(ver' + str(i) + '[1])) + "\\n" )' + '\n')
        io.write('        f.write(str(m.evaluate(ver' + str(i) + '[2])) + "\\n" )' + '\n')
    io.write('    check = Solver()\n')
    for v in g:
        for v2 in g:
            if v2 in g[v]:
                str_format = "    check.add(m.evaluate(ver{0}[0] * ver{1}[0]+ver{0}[1] * ver{1}[1]+ver{0}[2] * ver{1}[2] == 0))\n"
                io.write(str_format.format(str(v), str(v2)))
            #check noncolinear
            if v2 != v:
                str_format = "    check.add(Not(And(m.evaluate(ver{0}[1] * ver{1}[2] - ver{0}[2]* ver{1}[1] == 0), m.evaluate(ver{0}[2] * ver{1}[0] - ver{0}[0]* ver{1}[2] == 0), m.evaluate(ver{0}[0] * ver{1}[1] - ver{0}[1]* ver{1}[0] == 0)))) \n"
                io.write(str_format.format(str(v), str(v2)))
    io.write('    with open(output_sat_f, "a+") as f: \n')
    io.write('        if check.check() == unsat:\n')
    io.write('            f.write("verification failed") \n')
    io.write('        if check.check() == sat:\n')
    io.write('            f.write("verified")\n')
    io.write('        else:\n')
    io.write('            f.write("error during verification")')
    with open('file.py', mode='a') as f:
        print(io.getvalue(), file=f)