$TargetFile = "c:\Scripts\dist\FolderSizeManagerPro.exe"
$ShortcutName = "Folder Size Manager Pro.lnk"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath $ShortcutName

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetFile
$Shortcut.WorkingDirectory = "c:\Scripts\dist"
$Shortcut.Description = "Ứng dụng quản lý dung lượng chuyên nghiệp (Lazy Loading + Filters)"
$Shortcut.IconLocation = $TargetFile
$Shortcut.Save()

Write-Host "Đã tạo shortcut tại: $ShortcutPath" -ForegroundColor Green
