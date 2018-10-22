Модуль miio.py взят у https://github.com/OpenMiHome/mihome-binary-protocol, за что им и спасибо.  
Функция `encrypt()` подправлена: теперь она более универсальная, и принимает Device ID.

### Активация лампочки
Пустить лампочку в домашнюю WiFi-сеть можно и без официального приложения.  
`python -m lib.activate [ssid] [password]`

### Эмуляция рассвета
Указываем время начала, длительность в минутах, адрес лампочки в домашней сети.  
`python -m lib.dawn 07:00:00 10 192.168.1.10 --immediately`

### Тесты
`pytest test --cov lib`
