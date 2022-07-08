import csv
from itertools import groupby
import xlsxwriter
import msvcrt
import sys

print('Данная программа заносит результат в result.xlsx')
print('В result.xlsx заносится список номеров для обзвона без номеров из черного списка ')
print('Входные файлы должны быть формата csv')
x = str(input('Введите название файла с черным списком >>> '))
y = str(input('Введите список номеров для обзвона >>> '))
print('Обработка... Пожалуйста, подождите')

agent_name = ''
first_mass = []
sec_mass = []
final_mass = []

with open(y + '.csv', newline='', encoding='UTF-8') as f:
    reader = csv.reader(f)
    for row in reader:
        first_mass.append(row[1][1:])
        agent_name = row[2]

with open(x + '.csv', encoding='UTF-8') as csvfile:
    reader = csv.DictReader(csvfile,
                            fieldnames=['msisdn1', 'result1', 'city1', 'None1', 'msisdn2', 'result2', 'city2',
                                        'None2', 'msisdn3', 'result3', 'city3'], restkey=None, restval=None)
    for row in reader:
        if row['city1'] == agent_name:
            sec_mass.append(row['msisdn1'])
        if row['city2'] == agent_name:
            sec_mass.append(row['msisdn2'])
        if row['city3'] == agent_name:
            sec_mass.append(row['msisdn3'])

    # print(sec_mass)

    new_sec_mass = [el for el, _ in groupby(sec_mass)]

    for i in new_sec_mass:
        if i not in first_mass:
            final_mass.append(i)

print('Убрано ' + str(len(first_mass) - len(final_mass)) + ' номеров')

# открываем новый файл на запись
workbook = xlsxwriter.Workbook('result.xlsx')
# создаем там "лист"
worksheet = workbook.add_worksheet()
for i in range(len(final_mass)):
    worksheet.write('A' + str(i), final_mass[i])
    worksheet.write('B' + str(i), final_mass[i])
    worksheet.write('C' + str(i), agent_name)
# сохраняем и закрываем
workbook.close()
print("Программа закончена")
print("Нажмите esc, чтобы выйти")
while True:
    if msvcrt.kbhit():
        k = ord(msvcrt.getch())
        if k == 27:
            sys.exit()


