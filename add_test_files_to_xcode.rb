#!/usr/bin/env ruby

# Скрипт для автоматического добавления тестовых файлов в Xcode проект
# Использование: ruby add_test_files_to_xcode.rb

require 'xcodeproj'

puts "🚀 ДОБАВЛЕНИЕ ТЕСТОВЫХ ФАЙЛОВ В XCODE ПРОЕКТ"
puts "=" * 50

project_path = 'ALADDIN.xcodeproj'
project = Xcodeproj::Project.open(project_path)
target = project.targets.find { |t| t.name == 'ALADDIN' }

if target.nil?
  puts "❌ Ошибка: Target 'ALADDIN' не найден в проекте"
  exit 1
end

# Список файлов для добавления
files_to_add = [
  'Core/Utilities/APITestAnalyzer.swift',
  'IntegrationTestView.swift',
  'IntegrationTestViewModel.swift',
  'SimpleAPITester.swift'
]

puts "📋 Добавляемые файлы:"
files_to_add.each_with_index do |file_path, index|
  puts "#{index + 1}. #{file_path}"
end

puts ""
puts "🔍 Проверяем файлы и добавляем в проект..."

added_count = 0
error_count = 0

files_to_add.each do |file_path|
  if File.exist?(file_path)
    begin
      # Проверяем, не добавлен ли уже файл
      existing_ref = project.files.find { |f| f.path == file_path }
      if existing_ref.nil?
        file_ref = project.new_file(file_path)
        target.add_file_references([file_ref])
        puts "✅ Добавлен: #{file_path}"
        added_count += 1
      else
        puts "⚠️  Уже добавлен: #{file_path}"
      end
    rescue => e
      puts "❌ Ошибка при добавлении #{file_path}: #{e.message}"
      error_count += 1
    end
  else
    puts "❌ Файл не найден: #{file_path}"
    error_count += 1
  end
end

# Сохраняем проект
begin
  project.save
  puts ""
  puts "💾 Проект сохранен успешно"
rescue => e
  puts "❌ Ошибка сохранения проекта: #{e.message}"
  exit 1
end

puts ""
puts "📊 РЕЗУЛЬТАТЫ:"
puts "✅ Добавлено файлов: #{added_count}"
puts "❌ Ошибок: #{error_count}"
puts "📁 Всего обработано: #{files_to_add.length}"

if added_count > 0
  puts ""
  puts "🎯 ДАЛЬНЕЙШИЕ ШАГИ:"
  puts "1. Перезапустите Xcode"
  puts "2. Выполните Product → Clean Build Folder"
  puts "3. Соберите проект (Cmd+B)"
  puts "4. Добавьте кнопку тестирования в Settings UI"
  puts "5. Запустите тестирование на устройстве"
end

puts ""
puts "🎉 ГОТОВО! Файлы добавлены в Xcode проект."