# 🔍 СРАВНЕНИЕ СЕРВЕРА И РЕПОЗИТОРИЯ

**Дата:** Fri Feb 13 15:40:34 +04 2026  
**Сервер:** root@149.154.65.180  
**Репозиторий:** Локальный

---

## 📊 СТРУКТУРА НА СЕРВЕРЕ

### /opt/aladdin-backend/

### Файлы в /opt/aladdin-backend/
spawn ssh -o StrictHostKeyChecking=no root@149.154.65.180 find /opt/aladdin-backend -maxdepth 1 -type f -name '*.py' 2>/dev/null | sort
root@149.154.65.180's password: 
/opt/aladdin-backend/add_roadside_assistance_to_main.py
/opt/aladdin-backend/analyze_security_system.py
/opt/aladdin-backend/api_gateway_backup_20260201_135150.py
/opt/aladdin-backend/api_gateway_backup_20260202_113209.py
/opt/aladdin-backend/api_gateway_backup_5_20260202_212448.py
/opt/aladdin-backend/api_gateway_backup_6_20260202_212543.py
/opt/aladdin-backend/api_gateway_backup_6_20260202_212556.py
/opt/aladdin-backend/api_gateway_backup_6_20260202_212613.py
/opt/aladdin-backend/api_gateway_backup_7_20260202_212918.py
/opt/aladdin-backend/api_gateway_backup_batch_7_11_20260202_212657.py
/opt/aladdin-backend/api_gateway_backup_before_phishing_fix_final.py
/opt/aladdin-backend/api_gateway_backup_final_1770029572.py
/opt/aladdin-backend/api_gateway_backup_manual.py
/opt/aladdin-backend/api_gateway_backup_pre_prod.py
/opt/aladdin-backend/api_gateway_backup_sync_20260202_213052.py
/opt/aladdin-backend/api_gateway_backup_sync_20260202_213118.py
/opt/aladdin-backend/api_gateway_backup_sync_20260202_213234.py
/opt/aladdin-backend/api_gateway_backup_sync_20260202_213607.py
/opt/aladdin-backend/api_gateway_backup_sync_20260202_213730.py
/opt/aladdin-backend/api_gateway_before_final_complete.py
/opt/aladdin-backend/api_gateway_before_phishing_fix.py
/opt/aladdin-backend/api_gateway_before_security_enhancements.py
/opt/aladdin-backend/api_gateway_before_step1_phishing_sensitivity.py
/opt/aladdin-backend/api_gateway_clean.py
/opt/aladdin-backend/api_gateway_complete_backup_1769965829.py
/opt/aladdin-backend/api_gateway_complete.py
/opt/aladdin-backend/api_gateway_final.py
/opt/aladdin-backend/api_gateway_new.py
/opt/aladdin-backend/api_gateway_old.py
/opt/aladdin-backend/api_gateway_production_final_complete.py
/opt/aladdin-backend/api_gateway.py
/opt/aladdin-backend/api_performance_optimizations.py
/opt/aladdin-backend/api_test_single.py
/opt/aladdin-backend/check_new_agents.py
/opt/aladdin-backend/complete_api_sfm_mapping.py
/opt/aladdin-backend/correct_sfm_count.py
/opt/aladdin-backend/detailed_sfm_analysis.py
/opt/aladdin-backend/final_100_percent_test.py
/opt/aladdin-backend/fix_roadside_assistance_main.py
/opt/aladdin-backend/function_mapping.py
/opt/aladdin-backend/get_all_components_functions.py
/opt/aladdin-backend/gunicorn.conf.py
/opt/aladdin-backend/load_test.py
/opt/aladdin-backend/main_backup_20260212_232347.py
/opt/aladdin-backend/main.py
/opt/aladdin-backend/manual_mark_paid.py
/opt/aladdin-backend/migrate_group3.py
/opt/aladdin-backend/optimizations.py
/opt/aladdin-backend/register_all_agents_in_sfm.py
/opt/aladdin-backend/register_data_cleanup_in_sfm.py
/opt/aladdin-backend/register_roadside_assistance_in_sfm.py
/opt/aladdin-backend/schemas.py
/opt/aladdin-backend/sfm_adapter_backup_before_analytics_fix.py
/opt/aladdin-backend/sfm_adapter_backup_before_available_fix.py
/opt/aladdin-backend/sfm_adapter_backup_before_fix_20260202_234002.py
/opt/aladdin-backend/sfm_adapter_backup_before_real_fix.py
/opt/aladdin-backend/sfm_adapter_before_final_fix_20260203_005120.py
/opt/aladdin-backend/sfm_adapter.py
/opt/aladdin-backend/sfm_adapter_simple_backup_20260202_234306.py
/opt/aladdin-backend/sfm_http_wrapper.py
/opt/aladdin-backend/simple_api.py
/opt/aladdin-backend/start_sfm_core_http.py
/opt/aladdin-backend/test_all_security.py
/opt/aladdin-backend/test_all_security_v2.py
/opt/aladdin-backend/test_api.py
/opt/aladdin-backend/test_fallback.py
/opt/aladdin-backend/test_group1.py
/opt/aladdin-backend/test_sfm.py
/opt/aladdin-backend/test_simple.py

### Директории в /opt/aladdin-backend/
spawn ssh -o StrictHostKeyChecking=no root@149.154.65.180 find /opt/aladdin-backend -maxdepth 1 -type d 2>/dev/null | sort
root@149.154.65.180's password: 
/opt/aladdin-backend
/opt/aladdin-backend/app
/opt/aladdin-backend/data
/opt/aladdin-backend/docs
/opt/aladdin-backend/.git
/opt/aladdin-backend/logs
/opt/aladdin-backend/__pycache__
/opt/aladdin-backend/routers
/opt/aladdin-backend/scripts
/opt/aladdin-backend/security
/opt/aladdin-backend/venv
/opt/aladdin-backend/venvs

### Файлы в /opt/aladdin-backend/app/
spawn ssh -o StrictHostKeyChecking=no root@149.154.65.180 find /opt/aladdin-backend/app -type f -name '*.py' 2>/dev/null | head -50 | sort
root@149.154.65.180's password: 
/opt/aladdin-backend/app/admin_endpoints.py
/opt/aladdin-backend/app/admin_stats.py
/opt/aladdin-backend/app/auth/auth.py
/opt/aladdin-backend/app/auth/__init__.py
/opt/aladdin-backend/app/config.py
/opt/aladdin-backend/app/dashboard_stats.py
/opt/aladdin-backend/app/database/database.py
/opt/aladdin-backend/app/database/__init__.py
/opt/aladdin-backend/app/__init__.py
/opt/aladdin-backend/app/models.py
/opt/aladdin-backend/app/payment_methods.py
/opt/aladdin-backend/app/providers/mock_psp.py
/opt/aladdin-backend/app/rate_limit.py
/opt/aladdin-backend/app/referral_implementation.py
/opt/aladdin-backend/app/referral_payment_functions.py
/opt/aladdin-backend/app/referral_payment_integration.py
/opt/aladdin-backend/app/routers/auth_router.py
/opt/aladdin-backend/app/routers/components.py
/opt/aladdin-backend/app/routers/family.py
/opt/aladdin-backend/app/routers/__init__.py
/opt/aladdin-backend/app/routers/payments.py
/opt/aladdin-backend/app/routers/protection.py
/opt/aladdin-backend/app/routers/referral.py
/opt/aladdin-backend/app/routers/referral_test.py
/opt/aladdin-backend/app/schemas.py
/opt/aladdin-backend/app/utils.py

## 📊 СТРУКТУРА В РЕПОЗИТОРИИ

### Файлы в корне репозитория (api_gateway, роутеры)
./ai_assistant_router.py
./analyze_routers.py
./api_gateway_clean.py
./api_gateway_complete.py
./api_gateway_complete_full.py
./api_gateway_complete_full_v2.py
./api_gateway_current.py
./api_gateway_current_broken.py
./api_gateway_final.py
./api_gateway_final_real.py
./api_gateway_final_v3.py
./api_gateway_fixed.py
./api_gateway_fresh.py
./api_gateway_manual_fix.py
./api_gateway_production.py
./api_gateway_production_enhanced.py
./api_gateway_production_enhanced_no_prometheus.py
./api_gateway_production_enhanced_v2.py
./api_gateway_production_final.py
./api_gateway_production_final_complete.py
./api_gateway_production_minimal_security.py
./api_gateway_protection_ready.py
./api_gateway_server.py
./api_gateway_server_current.py
./api_gateway_sync_test.py
./api_gateway_test_simplified.py
./app_settings_sync_router.py
./auto_fix_metrics_router.py
./check_router_code.py
./components_router.py
./crash_detection_router.py
./crash_detection_router_optimized.py
./crash_detection_sync_router.py
./elderly_interface_sync_router.py
./gamification_router.py
./notifications_router_extended.py
./notifications_router_server.py
./offline_storage_sync_router.py
./other_functions_sync_router.py
./parental_control_sync_router.py
./subscription_sync_router.py
./system_router.py
./user_profile_sync_router.py

### Директория app/ в репозитории
app/routers/referral_fixed.py

## 🔍 СРАВНЕНИЕ КЛЮЧЕВЫХ ФАЙЛОВ

### Проверка ключевых файлов:

| Файл | На сервере | В репозитории | Статус |
|------|------------|---------------|--------|
| api_gateway_server_current.py | ✅ Да | ✅ Да | ✅ Идентичны |
| Файл | На сервере | В репозитории | Статус |
|------|------------|---------------|--------|
| main.py | ✅ Да | ❌ Нет | ⚠️  Только на сервере |
| Файл | На сервере | В репозитории | Статус |
|------|------------|---------------|--------|
| app/main.py | ✅ Да | ❌ Нет | ⚠️  Только на сервере |
| Файл | На сервере | В репозитории | Статус |
|------|------------|---------------|--------|
| app/routers | ✅ Да | ✅ Да | ✅ Идентичны |

## 📝 ВЫВОДЫ

### Идентичность данных:

1. **Основные файлы:** Проверьте таблицу выше
2. **Структура:** Сравните списки файлов
3. **Рекомендация:** Создайте бэкап сервера для полного сравнения
