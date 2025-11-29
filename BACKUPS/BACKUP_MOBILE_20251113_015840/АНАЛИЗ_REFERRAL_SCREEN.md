# Анализ ReferralScreen.swift - все строки для локализации

## Список всех прямых строк (50+ строк):

1. "Фон экрана реферальной программы" (accessibilityLabel)
2. "Реферальная программа" (accessibilityLabel)
3. "РЕФЕРАЛЬНАЯ ПРОГРАММА" (title)
4. "Приглашай друзей - получай бонусы" (subtitle)
5. "Навигационная панель реферальной программы" (accessibilityLabel)
6. "Подарок" (accessibilityLabel)
7. "Пригласи друзей" (Text)
8. "Вы и друг получите -20% скидку на 1 месяц" (Text)
9. "Пригласить друзей" (Button)
10. "ВАША СТАТИСТИКА" (Text)
11. "Приглашено" (title)
12. "Оплатили" (title)
13. "До 30%" (title)
14. "Прогресс до скидки 30%" (Text)
15. "Осталось пригласить: \(3 - paidReferralsCount)" (Text с параметрами)
16. "Вы достигли скидки 30%!" (Text)
17. "Прогресс до 1 месяца бесплатно" (Text)
18. "Осталось: \(10 - paidReferralsCount)" (Text с параметрами)
19. "Вы получили 1 месяц бесплатно!" (Text)
20. "ВАШ РЕФЕРАЛЬНЫЙ КОД" (Text)
21. "Скопировать код" (accessibilityLabel)
22. "Реферальный код: \(referralCode)" (accessibilityLabel с параметрами)
23. "Копировать" (Button)
24. "QR код" (Button)
25. "Показать QR код" (accessibilityLabel)
26. "КАК ЭТО РАБОТАЕТ" (Text)
27. "3 простых шага к бонусам" (subtitle)
28. "Поделитесь кодом" (title)
29. "Отправьте ваш реферальный код друзьям через WhatsApp, Telegram, VK или другие мессенджеры" (description)
30. "Друг регистрируется" (title)
31. "Друг использует ваш код при регистрации в ALADDIN и оформит любую платную подписку в течение 6 месяцев" (description)
32. "Получите бонусы" (title)
33. "Вы и друг получаете -20% скидку на 1 месяц! При 3 оплатах → -30% для вас! При 10 оплатах → 1 месяц бесплатно!" (description)
34. "СПОСОБЫ ПРИГЛАШЕНИЯ" (Text)
35. "WhatsApp" (title)
36. "Открыть WhatsApp" (subtitle)
37. "Telegram" (title)
38. "Открыть Telegram" (subtitle)
39. "VK" (title)
40. "Открыть VK" (subtitle)
41. "Еще способы" (title)
42. "Открыть системный шар" (subtitle)
43. "Копировать ссылку" (title)
44. "Скопировать приглашение" (subtitle)
45. "Копировать код" (title)
46. "Скопировать только код" (subtitle)
47. "QR код" (title)
48. "Показать QR код" (subtitle)
49. "НАГРАДЫ" (Text)
50. "Все награды" (Button)
51. "Показать все награды" (accessibilityLabel)
52. "1 оплата" (title)
53. "-20%" (reward)
54. "Вам + другу" (subtitle)
55. "3 оплаты" (title)
56. "-30%" (reward)
57. "Ваша скидка" (subtitle)
58. "10 оплат" (title)
59. "1 месяц" (reward)
60. "Бесплатно" (subtitle)
61. "разблокировано" / "заблокировано" (accessibilityLabel)
62. "ИСТОРИЯ РЕФЕРАЛОВ" (Text)
63. "Реферал #1", "Реферал #2", "Реферал #3" (name - в данных)
64. "2 дня назад", "1 неделя назад", "2 недели назад" (date - в данных)
65. "Ожидает" (reward - в данных)
66. "Завершено", "В ожидании", "Отменено" (ReferralStatus)
67. "QR код" (QRCodeView)
68. "Все награды" (RewardsView)
69. "Оплативших друзей: \(paidReferralsCount)" (RewardsView с параметрами)
70. "🎁 Присоединяйся к ALADDIN! Мы оба получим скидку -20% на 1 месяц после тестового периода!\n\nИспользуй мой код: \(referralCode)\n\nСкачай: https://aladdin.family/invite/\(referralCode)\n\nС тобой на защите! 🛡️" (referralText - длинный текст)

## Ключи для создания (префикс referral_):

referral_background
referral_title
referral_subtitle
referral_nav_accessibility
referral_gift_icon
referral_invite_friends_title
referral_invite_friends_desc
referral_invite_button
referral_stats_title
referral_stats_invited
referral_stats_paid
referral_stats_discount
referral_progress_30_title
referral_progress_30_remaining
referral_progress_30_achieved
referral_progress_month_title
referral_progress_month_remaining
referral_progress_month_achieved
referral_code_title
referral_code_copy_accessibility
referral_code_accessibility
referral_copy_button
referral_qr_button
referral_qr_show_accessibility
referral_how_it_works_title
referral_how_it_works_subtitle
referral_step1_title
referral_step1_desc
referral_step2_title
referral_step2_desc
referral_step3_title
referral_step3_desc
referral_methods_title
referral_method_whatsapp
referral_method_whatsapp_subtitle
referral_method_telegram
referral_method_telegram_subtitle
referral_method_vk
referral_method_vk_subtitle
referral_method_more
referral_method_more_subtitle
referral_method_copy_link
referral_method_copy_link_subtitle
referral_method_copy_code
referral_method_copy_code_subtitle
referral_method_qr
referral_method_qr_subtitle
referral_rewards_title
referral_rewards_all
referral_rewards_all_accessibility
referral_reward_1_title
referral_reward_1_amount
referral_reward_1_subtitle
referral_reward_3_title
referral_reward_3_amount
referral_reward_3_subtitle
referral_reward_10_title
referral_reward_10_amount
referral_reward_10_subtitle
referral_unlocked
referral_locked
referral_history_title
referral_status_completed
referral_status_pending
referral_status_cancelled
referral_qr_view_title
referral_rewards_view_title
referral_rewards_view_subtitle
referral_text_template


