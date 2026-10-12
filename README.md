# PG Robotics PWA

Flutter приложение PG Robotics v0.6 для iPhone и установки по HTTPS-ссылке на iPhone/Android. GitHub Actions собирает проект и публикует его через GitHub Pages.

## Публикация первой версии

1. Загрузите архив `PG_Robotics_v0.6_GitHub_Pages_Ready.zip` **в корень этого репозитория**: **Add file → Upload files → Commit changes**.
2. Откройте **Settings → Pages → Build and deployment → Source** и выберите **GitHub Actions**.
3. Перейдите во вкладку **Actions** и дождитесь успешного выполнения `Build and publish PG Robotics Flutter PWA`.
4. После зелёной сборки откройте https://alekseimasslij-art.github.io/pg-robotics-pwa/.

Workflow извлекает исходный Flutter-проект, запускает Flutter Web release build и публикует полученную папку `build/web`. У архива должны быть именно это имя и путь. ZIP содержит приложение, локальную новостную ленту и игру «Місія»; реальные push-уведомления не включены.

_Ссылка станет рабочей только после успешной сборки и настройки GitHub Pages._
