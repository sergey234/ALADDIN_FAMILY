#!/usr/bin/env python3
"""
Создание Launch Screen для iOS и Android
"""
import os
import time
from PIL import Image

# Размеры для iOS
IOS_SIZES = [
    {'name': 'iPhone_15_Pro_Max', 'width': 1290, 'height': 2796},
    {'name': 'iPhone_15_Pro', 'width': 1179, 'height': 2556},
    {'name': 'iPhone_SE', 'width': 1242, 'height': 2208},
    {'name': 'iPad_Pro_12.9', 'width': 2048, 'height': 2732},
]

# Размеры для Android
ANDROID_SIZES = [
    {'name': 'xxxhdpi', 'width': 1440, 'height': 2560},
    {'name': 'xxhdpi', 'width': 1080, 'height': 1920},
    {'name': 'xhdpi', 'width': 720, 'height': 1280},
    {'name': 'hdpi', 'width': 480, 'height': 800},
]


def create_launch_screens():
    """Создаёт Launch Screen для всех размеров"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("❌ Selenium не найден. Устанавливаю...")
        os.system("pip3 install selenium --quiet")
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, 'launch_screen.html')
    
    print("🎨 СОЗДАНИЕ LAUNCH SCREENS")
    print("=" * 70)
    
    # iOS Launch Screens
    print("\n📱 iOS Launch Screens:")
    ios_dir = os.path.join(base_dir, 'ios')
    os.makedirs(ios_dir, exist_ok=True)
    
    for size in IOS_SIZES:
        print(f"   {size['name']} ({size['width']}×{size['height']})...")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument(f"--window-size={size['width']},{size['height']}")
        options.add_argument('--force-device-scale-factor=1')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        
        driver = webdriver.Chrome(options=options)
        
        try:
            driver.get(f"file://{html_path}")
            time.sleep(3)  # Ждём анимацию
            
            output_path = os.path.join(ios_dir, f"LaunchScreen_{size['name']}.png")
            driver.save_screenshot(output_path)
            
            img = Image.open(output_path)
            file_size = os.path.getsize(output_path) / 1024
            print(f"      ✅ Создан: {img.size[0]}×{img.size[1]}, {file_size:.1f} KB")
        
        finally:
            driver.quit()
    
    # Android Launch Screens
    print("\n🤖 Android Launch Screens:")
    android_dir = os.path.join(base_dir, 'android')
    os.makedirs(android_dir, exist_ok=True)
    
    for size in ANDROID_SIZES:
        print(f"   {size['name']} ({size['width']}×{size['height']})...")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument(f"--window-size={size['width']},{size['height']}")
        options.add_argument('--force-device-scale-factor=1')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        
        driver = webdriver.Chrome(options=options)
        
        try:
            driver.get(f"file://{html_path}")
            time.sleep(3)
            
            output_path = os.path.join(android_dir, f"launch_screen_{size['name']}.png")
            driver.save_screenshot(output_path)
            
            img = Image.open(output_path)
            file_size = os.path.getsize(output_path) / 1024
            print(f"      ✅ Создан: {img.size[0]}×{img.size[1]}, {file_size:.1f} KB")
        
        finally:
            driver.quit()
    
    print("\n" + "=" * 70)
    print(f"🎉 Готово! Создано {len(IOS_SIZES) + len(ANDROID_SIZES)} Launch Screens")
    print(f"📁 iOS: {ios_dir}")
    print(f"📁 Android: {android_dir}")


if __name__ == "__main__":
    create_launch_screens()




