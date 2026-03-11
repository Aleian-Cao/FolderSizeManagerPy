$WshShell = New-Object -comObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\FileSMPy.lnk")
$Shortcut.TargetPath = "C:\Scripts\FolderSizeManagerPy\dist\FileSMPy.exe"
$Shortcut.WorkingDirectory = "C:\Scripts\FolderSizeManagerPy\dist"
$Shortcut.IconLocation = "C:\Scripts\FolderSizeManagerPy\FolderSizeManagerPy 2 logo.ico"
$Shortcut.Save()
Write-Host "Shortcut created at $DesktopPath\FileSMPy.lnk"