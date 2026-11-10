# Device QA — Family Hub (после W0–W5)

**Сборка / Simulator / Device — только после фразы владельца «GO на сборку».**

## Hub «Где семья» (Where Is Phone)

1. Таббар: Местоположение / Вождение / Безопасность / Подписка — New York, читаемо на Calm Navy.  
2. Заголовки + описания sheets — serif.  
3. Motion: при открытии Вождение запрашивается; empty честный.  
4. FAB / карта / share copy — без «шаринг».

## Вождение (Drive)

1. Селектор члена семьи переключает данные.  
2. Период: сегодня / неделя / месяц.  
3. Stats и список поездок = реальные (ledger), не fake 14/58.  
4. PDF Share: имя + период + строки поездок.  
5. Чужой член без поездок → empty other_member.

## SimpleHome (W4)

1. Три двери: title + subtitle serif.  
2. Family access card — serif title/body.

## Parental / Child / Dashboard (W5)

1. Parental: секции «Выберите ребёнка», «Родительский контроль», achievements — serif headers.  
2. Parent Dashboard: главный title + section titles serif.  
3. Child: greeting / what to do / companions / wellness entry — serif titles + captions.

## Trial / слоты (W-pre)

1. На Main: trial → «ПРОБНЫЙ» + N из 3 (не БАЗОВЫЙ + 2 из 3).  
2. Confirm при уходе на БАЗОВЫЙ во время trial.

## Не закрывать QA как 100% без

- Скрин/прогон на устройстве или симе после **GO на сборку**.  
- Grep plan↔fact по `AladdinFamilyType` в затронутых файлах.
