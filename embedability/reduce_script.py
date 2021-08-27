"""string = "in "
for i in range(1, 6634):
    if i == 6633:
        file =  '"C:\\Users\\brian\\private_ks\\embedability\\' + str(i) + '.red";END;'
    else:
        file =  '"C:\\Users\\brian\\private_ks\\embedability\\' + str(i) + '.red",'
    string = string + file
f = open("reduce_script.red", "w")
f.write(string)
f.close"""