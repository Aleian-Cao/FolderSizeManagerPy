$TargetFile = "c:\Scripts\dist\FolderSizeManagerUltimate.exe"
$ShortcutName = "Folder Size Manager Ultimate.lnk"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath $ShortcutName

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetFile
$Shortcut.WorkingDirectory = "c:\Scripts\dist"
$Shortcut.Description = "Giao diện hiện đại (Modern UI) + Tính năng Pro"
$Shortcut.IconLocation = $TargetFile
$Shortcut.Save()

Write-Host "Đã tạo shortcut tại: $ShortcutPath" -ForegroundColor Green
