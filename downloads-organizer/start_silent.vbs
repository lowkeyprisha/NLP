' Smart Downloads Organizer - Silent Background Launcher
' Double-click this to start the organizer without a console window

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Run the organizer hidden
WshShell.Run "cmd /c cd /d """ & scriptDir & """ && python organizer.py > organizer_console.log 2>&1", 0, False
