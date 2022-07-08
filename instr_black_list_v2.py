import pandas as pd
import xlsxwriter
import msvcrt
import sys

print('Данная программа заносит результат в result.xlsx')
print('В result.xlsx заносится список номеров для обзвона без номеров из черного списка ')
print('Входные файлы должны быть в той же директории, что и программа')
x = str(input('Введите название файла с черным списком >>> '))
y = str(input('Введите список номеров для обзвона >>> '))
print('Обработка... Пожалуйста, подождите')

agent_name = ''
first_mass = []
sec_mass = []
final_mass = []
final_mass_2 = []
agent_name_mass = []

calling = pd.read_excel('./' + y + '.xlsx')

agent_name = calling['city'][0]
first_mass = calling['msisdn'].tolist()
# print(first_mass)

blacklist = pd.read_excel('./' + x + '.xlsx')
sec_mass = blacklist['msisdn'].tolist()


for i in first_mass:
    if i not in sec_mass:
        final_mass.append(i)
        final_mass_2.append(i)

print('Было ', len(first_mass))
print('Стало ', len(final_mass))
# print(final_mass)

print('Убрано ' + str(len(first_mass) - len(final_mass)) + ' номеров')

# открываем новый файл на запись
workbook = xlsxwriter.Workbook('result.xlsx')
# создаем там "лист"
worksheet = workbook.add_worksheet()
worksheet.write('A1', 'msisdn')
worksheet.write('B1', 'name')
worksheet.write('C1', 'city')
for i in range(len(final_mass)):
    worksheet.write('A' + str(i+2), final_mass[i])
    worksheet.write('B' + str(i+2), final_mass_2[i])
    worksheet.write('C' + str(i+2), agent_name)
# сохраняем и закрываем
workbook.close()
print("Программа закончена")
print("Нажмите esc, чтобы выйти")
while True:
    if msvcrt.kbhit():
        k = ord(msvcrt.getch())
        if k == 27:
            sys.exit()


