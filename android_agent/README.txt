Krishna Android Agent v1

Main jobs:
1. Register this phone with Krishna Cloud
2. Poll cloud for commands
3. Execute simple commands:
   - ping
   - open_app
   - show_toast
   - open_url
4. Push execution result back to cloud

Core components:
- MainActivity
- CloudClient
- CommandPollService
- CommandExecutor
- AppLauncher
- later: AccessibilityService

Suggested package name:
com.krishna.agent