# Blog
## Описание:
Pet-project Blog. Backend.  
Ключ settings.SECRET_KEY написан в файле .env.  
CRUD для постов, пользователей, комментариев.  
При удалении объектa, данные сохраняются в базе меняя статус на "hidden", и больше не отображаются на экране. Удалить объект можно только через админку.  
Прописана система прав пользователей.  
Ограничен доступ анонимных пользователей.  
Настроена система поиска постов.  
Настроена система тегов с помощью TaggableManager.  
Стандартная регистрация и аутентификация, добавлена возможность восстанавливать страницу.  
Прописан API, аутентификация по jwt-токену.  
API покрыт тестами APITestCase.  
Проект покрыт тестами django.TestCase.  
## Запуск
Откройте пустую папку в своей программе разработки(PyCharm, VSCode и пр.) 
Откройте терминал, создайте среду разработки (`pip install virtualenv` =>> `python -m venv env` =>> `. env/bin/activate`, если ОС `windows` - `. env/Scripts/activate`). После этого должна появится надпись `(env)` над строкой в терминале.  
Дальше впишите команду `https://github.com/RomanInBar/Blog.git` для клонирования репозитория. 
Установите зависимости `pip install -r requirements.txt`.  
В папке lesson_2_3 создайте файл `.env`, напишите в нём: SECRET_KEY = key (key - это секретный ключ проекта. Его можно сгенирировать на сайте `https://djecrety.ir/`) 
## API
Написан при использовании JWT-токена, так что поддерживает стандартные эндпоинты.  
`/api/posts/my/` - Посты пользователя  
`/api/posts/1/comments/` - Комментарии к посту  
Натсроена фильтрация, поиск и сортировка объектов.  

# v1.1
Добавлена система лайков с помощью полиморфной связи.  
Добавлена функция подписки на автора.  
Добавлен рейтинг авторов.   
Добавлены функции топ-лист постов и авторов.  
Добавлена возможность добавлять изображения к постам. При загрузке из базы, изображения конвертируются в формат `.webp`.  
Обновлена система восстановления страницы, теперь производится через почту пользователя с помощью `uuid`.   
Проект переведен на базу данных PostgreSQL.  



