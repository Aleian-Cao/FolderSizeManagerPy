$TargetFile = "c:\Scripts\dist\FolderSizeManagerPy.exe"
$ShortcutName = "Folder Size Manager (Python).lnk"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath $ShortcutName

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetFile
$Shortcut.WorkingDirectory = "c:\Scripts\dist"
$Shortcut.Description = "Ứng dụng quản lý dung lượng thư mục (Python Version)"
$Shortcut.IconLocation = $TargetFile
$Shortcut.Save()

Write-Host "Đã tạo shortcut tại: $ShortcutPath" -ForegroundColor Green
