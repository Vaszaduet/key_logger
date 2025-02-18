[Setup]
AppName=KeyLogger
AppVersion=1.0
DefaultDirName={pf}\KeyLogger
DefaultGroupName=KeyLogger
OutputDir=Output
OutputBaseFilename=KeyLogger_Setup
UninstallDisplayIcon={app}\key_logger.ico
PrivilegesRequired=admin

[Files]
Source: "dist\KeyLogger.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "key_logger.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\KeyLogger"; Filename: "{app}\KeyLogger.exe"; IconFilename: "{app}\key_logger.ico"
Name: "{commondesktop}\KeyLogger"; Filename: "{app}\KeyLogger.exe"; IconFilename: "{app}\key_logger.ico"
Name: "{group}\Удалить KeyLogger"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\KeyLogger.exe"; Description: "Запустить KeyLogger"; Flags: postinstall nowait

[UninstallDelete]
Type: filesandordirs; Name: "{app}"