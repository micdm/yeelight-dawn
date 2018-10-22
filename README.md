Модуль miio.py взят у https://github.com/OpenMiHome/mihome-binary-protocol, за что им и спасибо.

### Активация лампочки
`python -m lib.activate [ssid] [password]`

### Эмуляция рассвета
`python -m lib.dawn 07:00:00 10 192.168.1.10 --immediately`

### Запуск тестов
`pytest test --cov lib`
