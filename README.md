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
### Зависимость от солнечной активности
Рассмотрим, как изменится распределение вероятности **температуры** нейтралов летним днем в экваториальных широтах 
в зависимости от солнечной активности:

![](images/by_h/T-лето-экваториальные-день-высокаяСА.png)
![](images/by_h/T-лето-экваториальные-день-низкаяСА.png)

Можно заметить, что здесь **среднее значение температуры от солнечной активности практически не зависит**.
Однако, можем заметить, что при высокой солнечной активности разброс значений больше

Сравним еще распределения летним днем в средних широтах:

![](images/by_h/T-лето-средние-день-высокаяСА.png)
![](images/by_h/T-лето-средние-день-низкаяСА.png)

Наблюдаем аналогичную картину: средние значения при высокой и низкой СА расходятся не
значительно, но разброс значений при высокой СА больше, чем при низкой

Теперь построим в этих же условиях распределение плотности вероятности **концентрации нейтралов**:

![](images/by_h/M-лето-экваториальные-день-высокаяСА.png)
![](images/by_h/M-лето-экваториальные-день-низкаяСА.png)

![](images/by_h/M-лето-средние-день-высокаяСА.png)
![](images/by_h/M-лето-средние-день-низкаяСА.png)

Можно заметить, что
**распределение плотности вероятности концентрации нейтралов от солнечной активности зависит несущественно**

>**_Вывод:_**  
>* распределение P(M) от солнечной активности практически не зависит
>* среднее значение T от солнечной активности зависит не существенно, однако,
>вероятностное распределение P(T) немного меняется в зависимости от СА


### Зависимость от времени суток
Так как была выявлена зависимость распределения плотности вероятности температуры от солнечной активности,
необходимо снова проверять зависимость распределения плотности вероятности температуры от времени суток 
при замороженных  остальных параметрах. Больше всего наблюдений летом на экваторе 
при низкой СА, при этих параметрах и будем проверять:

![](images/by_h/T-лето-экваториальные-день-низкаяСА.png)
![](images/by_h/T-лето-экваториальные-ночь-низкаяСА.png)

В обоих случаях количество наблюдений большое, и картинки наблюдаются схожие

На этих же данных посмотрим распределение вероятности концентрации нейтралов

![](images/by_h/M-лето-экваториальные-день-низкаяСА.png)
![](images/by_h/M-лето-экваториальные-ночь-низкаяСА.png)

Можно заметить, что на высотах h > 75 км ночью разброс значений чуть больше, чем днем, 
но отличия не существенны

>**_Вывод:_**  
>Распределения P(T) и P(M) от времени суток зависят не существенно

### Зависимость от широты
Построим распределение плотности вероятности температуры нейтралов в летний день
при низкой СА для экваториальных, средних и полярных широт

![](images/by_h/T-лето-экваториальные-день-низкаяСА.png)
![](images/by_h/T-лето-средние-день-низкаяСА.png)
![](images/by_h/T-лето-полярные-день-низкаяСА.png)

Видно, что разброс значений температуры возрастает при приближении к полярным широтам.
Причем от региона зависят и средние значения температуры

Для распределения плотности вероятности концентрации нейтралов:
![](images/by_h/M-лето-экваториальные-день-низкаяСА.png)
![](images/by_h/M-лето-средние-день-низкаяСА.png)
![](images/by_h/M-лето-полярные-день-низкаяСА.png)

Разброс значений концентрации нейтралов так же увеличивается при приближении к 
полярным широтам. Меняются и средние значения M

>**_Вывод:_**  
>Распределения P(T) и P(M) зависят от широты

### Зависимость от сезона
Рассмотрим зиму и лето в полярных широтах при низкой СА (время суток опустим, так как в
этих широтах все лето и всю зиму время суток не меняется, да и выше было доказано, что от
времени суток распределения практически не зависят):

![](images/by_h/T-зима-полярные-низкаяСА.png)
![](images/by_h/T-лето-полярные-низкаяСА.png)

Сезонная зависимость температуры ярко выражена.

Проверим еще для четырех времен года в средних широтах:

![](images/by_h/T-зима-средние-низкаяСА.png)
![](images/by_h/T-лето-средние-низкаяСА.png)
![](images/by_h/T-осень-средние-низкаяСА.png)
![](images/by_h/T-весна-средние-низкаяСА.png)

Самый большой разброс температур наблюдается зимой, наименьший - летом.

_Этот эксперимент подтверждает так же предыдущее утверждение о широтной зависимости
распределения плотности вероятности температуры (в полярных широтах более заметна
разница между зимним и летним распределением)_

Проверим сезонную зависимость распределения плотности концентрации нейтралов:

![](images/by_h/M-зима-полярные-низкаяСА.png)
![](images/by_h/M-лето-полярные-низкаяСА.png)

Зимой разброс значений больше, чем летом

![](images/by_h/M-зима-средние-низкаяСА.png)
![](images/by_h/M-лето-средние-низкаяСА.png)
![](images/by_h/M-осень-средние-низкаяСА.png)
![](images/by_h/M-весна-средние-низкаяСА.png)

Опять же, наибольший разброс получился зимой, а наименьший - летом.

>**_Вывод:_**  
>Распределения P(T) и P(M) зависят от сезона


