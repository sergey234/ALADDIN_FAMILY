import sys

file_path = sys.argv[1]

with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if 'def execute_function(self, func_name: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Any, Optional[str]]:' in line:
        # Add real backup interception
        indent = "        "
        new_lines.append(f"{indent}if func_name == 'backup_component':\n")
        new_lines.append(f"{indent}    return True, self._execute_real_backup(params.get('component_id')), None\n\n")

    if 'def _get_fallback_data(self, func_name: str, params: Dict[str, Any]) -> Dict[str, Any]:' in line:
        # Insert _execute_real_backup before this method
        indent = "    "
        new_lines.insert(-1, f"\n{indent}def _execute_real_backup(self, component_id: str) -> Dict[str, Any]:\n")
        new_lines.insert(-1, f"{indent}    import subprocess\n")
        new_lines.insert(-1, f"{indent}    import os\n")
        new_lines.insert(-1, f"{indent}    backup_id = f'backup_{{component_id}}_{{int(time.time())}}'\n")
        new_lines.insert(-1, f"{indent}    backup_dir = '/opt/aladdin-backend/backups/db'\n")
        new_lines.insert(-1, f"{indent}    backup_path = f'{{backup_dir}}/{{backup_id}}.sql'\n")
        new_lines.insert(-1, f"{indent}    try:\n")
        new_lines.insert(-1, f"{indent}        os.makedirs(backup_dir, exist_ok=True)\n")
        new_lines.insert(-1, f"{indent}        cmd = f\"PGPASSWORD='AladdinSecure2024!' pg_dump -h localhost -U aladdin_user -d aladdin_db > {{backup_path}}\"\n")
        new_lines.insert(-1, f"{indent}        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)\n")
        new_lines.insert(-1, f"{indent}        if result.returncode == 0:\n")
        new_lines.insert(-1, f"{indent}            return {{'status': 'success', 'backup_id': backup_id, 'path': backup_path, 'source': 'real_sfm'}}\n")
        new_lines.insert(-1, f"{indent}        return {{'status': 'error', 'message': result.stderr, 'source': 'real_sfm'}}\n")
        new_lines.insert(-1, f"{indent}    except Exception as e:\n")
        new_lines.insert(-1, f"{indent}        return {{'status': 'error', 'message': str(e), 'source': 'real_sfm'}}\n\n")

with open(file_path, 'w') as f:
    f.writelines(new_lines)
