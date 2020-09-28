python3 cli.py M --season лето --region полярные --sza день --f107 низкаяСА
python3 cli.py M --season лето --region поолярные --sza день --f107 высокаяСА
python3 cli.py M --season лето --region средние --sza день --f107 высокаяСА
python3 cli.py M --season лето --region средние --sza день --f107 низкаяСА
python3 cli.py M --season лето --region средние --sza ночь --f107 низкаяСА
python3 cli.py M --season лето --region экваториальные --sza ночь --f107 низкаяСА
python3 cli.py M --season лето --region экваториальные --sza ночь --f107 высокаяСА
python3 cli.py M --season лето --region экваториальные --sza день --f107 высокаяСА
python3 cli.py M --season лето --region экваториальные --sza день --f107 низкаяСА
python3 cli.py M --season осень --region средние --sza день --f107 низкаяСА
python3 cli.py M --season осень --region экваториальные --sza ночь --f107 низкаяСА
python3 cli.py M --season осень --region экваториальные --sza день --f107 низкаяСА
python3 cli.py M85 -y latitude --season зима --sza ночь --f107 низкаяСА
python3 cli.py M70 -y latitude --season весна --sza день --f107 низкаяСА
python3 cli.py M55 -y latitude --season лето --sza день --f107 низкаяСА

python3 cli.py M85 -y month --region полярные --sza сумерки --f107 низкаяСА
python3 cli.py M75 -y month --region средние --sza день --f107 низкаяСА
python3 cli.py M50 -y month --region экваториальные --sza день --f107 низкаяСА
python3 cli.py M60 -y sza --season осень --region полярные --f107 низкаяСА
python3 cli.py M80 -y sza --season лето --region средние --f107 низкаяСА
python3 cli.py M80 -y sza --season лето --region экваториальные --f107 низкаяСА

python3 cli.py M50 -y f107 --season лето --region полярные --sza сумерки
