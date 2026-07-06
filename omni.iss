[Setup]
AppName=OMNI Engine
AppVersion=1.0
DefaultDirName={localappdata}\OMNI_Engine
DefaultGroupName=OMNI Engine
OutputDir=installer
OutputBaseFilename=OMNI_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
ChangesEnvironment=yes

[Files]
Source: "dist\omni\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "marketplace.json"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Check: NeedsAddPath(ExpandConstant('{app}'))

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath) then
  begin
    Result := True;
    Exit;
  end;
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;
