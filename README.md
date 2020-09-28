# Моделирование нижней геосферы земли
Босинзон Галина, 734 группа
## Код
Основной код, используемый для выполнения проекта, лежит в директории `python_code`

### Функция create_dataset
```python
def create_grouped_dataset(mat_file: str, param: str, filter_expr='1 = 1') -> DataFrame:
    """
    Функция, генерирующая из .mat-файла датафрэйм для параметра, отбирая записи по условию
    :param mat_file: путь к .mat файлу
    :param param: какой параметр считаем (Temperature или M)
    :param filter_expr: условие
    :return: DataFrame
    """
```
Функция создает датасет из `.mat`-файла, в котором сырые данные файла пересчитаны
в нужные значения `season`, `region`, `SZA` и `F107`. 
На выходе датасет дополнен значениями температуры или концентрации нейтралов (в
зависимости от переданного значения `param`), а также отобраны только нужные записи
с помощью фильтра `filter_expr`

Расчет значений `season`, `region`, `SZA` и `F107` и фильтрация производятся
с помощью sql-запроса:

```sql
    select * from (
    select 
    case when month in (11, 12, 1) and shirota > 0 
            or month in (5, 6, 7) and shirota < 0 then 'зима'
        when month in (2, 3, 4) and shirota > 0
            or month in (8, 9, 10) and shirota < 0 then 'весна'
        when month in (5, 6, 7) and shirota > 0 
            or month in (11, 12, 1) and shirota < 0 then 'лето'
        when month in (8, 9, 10) and shirota > 0
            or month in (2, 3, 4) and shirota < 0 then 'осень'
    end season
    , case when abs(shirota) > 60 then 'полярные'
          when abs(shirota) < 30 then 'экваториальные'
         else 'средние'
    end region
    , case when F107 < 100 then 'низкаяСА'
        when F107 > 150 then 'высокаяСА'
        else 'средняяСА'
    end F107
    , case when SZA < 60 then 'день'
        when SZA > 100 then 'ночь'
        else 'сумерки'
    end SZA
    {%- for col_name in column_names %}
    , {{col_name}}
    {%- endfor %}
    from summary
    ) t where {{filter_query}}
```

### Класс KdeBuilder

```python
class KdeBuilder:
    """
    Класс для визуализации данных
    """

    def __init__(self, mat_file, param, **kwargs):
```
При инициализации передаются параметры:
* `mat_file` - путь к файлу с исходными данными
* `param` - что рассчитываем (`Temperature` или `M`)
* `**kwargs` - значения `season`, `region`, `SZA` и `F107` , если по ним нужен отбор

Во время инициализации создается датасет из файла.

Для построения графика необходимо вызвать метод `create_plot`

```python
    def create_plot(self, file, x_label=None, y_label='Высота, км'):
        """
        Метод, строящий график
        :param file: куда сохранять файл
        :param x_label: подпись оси x
        :param y_label: подпись оси y
        :return:
        """
```

### Утилита cli.py
Сделана для удобства вызова построения графиков

Вызывается с опциями, соответствующими критериям фильтра.

```sh
usage: cli.py [OPTIONS] PARAM
```

`PARAM` - `T` или `M` в зависимости от того, что мы хотим рассчитать

`OPTIONS`:

|Опция| возможные значения |
|-----|------|
|--season|лето, зима, осень, весна|
|--region|экваториальные, средние, полярные|
|--sza|день, ночь, сумерки|
|--f107|низкаяСА, высокаяСА, средняяСА|
 
_Примеры:_

* Построеение графика плотности вероятности температуры нейтралов летом в полярных широтных, днем, при низкой солнечной активности

```sh 
$ python3 cli.py T --season лето --region полярные --sza день --f107 низкаяСА
```

* Построение графика плотности вероятности концентрации нейтралов зимой в средних широтах (для всех времен суток и СА):

```shell 
$ python3 cli.py M --season зима --region средние
```

**График сохраняется в директории `images` c названием**
```python 
f'images/{param}-{"-".join([value for value in kwargs.values() if value])}.png'
```
## Исходные данные
Наблюдения со спутника AURA лежат в файле `data/data.mat`

Также в папке `data` лежат эти данные в текстовом виде

Изобразим распределения данных по _сезонам, регионам, временам суток и солнечной активности_:

```shell script
$ python3 python_code/create_data_hist.py --param season
$ python3 python_code/create_data_hist.py --param region
$ python3 python_code/create_data_hist.py --param SZA
$ python3 python_code/create_data_hist.py --param F107
```

![](images/data_season.png)
![](images/data_region.png)
![](images/data_SZA.png)
![](images/data_F107.png)
## Распределение плотностей вероятностей T и M от условий
В этом разделе будем строить распределения плотности вероятности T и десятичного логарифма M и графики зависимостей
среднего и наиболее вероятного значения этих параметров от высоты h при различных гелиофизических условиях,
а так же графики зависимостей этих величин от гелиофизических условий.

На иллюстрациях этого раздела слева будут изображены распределения плотности вероятности величины,
нормированной на максимальное значение, а справа - графики среднего и наиболее
вероятного значения величины.

### Зависимость от солнечной активности
Рассмотрим, как изменится распределение вероятности температуры нейтралов летним днем в экваториальных широтах 
в зависимости от солнечной активности:

![](images/by_h/T-лето-экваториальные-день-высокаяСА.png)
![](images/by_h/T-лето-экваториальные-день-низкаяСА.png)

Дисперсия значений при высокой СА больше, чем при низкой. Возможно, это связано с меньшим количеством наблюдений.
Тем не менее, наиболее вероятные значения близки к средним (в переделах 0.8%).

Сравним еще распределения летним днем в средних широтах:

![](images/by_h/T-лето-средние-день-высокаяСА.png)
![](images/by_h/T-лето-средние-день-низкаяСА.png)

Снова разброс значений при высокой СА больше, чем при низкой, однако, в данном случае средние величины сильнее отличаются
от вероятных, чем в предыдущем (в пределах 2%).

Построим зависимость распределения температуры нейтралов от солнечной активности
(например, на высоте h= 50 км):
![](images/by_f107/T50-лето-экваториальные-день.png)
![](images/by_f107/T50-лето-средние-день.png)

Для обоих регионов наблюдается минимум при f107 около 140, с отклонением значения примерно на 8%.
Исключая этот минимум, колебания температуры не более 2%.

Для низкой солнечной активности значения колеблются в пределах 1,2%.


Теперь построим в этих же условиях распределение плотности вероятности концентрации нейтралов:

![](images/by_h/M-лето-экваториальные-день-высокаяСА.png)
![](images/by_h/M-лето-экваториальные-день-низкаяСА.png)

![](images/by_h/M-лето-средние-день-высокаяСА.png)
![](images/by_h/M-лето-средние-день-низкаяСА.png)

При высокой СА дисперсия значений больше, чем при низкой. При этом, во всех случаях наиболее вероятные
значения практически совпадают со средними (отклонение десятичного логарифма менее 0.1).

Построим зависимость распределения концентрации нейтралов
от солнечной активности:

![](images/by_f107/M80-зима-экваториальные-ночь.png)
![](images/by_f107/M50-лето-полярные-сумерки.png)

Колебания концентрации не значительны (отклонение десятичного логарифма менее 0.05).

_При высокой солнечной активности разброс значений T и M гораздо больше, чем при низкой. Кроме того, для высокой СА
мы имеем небольшое количество наблюдений. Поэтому в следующих экспериментах будем выбирать значения при низкой СА._


### Зависимость от времени суток
Наиболее показательным примером будет рассмотреть распределения величин ночью и днем 
в экваториальных широтах в межсезонье, так как день примерно равен ночи, и на экваторе 
наблюдается наибольший разброс значений зенитных углов.

![](images/by_h/T-осень-экваториальные-день-низкаяСА.png)
![](images/by_h/T-осень-экваториальные-ночь-низкаяСА.png)

Ночью разброс значений больше, чем днем. Ночью средние температуры отклоняются от наиболее вероятных в пределах 0.8%,
а днем в пределах 0.7%.

Построим зависимости распределения температуры нейтралов 
от зенитного угла:

![](images/by_sza/T60-осень-полярные-низкаяСА.png)
![](images/by_sza/T85-зима-средние-низкаяСА.png)
![](images/by_sza/T85-осень-экваториальные-низкаяСА.png)

Эти графики показывают, что существует зависимость температуры от зенитного угла (колебания значений около 10%).

На этих же данных посмотрим распределение вероятности концентрации нейтралов

![](images/by_h/M-осень-экваториальные-день-низкаяСА.png)
![](images/by_h/M-осень-экваториальные-ночь-низкаяСА.png)

Осенью на экваторе наиболее вероятные значения M совпадают со средними (прямые десятичного логарифма 
накладываются друг на друга. При этом, 
наблюдается, что дисперсия значений растет при увеличении высоты как днем, так и ночью.

Построим зависимость распределения концентрации нейтралов от зенитного угла

![](images/by_sza/M60-осень-полярные-низкаяСА.png)
![](images/by_sza/M80-лето-средние-низкаяСА.png)
![](images/by_sza/M80-лето-экваториальные-низкаяСА.png)

Наблюдается незначительная зависимость наиболее вероятной концентрации от зенитного угла в пределах одного порядка 
(отклонения десятичного логарифма не более 0.2)

Резкий разрыв на экваторе в районе зенитного угла в 90 градусов объясняется тем, что на экваторе сумерки
продолжаются недолго, и при зенитных углах около 90 имеем малое количество наблюдений.


### Зависимость от широты
Построим распределение плотности вероятности температуры нейтралов в летний день
при низкой СА для экваториальных, средних и полярных широт

![](images/by_h/T-лето-экваториальные-день-низкаяСА.png)
![](images/by_h/T-лето-средние-день-низкаяСА.png)
![](images/by_h/T-лето-полярные-день-низкаяСА.png)

Заметим, что дисперсия значений температуры наибольшая в средних широтах, а
различия в распределениях для разных регионов видны невооруженным взглядом.

В средних широтах наблюдается наибольшее отклонение средней температуры от наиболее вероятной.

Построим распределение температуры нейтралов от широты:

![](images/by_latitude/T55-лето-день-низкаяСА.png)
![](images/by_latitude/T70-весна-день-низкаяСА.png)
![](images/by_latitude/T85-зима-ночь-низкаяСА.png)

Зависимость температуры от широты существует (колебания значений в пределах 8%).

Для распределения плотности вероятности концентрации нейтралов:

![](images/by_h/M-лето-экваториальные-день-низкаяСА.png)
![](images/by_h/M-лето-средние-день-низкаяСА.png)
![](images/by_h/M-лето-полярные-день-низкаяСА.png)

Разброс значений концентрации нейтралов так же наибольший в средних широтах.

Наиболее вероятные значения концентрации совпадают с наиболее вероятными в экваториальных и полярных широтах,
но в средних широтах все же различаются, хоть и не существенно (отклонения десятичного логарифма менее 0.1.

Зависимости концентрации от широты:

![](images/by_latitude/M55-лето-день-низкаяСА.png)
![](images/by_latitude/M70-весна-день-низкаяСА.png)
![](images/by_latitude/M85-зима-ночь-низкаяСА.png)

Зависимость концентрации нейтралов от широты незначительна, в пределах одного порядка (колебания десятичного логарифма 
в пределах 0.2).

### Зависимость от сезона
Сравним распределения по четырем сезонам в средних широтах:

![](images/by_h/T-зима-средние-день-низкаяСА.png)
![](images/by_h/T-лето-средние-день-низкаяСА.png)
![](images/by_h/T-осень-средние-день-низкаяСА.png)
![](images/by_h/T-весна-средние-день-низкаяСА.png)

Видим различия в распределениях. Заметим, что весной в межсезонье разница между средней и наиболее вероятной 
температурой достигает 3%.

Построим зависимость распределения температуры от месяца в северном полушарии:

![](images/by_month/T50-экваториальные-день-низкаяСА.png)
![](images/by_month/T75-средние-день-низкаяСА.png)
![](images/by_month/T85-полярные-сумерки-низкаяСА.png)

Наблюдается зависимость температуры нейтралов от сезона (в пределах 8%).

Проверим сезонную зависимость распределения плотности концентрации нейтралов:



![](images/by_h/M-зима-средние-день-низкаяСА.png)
![](images/by_h/M-лето-средние-день-низкаяСА.png)
![](images/by_h/M-осень-средние-день-низкаяСА.png)
![](images/by_h/M-весна-средние-день-низкаяСА.png)

Опять же, летом и зимой разброс больше, чем в межсезонье.

Зависимость концентрации от месяца:

![](images/by_month/M50-экваториальные-день-низкаяСА.png)
![](images/by_month/M75-средние-день-низкаяСА.png)
![](images/by_month/M85-полярные-сумерки-низкаяСА.png)

Наблюдается незначительная зависимость концентрации нейтралов от времени года в пределах одного порядка 
(колебания десятичного логарифма менее 0.2)

## Сравнение рассчитанных значений со значениями модели MSIS

Сравним средние и наиболее вероятные значения T и M, рассчитанные на основании данных со спутника,
 со значениями модели MSIS:
 
![](images/msis/T-зима-средние-день-низкаяСА.png)
![](images/msis/T-лето-экваториальные-ночь-низкаяСА.png)
![](images/msis/M-зима-средние-день-низкаяСА.png)
![](images/msis/M-лето-экваториальные-ночь-низкаяСА.png)

Заметим, что модель температуры MSIS отличается от рассчитанной на значениях со спутника не только количественно, 
но и качественно.

Для концентрации модель совпадает с рассчитанной качественно, однако, количественно отличается на 13 порядков.
## Выводы 
1.  
    - Распределение **температуры** нейтралов зависит от зенитного угла (разброс значений до 10%), а также от
    широты, времени года и солнечной активности (разброс значений в пределах 8%).
    - Наблюдается незначительная зависимость **концентрации** в пределах одного порядка от широты, времени года и
    зенитного угла (колебания десятичного логарифма менее 0.2), а зависимость значений концентрации от солнечной активности
    пренебрежительно мала (колебания десятичного логарифма меенее 0.05)
2.
    - Различие значений средней и наиболее вероятной **температуры** нейтралов при некоторых гелиофизических условиях
    достигает 3%,
    следовательно, необходим переход к вероятностным характеристикам.
    - Средние значения **концентрации** нейтралов близки к наиболее вероятным (в средних широтах различия десятичных 
     логарифмов менее 0.1, а в полярных и экваториальных широтах графики логарифмов накладываются друг на друга), 
     следовательно, переход к вероятностным характеристикам не критичен.
3.  Рассчитанные M на данных со спутника отличаются от модели MSIS на 13 порядков, а модель T отличается от данных со спутника
 не только количественно, но и качественно, из чего можно сделать вывод, что модель MSIS 
 неприменима для решения задач моделирования ионосферных слоев. 
