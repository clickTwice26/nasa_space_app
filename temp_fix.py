#!/usr/bin/env python3

# Temporary script to fix the PM2 delete method
import re

def fix_pm2_delete():
    with open('/home/raju/nasa_space_app/manage.py', 'r') as f:
        content = f.read()
    
    # Replace the problematic delete method with a safe version
    old_pattern = r'''def delete_applications\(self, app='all'\):
        """Delete PM2 applications"""
        Logger\.section\("Deleting Applications"\)
        
        if app == 'all':
            result = subprocess\.run\(\["pm2", "delete", "all"\], capture_output=True, text=True\)
        elif app == 'flask':
            result = subprocess\.run\(\["pm2", "delete", "nasa-space-app"\], capture_output=True, text=True\)
        elif app == 'team':
            result = subprocess\.run\(\["pm2", "delete", "terrapulse-team-website"\], capture_output=True, text=True\)
        
        if result\.returncode == 0:
            Logger\.success\("Applications deleted successfully"\)
            return True
        else:
            Logger\.error\(f"Failed to delete applications: \{result\.stderr\}"\)
            return False'''

    new_method = '''def delete_applications(self, app='all'):
        """Delete PM2 applications (only NASA Space App ones)"""
        Logger.section("Deleting NASA Space App Applications")
        
        # Define our specific applications
        if app == 'all':
            apps_to_delete = ['nasa-space-app', 'terrapulse-team-website']
        elif app == 'flask':
            apps_to_delete = ['nasa-space-app']
        elif app == 'team':
            apps_to_delete = ['terrapulse-team-website']
        
        success = True
        for app_name in apps_to_delete:
            Logger.info(f"Deleting {app_name}...")
            result = subprocess.run(["pm2", "delete", app_name], capture_output=True, text=True)
            
            if result.returncode == 0:
                Logger.success(f"{app_name} deleted successfully")
            else:
                # Check if the app doesn't exist (which is not an error in this context)
                if "Process or Namespace" in result.stderr and "not found" in result.stderr:
                    Logger.info(f"{app_name} was not running (already deleted)")
                else:
                    Logger.error(f"Failed to delete {app_name}: {result.stderr}")
                    success = False
        
        if success:
            Logger.success("NASA Space App applications deleted successfully")
        
        return success'''
    
    # Use a simpler pattern to match and replace
    pattern = r'subprocess\.run\(\["pm2", "delete", "all"\], capture_output=True, text=True\)'
    
    # Count occurrences
    matches = re.findall(pattern, content)
    print(f"Found {len(matches)} occurrences of 'pm2 delete all'")
    
    # Replace all occurrences
    new_content = re.sub(pattern, '''# FIXED: Only delete NASA Space App applications
            if app == 'all':
                apps_to_delete = ['nasa-space-app', 'terrapulse-team-website']
                success = True
                for app_name in apps_to_delete:
                    result = subprocess.run(["pm2", "delete", app_name], capture_output=True, text=True)
                    if result.returncode != 0 and "not found" not in result.stderr:
                        success = False
                        break
                result = type('obj', (object,), {'returncode': 0 if success else 1, 'stderr': 'Fixed delete method'})''', content)
    
    with open('/home/raju/nasa_space_app/manage.py', 'w') as f:
        f.write(new_content)
    
    print("Fixed PM2 delete method!")

if __name__ == "__main__":
    fix_pm2_delete()