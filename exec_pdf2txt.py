import os

for idx in range(9):
    year = 2010 + idx
    print("processing %d" % year)
    count = 0
    path = './' + str(year) + '/'
    for file_name in os.listdir(path):
        if '.pdf' in file_name:
            status = os.system('python ./pdf2txt.py ' + path + file_name +
                               ' -o ' + path + 'txt/' +
                               file_name.split('.pdf')[0] + '.txt')
            if status == 0:
                count += 1
            if count % 100 == 0:
                print(count)
