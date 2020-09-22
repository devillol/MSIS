# Моделирование нижней геосферы земли
Босинзон Галина, 734 группа
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

![](images/Temperature-лето-экваториальные-день-высокаяСА.png)
![](images/Temperature-лето-экваториальные-день-низкаяСА.png)

Можно заметить, что здесь **среднее значение температуры от солнечной активности практически не зависит**.
Однако, можем заметить, что при высокой солнечной активности разброс значений больше

Сравним еще распределения летним днем в средних широтах:

![](images/Temperature-лето-средние-день-высокаяСА.png)
![](images/Temperature-лето-средние-день-низкаяСА.png)

Наблюдаем аналогичную картину: средние значения при высокой и низкой СА расходятся не
значительно, но разброс значений при высокой СА больше, чем при низкой

Теперь построим в этих же условиях распределение плотности вероятности **концентрации нейтралов**:

![](images/M-лето-экваториальные-день-высокаяСА.png)
![](images/M-лето-экваториальные-день-низкаяСА.png)

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

![](images/Temperature-лето-экваториальные-день-низкаяСА.png)
![](images/Temperature-лето-экваториальные-ночь-низкаяСА.png)

В обоих случаях количество наблюдений большое, и картинки наблюдаются схожие

На этих же данных посмотрим распределение вероятности концентрации нейтралов

![](images/M-лето-экваториальные-день-низкаяСА.png)
![](images/M-лето-экваториальные-ночь-низкаяСА.png)

Можно заметить, что на высотах h > 75 км ночью разброс значений чуть больше, чем днем, 
но отличия не существенны

>**_Вывод:_**  
>Распределения P(T) и P(M) от времени суток зависят не существенно

### Зависимость от широты
Построим распределение плотности вероятности температуры нейтралов в летний день
при низкой СА для экваториальных, средних и полярных широт

![](images/Temperature-лето-экваториальные-день-низкаяСА.png)
![](images/Temperature-лето-средние-день-низкаяСА.png)
![](images/Temperature-лето-полярные-день-низкаяСА.png)

Видно, что разброс значений температуры возрастает при приближении к полярным широтам.
Причем от региона зависят и средние значения температуры

Для распределения плотности вероятности концентрации нейтралов:
![](images/M-лето-экваториальные-день-низкаяСА.png)
![](images/M-лето-средние-день-низкаяСА.png)
![](images/M-лето-полярные-день-низкаяСА.png)

Разброс значений концентрации нейтралов так же увеличивается при приближении к 
полярным широтам. Меняются и средние значения M

>**_Вывод:_**  
>Распределения P(T) и P(M) зависят от широты

### Зависимость от сезона
Рассмотрим зиму и лето в полярных широтах при низкой СА (время суток опустим, так как в
этих широтах все лето и всю зиму время суток не меняется, да и выше было доказано, что от
времени суток распределения практически не зависят):

![](images/Temperature-зима-полярные-низкаяСА.png)
![](images/Temperature-лето-полярные-низкаяСА.png)

Сезонная зависимость температуры ярко выражена.

Проверим еще для четырех времен года в средних широтах:

![](images/Temperature-зима-средние-низкаяСА.png)
![](images/Temperature-лето-средние-низкаяСА.png)
![](images/Temperature-осень-средние-низкаяСА.png)
![](images/Temperature-весна-средние-низкаяСА.png)

Самый большой разброс температур наблюдается зимой, наименьший - летом.

_Этот эксперимент подтверждает так же предыдущее утверждение о широтной зависимости
распределения плотности вероятности температуры (в полярных широтах более заметна
разница между зимним и летним распределением)_

Проверим сезонную зависимость распределения плотности концентрации нейтралов:

![](images/M-зима-полярные-низкаяСА.png)
![](images/M-лето-полярные-низкаяСА.png)

Зимой разброс значений больше, чем летом

![](images/M-зима-средние-низкаяСА.png)
![](images/M-лето-средние-низкаяСА.png)
![](images/M-осень-средние-низкаяСА.png)
![](images/M-весна-средние-низкаяСА.png)

Опять же, наибольший разброс получился зимой, а наименьший - летом.

>**_Вывод:_**  
>Распределения P(T) и P(M) зависят от сезона