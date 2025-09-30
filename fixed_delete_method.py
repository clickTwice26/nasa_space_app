    def delete_applications(self, app='all'):
        """Delete PM2 applications (only NASA Space App ones)"""
        Logger.section("Deleting NASA Space App Applications")
        
        # Define our specific applications to avoid deleting others
        if app == 'all':
            apps_to_delete = ['nasa-space-app', 'terrapulse-team-website']
        elif app == 'flask':
            apps_to_delete = ['nasa-space-app']
        elif app == 'team':
            apps_to_delete = ['terrapulse-team-website']
        else:
            apps_to_delete = []
        
        success = True
        results = []
        
        for app_name in apps_to_delete:
            Logger.info(f"Deleting {app_name}...")
            result = subprocess.run(["pm2", "delete", app_name], capture_output=True, text=True)
            
            if result.returncode == 0:
                Logger.success(f"✅ {app_name} deleted successfully")
                results.append(f"{app_name}: deleted")
            else:
                # Check if the app doesn't exist (which is not an error)
                if "Process or Namespace" in result.stderr and "not found" in result.stderr:
                    Logger.info(f"ℹ️  {app_name} was not running (already deleted)")
                    results.append(f"{app_name}: not found")
                else:
                    Logger.error(f"❌ Failed to delete {app_name}: {result.stderr}")
                    results.append(f"{app_name}: failed - {result.stderr}")
                    success = False
        
        if success:
            Logger.success("🎉 NASA Space App applications deleted successfully")
            Logger.info("Other PM2 applications were left untouched")
        else:
            Logger.error("Some deletions failed")
        
        return success