'''
This program reads data from the .txt output from ImageJ's macro on leaf imaging.
After the data has been read, it is converted to proper format in order to be 
written into a database so that queries can be run on it to combine the data
from different parts of leafs into one total area of leaf.

This program will not be able to catch every single problem within these files, but it can come close.
So in order to make everything easier, make sure the pictures are taken well, with nothing other
than leaves on the board and the leaves properly spaced apart with plenty of gap in between.

This program basically works by running the some loop over until the amount of times it is told
to run ends. This is entered by the user. The program takes what was written into a txt file, 
converting it to a database, and then running queries on the database to splice out data into a list of lists (matrix).
After the list has been made, the loop runs on the matrix, slowly compacting the overall list by adding area.

This is by no means a catch all program as it cannot fully account for every problem experienced
found in all of these images. For the most part, the data will be correct, but there will most 
likely be one or two errors within a data pool so large.

In order to use this more effectively, copy and paste the main for loop multiple times
so that the program can compact the area data further, leading to more accurate data.

Column names should be removed from the txt file before using this program.

Version 1.00

Created by Luke Steffen
Created on 06/22/2017

Patch 1.1:
    
    1. Added system to allow user to determine how many times the loop
    should run more efficiently.
    
    2. Allows user to now determine if they would like to have the results printed to the
    console
    
    Updated by Luke Steffen
    Updated on 07/05/2017
    
Patch 1.2:
    
    1. Implemented a new sytem to find vertically placed leaves and remove them from the combining process
    and adding the leaves to the end of the output file.
    
    Updated by Luke Steffen
    Updated on 07/07/2017
    
Patch 1.3:
    
    1. Now able to pick out objects at certain x and y coordinate range. The objects are placed in a list
    and the user is able to output them into other places.
    
    Updated by Luke Steffen
    Updated on 07/21/2017
'''
import sqlite3 as sql

in2 = input("Please enter the filepath of the ImageJ results: ")
in1 = input("Please enter the filepath of the database: ")
in3 = input("Please enter the filepath the data will be written to: ")

con = sql.connect(in1)
file = open(in2, "r")
file2 = open(in3, "w")

c = con.cursor()

# The line below should only be used if the creation of a new table is needed.
c.execute("CREATE TABLE leaf(ID, Label, Area, XM, YM, Perimeter, Circumference, Feret, FeretX, FeretY, FeretAngle, MiniF, AR, Round, Solidity)")
mainList = []
for line in file:
    l = line.split('\t')
    mainList.append(l)

#The following three lines should only be used if you're writing data for the first time.
for l in mainList:
    c.execute("INSERT INTO leaf VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", l)
con.commit()
print("Data has been written to database\n")
c.execute("SELECT Area FROM leaf")
area = c.fetchall()
avg = 0
area2 = []
c1 = 0
#These for loops convert the area to floats and calculates the rough average of the leaf area.
for a in area:
    if (a[0] != "Area"):
        a = a[0]
        a = float(a)
        area2.append(a)

for a in area2:
    avg = avg + a 
avg = avg / len(area2)
print(avg)
# These three lines and for loop set up the lists by retrieving the data from the database
# After, it converts the variables needed to floats so mathmatical functions can be performed
c.execute("SELECT ID, Label, Area, XM, YM, Feret, FeretAngle FROM leaf")
results = c.fetchall()
results2 = []
# This for loop converts all values within the database to floats
for l in results:
    l = list(l)
    if (l[2] != "Area"):
        l[2] = float(l[2])
        l[3] = float(l[3])
        l[4] = float(l[4])
        l[5] = float(l[5])
        l[6] = float(l[6])
        results2.append(l)
results = results2
times = input("Enter in the amount of times the loop should run: ")
times = int(times)
verticals = []
nonLeaves = []
copylist = results
'''This for loop finds vertical leaves by looking at the FeretAngle to see if it is 
around 90 degrees. It then appends that leaf to a list of vertical leaves'''
for v in results:
    if (v[5] < 10):
        pass
    else:
        if (80 < v[6] < 100 ):
            verticals.append(v)
#             print("Appending", v)
'''This for loop removes the verticals leaves from the original results list
by cross referencing them with the vertical leaves list'''
for v1 in range(0, len(results)):
    if (v1 == len(results) - 1):
        break
    for r in verticals:
        if (r == results[v1]):
            results.remove(r)
#             print("Removing ", r)
print("Verticals have been moved from the list.")
'''This for loop detects clamp present within the 2016 data and removes it from the overall list.
If there is not clamp or other object not present within the images, it is suggested that this code
is commented out. If the object is in another common spot within the files, the x and y Range can 
be changed to match'''
for c in results:
    if (30 < c[3] < 32 and 81 < c[4] < 83):
        nonLeaves.append(c)
'''This loop removes non-leaves from the list, preventing them from interfering with the data.
It does this by cross referencing the the nonLeaves list with the main results list.'''
for v2 in range(0, len(results)):
    if (v2 == len(results) - 1):
        break
    for c in nonLeaves:
        if (c == results[v2]):
            results.remove(c)
print("Objects have been removed from the list.")
for t in range(0, times):
    print(t + 1)
    '''
    This is the main for loop of the program. It works by checking the y of the leaf and leaf in front of it.
    If the y values are close enough and the area of the leaf is under the average area, the two areas are
    combined into the first value and deleting the data line in front of it. This needs to be repeated more
    than once as it can only take into account two pieces at a time, therefore skipping is possible.
    '''
    for i in range(0, len(results)):
        if (i == len(results) - 1):
            break
        if (results[i][1] == results[i+1][1]):
            if (results[i][4] + 3.2 > results[i+1][4]):
                if ((results[i][2] < avg + 1) or (results[i+1][2] < avg + 1)):
                    results[i][2] = results[i][2] + results[i+1][2]
                    results.remove(results[i+1])
            elif (results[i][4] - 3.2 < results[i+1][4] and (results[i][4] + 3.2 > results[i+1][4])):
                if ((results[i][2] < avg + 1) or (results[i+1][2] < avg + 1)):
                    results[i][2] = results[i][2] + results[i+1][2]
                    results.remove(results[i+1])

print("c = console f = file b = both n = none")
printobj = input("Would you like the the objects to be written on the console or file (c, f, b, n): ")
if (printobj == "c"):
    print("Objects")
    for o in nonLeaves:
        print(o)
elif (printobj == "f"):
    file2.write("Objects\n")
    for n in nonLeaves:
        for item in n:
            file2.write(str(item))
            file2.write("\t")
        file2.write('\n')
    print("Objects written to file")
elif (printobj == "b"):
    print("Objects")
    for o in nonLeaves:
        print(o)
    file2.write("Objects\n")
    for n in nonLeaves:
        for item in n:
            file2.write(str(item))
            file2.write("\t")
        file2.write('\n')
    print("Objects written to file")
else:
    print("Objects will not be written anywhere.")

'''
This while loop acts as a failsafe for user input.
within the loop, the user can decide if they want to write the results
to the console or not. Both options write to the output file.
'''                    
state = "run"
while (state != "done"):
    printR = input("Would you like the results printed onto the console? (y or n): ")
    if (printR == 'y'):
        file2.write("ID\tName\tArea\tXM\tYM\n")
        for line in results:
            for item in line:
                file2.write(str(item))
                file2.write('\t')
            file2.write('\n')
        file.close()
        file2.close()
        print("\nCombining and writing to file complete\n")
        print("Check the vertical leaves to make sure all of the datapoints")
        print("are leaves.")
        for line in results:
            print(c1, line, '\n')
            c1 += 1
        state = "done"
    elif (printR == 'n'):
        file2.write("ID\tName\tArea\tXM\tYM\tFeret\tFeretAngle\n")
        for line in results:
            for item in line:
                file2.write(str(item))
                file2.write('\t')
            file2.write('\n')
        file2.write("Vertical Leaves\n")
        for v in verticals:
            for vitem in v:
                file2.write(str(vitem))
                file2.write('\t')
            file2.write('\n')
        file.close()
        file2.close()
        print("\nCombining and writing to file complete\n")
        print("Check the vertical leaves to make sure all of the datapoints")
        print("are leaves if you have written them to the file.")
        state = "done"
    else:
        print("Invalid value entered")
                    