# backup_manager.py
# Vault Backup and Export Functionality

import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox


def export_vault_backup(username, output_path=None):
    """
    Export entire vault as encrypted backup

    Returns: (success, message, filepath)
    """
    try:
        # Check if vault exists
        vault_file = f"vault_{username}.json"
        if not os.path.exists(vault_file):
            return False, "No vault found to backup", None

        # Get output path if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"vault_backup_{username}_{timestamp}.vault"
            output_path = filedialog.asksaveasfilename(
                defaultextension=".vault",
                initialfile=default_name,
                title="Save Vault Backup",
                filetypes=[("Vault Backup", "*.vault"), ("All Files", "*.*")]
            )

        if not output_path:
            return False, "Backup cancelled", None

        # Read vault data
        with open(vault_file, 'r') as f:
            vault_data = json.load(f)

        # Create backup package with metadata
        backup_data = {
            "username": username,
            "backup_date": datetime.now().isoformat(),
            "file_count": len(vault_data),
            "vault_data": vault_data
        }

        # Write backup file
        with open(output_path, 'w') as f:
            json.dump(backup_data, f, indent=2)

        return True, f"Backup created successfully!\nFiles backed up: {len(vault_data)}", output_path

    except Exception as e:
        return False, f"Backup failed: {str(e)}", None


def import_vault_backup(username, backup_path=None):
    """
    Import vault from backup file

    Returns: (success, message, files_imported)
    """
    try:
        # Get backup file if not provided
        if not backup_path:
            backup_path = filedialog.askopenfilename(
                title="Select Vault Backup",
                filetypes=[("Vault Backup", "*.vault"), ("All Files", "*.*")]
            )

        if not backup_path:
            return False, "Import cancelled", 0

        # Read backup file
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)

        # Validate backup format
        if "vault_data" not in backup_data:
            return False, "Invalid backup file format", 0

        vault_data = backup_data["vault_data"]
        file_count = len(vault_data)

        # Check if vault already exists
        vault_file = f"vault_{username}.json"
        if os.path.exists(vault_file):
            response = messagebox.askyesno(
                "Vault Exists",
                f"A vault already exists for {username}.\n\n"
                f"Current files: {len(json.load(open(vault_file, 'r')))}\n"
                f"Backup files: {file_count}\n\n"
                "Do you want to MERGE the backup into existing vault?\n"
                "(Click 'No' to cancel import)"
            )
            if not response:
                return False, "Import cancelled", 0

            # Merge with existing vault
            with open(vault_file, 'r') as f:
                existing_data = json.load(f)

            # Merge (backup files overwrite existing ones with same name)
            existing_data.update(vault_data)
            vault_data = existing_data

        # Write vault file
        with open(vault_file, 'w') as f:
            json.dump(vault_data, f, indent=2)

        backup_date = backup_data.get("backup_date", "Unknown")
        return True, f"Import successful!\nFiles imported: {file_count}\nBackup date: {backup_date}", file_count

    except Exception as e:
        return False, f"Import failed: {str(e)}", 0


def export_activity_report(username):
    """
    Export activity report as PDF/Text

    Returns: (success, message, filepath)
    """
    try:
        from datetime import datetime

        # Read logs
        log_file = "logs.txt"
        if not os.path.exists(log_file):
            return False, "No activity logs found", None

        with open(log_file, 'r') as f:
            all_logs = f.readlines()

        # Filter logs for this user
        user_logs = [log for log in all_logs if username in log]

        if not user_logs:
            return False, "No activity found for this user", None

        # Generate report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"activity_report_{username}_{timestamp}.txt",
            title="Save Activity Report",
            filetypes=[("Text File", "*.txt"), ("All Files", "*.*")]
        )

        if not report_path:
            return False, "Export cancelled", None

        # Write report
        with open(report_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write(f"ACTIVITY REPORT FOR: {username}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total Activities: {len(user_logs)}\n\n")
            f.write("=" * 60 + "\n")
            f.write("ACTIVITY LOG:\n")
            f.write("=" * 60 + "\n\n")

            for log in user_logs:
                f.write(log)

        return True, f"Report exported successfully!\nActivities logged: {len(user_logs)}", report_path

    except Exception as e:
        return False, f"Export failed: {str(e)}", None