#!/usr/bin/expect -f
# Завершение деплоя Crash Detection Agent

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 Завершение деплоя Crash Detection Agent"
puts "=========================================="
puts ""

# Исправление скрипта регистрации
puts "📝 Шаг 1: Исправление скрипта регистрации..."
spawn scp register_crash_detection_in_sfm.py $server:/tmp/

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Скрипт обновлен"
    }
}
wait

# Регистрация в SFM
puts "📝 Шаг 2: Регистрация в SFM..."
spawn ssh $server "cd /tmp && echo 'y' | python3 register_crash_detection_in_sfm.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Регистрация завершена"
    }
}
wait

# Статистика SFM
puts "📊 Шаг 3: Статистика SFM..."
spawn scp check_sfm_stats_crash.py $server:/tmp/

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}
wait

spawn ssh $server "cd /tmp && python3 check_sfm_stats_crash.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}
wait

puts ""
puts "✅ ДЕПЛОЙ ЗАВЕРШЕН!"
