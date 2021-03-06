# Balance
## Программа вычисления центровочного веса воздушных судов

Balance (центровка) - упрощенный (учебная версия) аналог, используемых в аэропортовой деятельности продуктов.
> !!! ВАЖНО !!!
Часть функционала требует доработки, поэтому крайне не рекомендуется использование в промышленной эксплуатации.

## Программа преддназначена для специально обученных людей, владеющих информацией о:
- типах воздушных судов (далее ВС) и их модификаций
- основных схемах компановки/размещения кресел и багажных отсеков
- правилах размещения пассажиров, используемых обслуживаемых авиакомпаний

## Правила работы

- В поставляемой базе данных имеются примеры заполнения комплектации ВС с возможностью добавления и изменения
- Каждая авиакомпания предоставляет информацию об используемых ею ВС и их комплектаций
- Заполняя центровочный лист, сначала нужно выбрать рейс (Flight), затем тип ВС, а потом и конкретное ВС по его номеру (a/c reg).
- Ввести корректные дату и время
- Ввести общее количество пассажиров (PAX)
- Ввести общее количество багажа (Cargo)
- Ввести количество топлива на вылет (Fuel) и количество заправленного топлива (Trip fuel)
- Затем следует распределить пассажиров по рядам с таблице "Manage seats", строка "peolpe", имея ввиду максимальное количество пассажиров на данном ряду (строка "max_of_seats")
- После размещения пассажиров нужно заполнить аналогичную таблицу для грузов - "Manage cargo"
- Затем необходимо проверить правильность заполнения, нажав кнопку "check". Программа поочередно проверит таблицы, и произведет расчет центровочных коэффициентов. Нужно чтобы количество пассажиров в поле "PAX" равнялось сумме размещенных пассажиров на рядах, аналогично - с грузом. Корректными считаются коэффициенты между 27 и 30, и, если полученные не попадают в указанный диапазон нужно ввести правки - сдвинуть людей и багаж влево (если коэффициент больше 30) или вправо (если коэффициент меньше 27) по таблице.

## Правила сборки

Для сборки необходимо воспользоваться "pyinstaller <путь к файлу проекта>/main.py -F", добавив к полученному файлу в папке "dist" остальные файлы из архива. 
