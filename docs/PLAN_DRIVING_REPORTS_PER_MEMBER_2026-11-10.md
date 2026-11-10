# Driving reports — per member (канон после оболочки)

**Дата:** 2026-11-10  

## Как должно работать (Life360-уровень, без лжи)

1. **Запись поездки** на устройстве члена семьи (auto GPS motion или Start/End).  
2. **Ledger** `FamilyDrivingTripLedger` хранит поездку с `userId` / именем.  
3. **Экран Вождение**: селектор члена → период today/week/month → список поездок + stats **из реальных trip**.  
4. **PDF** — Share sheet: имя члена + период + сводка + строки поездок.  
5. **Чужой член без данных** — честный empty, не чужие цифры и не mock.

## Источники

| Источник | Роль |
|----------|------|
| Local ledger | SSOT на телефоне для поездок этого устройства |
| `GET /api/reports/driving?userId&period` | Remote trips (если БД жива) |
| `GET /api/reports/driving/stats` | **Не** primary UI; на MAIN больше без fake 14/58 trips |
| Component analytics `applyFrom` | Отключён как источник правды |

## Ограничения (честно)

- Поездки другого члена видны родителю, только если сервер их отдал **или** тот член синхронизировал их на сервер. Локальный ledger чужого телефона на ваш iPhone сам не «перепрыгивает».  
- Следующий шаг (отдельный GO): push trip на MAIN при `finalize` + family sync.

## W3 serif

FamilySafetyRemainderHub sheets — New York через `AladdinFamilyType`.
