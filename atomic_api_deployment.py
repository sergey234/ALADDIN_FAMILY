#!/usr/bin/env python3
"""
🚀 ATOMIC API DEPLOYMENT SCRIPT
Переход с 101 декораторов → 183 декоратора
Безопасная атомарная замена с автоматическим откатом
"""

import os
import sys
import time
import shutil
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path

class AtomicAPIDeployment:
    def __init__(self):
        self.project_root = Path("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")
        self.current_file = self.project_root / "api_gateway_final.py"
        self.target_file = self.project_root / "api_gateway_complete.py"
        self.backup_dir = self.project_root / "emergency_backups"
        self.backup_dir.mkdir(exist_ok=True)

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        if not file_path.exists():
            return ""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def create_emergency_backup(self) -> str:
        """Create emergency backup of current production file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"emergency_backup_{timestamp}.py"
        backup_path = self.backup_dir / backup_name

        print(f"🛡️ Creating emergency backup: {backup_name}")
        shutil.copy2(self.current_file, backup_path)

        # Save hash for verification
        backup_hash = self.calculate_file_hash(backup_path)
        hash_file = backup_path.with_suffix('.sha256')
        with open(hash_file, 'w') as f:
            f.write(backup_hash)

        print(f"✅ Emergency backup created: {backup_hash[:16]}...")
        return str(backup_path)

    def validate_files(self) -> bool:
        """Validate both current and target files"""
        print("🔍 Validating files...")

        # Check current file exists
        if not self.current_file.exists():
            print(f"❌ Current file not found: {self.current_file}")
            return False

        # Check target file exists
        if not self.target_file.exists():
            print(f"❌ Target file not found: {self.target_file}")
            return False

        # Count decorators
        current_decorators = self.count_decorators(self.current_file)
        target_decorators = self.count_decorators(self.target_file)

        print(f"📊 Current version: {current_decorators} decorators")
        print(f"📊 Target version: {target_decorators} decorators")
        print(f"📈 Adding: +{target_decorators - current_decorators} decorators")

        if target_decorators <= current_decorators:
            print("❌ Target version has fewer or equal decorators!")
            return False

        return True

    def count_decorators(self, file_path: Path) -> int:
        """Count FastAPI decorators in file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                import re
                decorators = re.findall(r'@app\.(get|post|put|delete|patch)', content)
                return len(decorators)
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return 0

    def atomic_replace(self) -> bool:
        """Perform atomic file replacement"""
        print("🚀 Starting atomic replacement...")

        try:
            # Create backup first
            backup_path = self.create_emergency_backup()

            # Calculate target hash before replacement
            target_hash = self.calculate_file_hash(self.target_file)

            # Atomic replacement using temporary file
            temp_file = self.current_file.with_suffix('.tmp')

            # Copy target to temp
            shutil.copy2(self.target_file, temp_file)

            # Atomic move (this is atomic on POSIX systems)
            temp_file.replace(self.current_file)

            # Verify replacement
            new_hash = self.calculate_file_hash(self.current_file)

            if new_hash == target_hash:
                print("✅ Atomic replacement successful!")
                print(f"🔄 New file hash: {new_hash[:16]}...")
                return True
            else:
                print("❌ Hash verification failed! Starting rollback...")
                self.rollback(backup_path)
                return False

        except Exception as e:
            print(f"❌ Atomic replacement failed: {e}")
            return False

    def rollback(self, backup_path: str) -> bool:
        """Rollback to backup version"""
        try:
            print(f"🔄 Rolling back to: {backup_path}")
            backup_file = Path(backup_path)

            if backup_file.exists():
                shutil.copy2(backup_file, self.current_file)
                print("✅ Rollback successful!")
                return True
            else:
                print("❌ Backup file not found!")
                return False
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False

    def health_check(self) -> bool:
        """Basic health check after deployment"""
        print("🏥 Running health check...")

        try:
            # Check if file exists and is readable
            if not self.current_file.exists():
                print("❌ API file not found after deployment!")
                return False

            # Check decorator count
            decorators = self.count_decorators(self.current_file)
            if decorators < 180:  # Should be 183
                print(f"❌ Insufficient decorators: {decorators} (expected ~183)")
                return False

            print(f"✅ Health check passed: {decorators} decorators found")
            return True

        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

    def deploy(self) -> bool:
        """Main deployment function"""
        print("🚀 STARTING ATOMIC API DEPLOYMENT")
        print("=" * 50)

        # Step 1: Validate
        if not self.validate_files():
            print("❌ Validation failed!")
            return False

        # Step 2: Create emergency backup
        backup_path = self.create_emergency_backup()

        # Step 3: Atomic replacement
        if not self.atomic_replace():
            print("❌ Deployment failed!")
            return False

        # Step 4: Health check
        if not self.health_check():
            print("❌ Health check failed! Rolling back...")
            self.rollback(backup_path)
            return False

        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print(f"📊 New API Gateway: 183 decorators active")
        print(f"🛡️ Emergency backup: {backup_path}")

        return True

def main():
    deployment = AtomicAPIDeployment()
    success = deployment.deploy()

    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. Restart your API server")
        print("2. Test all endpoints individually")
        print("3. Monitor performance metrics")
        print("4. Update documentation")
        sys.exit(0)
    else:
        print("\n❌ DEPLOYMENT FAILED!")
        print("Check logs above for details")
        sys.exit(1)

if __name__ == "__main__":
    main()