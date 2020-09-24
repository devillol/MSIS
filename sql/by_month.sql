select y, value from (
    select
    month as y
    , case when abs(latitude) > 60 then 'полярные'
          when abs(latitude) < 30 then 'экваториальные'
         else 'средние'
    end region
    , case when F107 < 100 then 'низкаяСА'
        when F107 > 150 then 'высокаяСА'
        else 'средняяСА'
    end F107
    , case when SZA < 60 then 'день'
        when SZA > 100 then 'ночь'
        else 'сумерки'
    end SZA , round({{column_names[0]}}, {{n_round}}) as value
    from summary
    where latitude > 0
) t
where {{filter_expr}}