#define AppName "SHEIKH HAMAMOMIN AI"
[Setup]
AppId={{4868BDA9-105F-43C0-B70C-E872C7D877CC}
AppName={#AppName}
AppVersion=0.1.0
DefaultDirName={localappdata}\Programs\SheikhHamamomin
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
OutputDir=..\dist\installer
OutputBaseFilename=SheikhHamamomin-Setup
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\SheikhHamamomin.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
[Files]
Source: "..\dist\SheikhHamamomin\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\SheikhHamamomin.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\SheikhHamamomin.exe"; Tasks: desktopicon
[Tasks]
Name: desktopicon; Description: "Create a desktop shortcut"; Flags: unchecked
[Run]
Filename: "{app}\SheikhHamamomin.exe"; Description: "Launch assistant"; Flags: nowait postinstall skipifsilent
