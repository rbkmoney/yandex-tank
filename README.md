С помощью танка можно провести нагрузочное тестирование макросервиса.

Шаги:
1. Поменять в load.ini настройки
    ; Minigun config section:
    [minigun]
    phout=phout.log
    minigun_cmd=./mg
    worker_mod=minigun_worker_api_impl
    ccw=10 ;Concurrent workers
    aps=3 ;Actions per second
    wps=5 ;Workers launching speed (Workers per second)
    session_duration=5000
    total_duration=50000
    auth_url=auth.rbk.test
    auth_port=8080
    auth_name=demo_merchant
    auth_pass=test
    api_url=api.rbk.test
    api_port=8080
2. make wc_build_minigun
3. make test