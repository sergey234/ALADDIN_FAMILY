# 📝 ПЕРЕВОД GUIDELINE 3.1.1 ОТ APPLE

**Дата:** 7 декабря 2025  
**Оригинал:** Guideline 3.1.1 - Business - Payments - In-App Purchase

---

## 🇬🇧 ОРИГИНАЛЬНЫЙ ТЕКСТ (АНГЛИЙСКИЙ)

Guideline 3.1.1 - Business - Payments - In-App Purchase

We noticed that your app includes or accesses paid digital content, services, or functionality by means other than in-app purchase, which is not appropriate for the App Store. Specifically:

- Your app accesses digital content purchased outside the app, such as subscription, but that content isn't available to purchase using in-app purchase.

Apps on the United States storefront may link out to the default browser, using buttons, external links, or other calls to action, for payment mechanisms other than in-app purchase. To learn more, see the News post on Apple Developer. For storefronts where there are not alternative options for qualifying apps, the app must use in-app purchase.

Next Steps

The paid digital content, services, or subscriptions included in or accessed by your app must be available for purchase in the app using only in-app purchase.

Apps that offer paid digital services and content across multiple platforms may allow customers to access the content they acquired outside the app as long as it is also available for purchase using in-app purchase. See Guideline 3.1.3(b) Multiplatform Services for more information.

If you have any additional information to provide regarding the digital content and services in your app and how the guidelines apply to them, please reply to this message in App Store Connect and let us know. If there is information you'd like us to consider in our review of future submissions, please feel free to include it in the App Review Information section of App Store Connect.

Resources

- See how to implement in-app purchase with the StoreKit framework.
- Review step-by-step instructions for creating in-app purchases in App Store Connect.
- Learn more about our policies for apps that offer paid digital content and services.

---

## 🇷🇺 ДОСЛОВНЫЙ ПЕРЕВОД (РУССКИЙ)

Руководство 3.1.1 - Бизнес - Платежи - Покупки в приложении

Мы заметили, что ваше приложение включает или получает доступ к платному цифровому контенту, услугам или функциональности средствами, отличными от покупки в приложении, что не соответствует правилам App Store. Конкретно:

- Ваше приложение получает доступ к цифровому контенту, купленному вне приложения, например, подписке, но этот контент недоступен для покупки с использованием покупки в приложении.

Приложения в магазине Соединенных Штатов могут ссылаться на браузер по умолчанию, используя кнопки, внешние ссылки или другие призывы к действию, для механизмов оплаты, отличных от покупки в приложении. Чтобы узнать больше, см. новостной пост на Apple Developer. Для магазинов, где нет альтернативных вариантов для соответствующих приложений, приложение должно использовать покупку в приложении.

Следующие шаги

Платное цифровое содержимое, услуги или подписки, включенные в приложение или доступные через него, должны быть доступны для покупки в приложении только с использованием покупки в приложении.

Приложения, предлагающие платные цифровые услуги и контент на нескольких платформах, могут позволить клиентам получать доступ к контенту, приобретенному вне приложения, при условии, что он также доступен для покупки с использованием покупки в приложении. См. Руководство 3.1.3(b) Мультиплатформенные сервисы для получения дополнительной информации.

Если у вас есть дополнительная информация о цифровом контенте и услугах в вашем приложении и о том, как применяются правила, пожалуйста, ответьте на это сообщение в App Store Connect и дайте нам знать. Если есть информация, которую вы хотели бы, чтобы мы рассмотрели при проверке будущих отправок, пожалуйста, не стесняйтесь включить ее в раздел App Review Information в App Store Connect.

Ресурсы

- См. как реализовать покупку в приложении с помощью фреймворка StoreKit.
- Просмотрите пошаговые инструкции по созданию покупок в приложении в App Store Connect.
- Узнайте больше о наших политиках для приложений, предлагающих платный цифровой контент и услуги.

---

## 📊 КЛЮЧЕВЫЕ МОМЕНТЫ

### Суть проблемы:
- Приложение получает доступ к подпискам, купленным на сайте
- Эти подписки НЕ доступны для покупки через IAP в приложении

### Требование Apple:
- ВСЕ платные подписки должны быть доступны для покупки через IAP в приложении
- Исключение: Мультиплатформенные сервисы (Guideline 3.1.3(b)) - можно активировать подписки, купленные на сайте, НО они также должны быть доступны через IAP

### Для США:
- Можно ссылаться на внешний браузер для оплаты (НО с комиссией 27%)

### Для остальных стран:
- ОБЯЗАТЕЛЬНО использовать IAP

---

**Дата создания:** 07.12.2025

