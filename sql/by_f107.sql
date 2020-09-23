select y, value from (
    select
    cast(10 * round(F107/10) as int ) as y
    , case when abs(latitude) > 60 then 'полярные'
          when abs(latitude) < 30 then 'экваториальные'
         else 'средние'
    end region
    , case when month in (11, 12, 1) and latitude > 0
            or month in (5, 6, 7) and latitude < 0 then 'зима'
        when month in (2, 3, 4) and latitude > 0
            or month in (8, 9, 10) and latitude < 0 then 'весна'
        when month in (5, 6, 7) and latitude > 0
            or month in (11, 12, 1) and latitude < 0 then 'лето'
        when month in (8, 9, 10) and latitude > 0
            or month in (2, 3, 4) and latitude < 0 then 'осень'
    end season
    , case when SZA < 60 then 'день'
        when SZA > 100 then 'ночь'
        else 'сумерки'
    end SZA , round({{column_names[0]}}, {{n_round}}) as value
    from summary
) t
where {{filter_expr}}