
import csv

# read data from xlsx and save data in a csv file
def xlxstocsv( tabnames, substring, importedfile ):
   
   for num in tabnames:
    if num.find(substring) > -1:
        sheet = importedfile[num]        
        name = "temp/" + num + ".csv"
        with open(name, 'w', newline='') as file:
            savefile = csv.writer(file)
            for i in sheet.rows:
                savefile.writerow([cell.value for cell in i])


# read data from xlsx and save data in a csv file
def xlxstocsvW10( tabnames, substring, importedfile ):
   
   for num in tabnames:
    if num.find(substring) > -1:
        sheet = importedfile[num]        
        name = "datasystem/windminutes/" + num + ".csv"
        with open(name, 'w', newline='') as file:
            savefile = csv.writer(file)
            for i in sheet.rows:
                savefile.writerow([cell.value for cell in i])

# read data from xlsx and save data in a csv file
def xlxstocsvres( tabnames, substring, importedfile ):
   
   for num in tabnames:
    if num.find(substring) > -1:
        sheet = importedfile[num]        
        name = "results/csv_variables/" + num + ".csv"
        with open(name, 'w', newline='') as file:
            savefile = csv.writer(file)
            for i in sheet.rows:
                savefile.writerow([cell.value for cell in i])

# read data from xlsx and save data in a csv file
def xlxstocsvsaved( tabnames, substring, importedfile ):
   
   for num in tabnames:
    if num.find(substring) > -1:
        sheet = importedfile[num]        
        name = "saved_simulations/csvreports/" + num + ".csv"
        with open(name, 'w', newline='') as file:
            savefile = csv.writer(file)
            for i in sheet.rows:
                savefile.writerow([cell.value for cell in i])
