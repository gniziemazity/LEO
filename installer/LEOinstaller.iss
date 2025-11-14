;MIT License
;
;Copyright (c) 2024-2025 Anssi Gröhn
;
;Permission is hereby granted, free of charge, to any person obtaining a copy
;of this software and associated documentation files (the "Software"), to deal
;in the Software without restriction, including without limitation the rights
;to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
;copies of the Software, and to permit persons to whom the Software is
;furnished to do so, subject to the following conditions:
;
;The above copyright notice and this permission notice shall be included in all
;copies or substantial portions of the Software.
;
;THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
;IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
;FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
;AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
;LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
;OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
;SOFTWARE.
[Setup]
AppName=LEO (Lupsakkaasti ja Ehjästi Ohjelmoit)
AppVersion=1.0.1
WizardStyle=modern
DefaultDirName={autopf}\LEO
DefaultGroupName=RaduSoft
LicenseFile=..\LICENSE


[Files]    
Source: "..\code\*"; DestDir: "{app}\code"
Source: "..\plans\*"; DestDir: "{app}\plans"                               
Source: "..\settings\*"; DestDir: "{app}\settings"
Source: "..\tmp\*"; DestDir: "{commonappdata}\tmp"; Permissions: everyone-full; Attribs: 
Source: "..\kill.bat"; DestDir: "{app}"
Source: "..\start.bat"; DestDir: "{app}"
Source: "..\screen.ahk"; DestDir: "{app}"
Source: "..\icon.png"; DestDir: "{app}"


[Code]
var
  DownloadPage: TDownloadWizardPage;

function OnDownloadProgress(const Url, FileName: String; const Progress, ProgressMax: Int64): Boolean;
begin
  if Progress = ProgressMax then
    Log(Format('Successfully downloaded file to {tmp}: %s', [FileName]));
  Result := True;
end;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), @OnDownloadProgress);
end;
                                                                                
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  if CurPageID = wpReady then begin
    DownloadPage.Clear;
    DownloadPage.Add('https://github.com/gniziemazity/LEO/releases/download/v1.0.1/python-3.12.2-embed-amd64.zip', 'python.zip', '');
    // since captcha prevents downloading directly from official site
    DownloadPage.Add('https://github.com/gniziemazity/LEO/releases/download/v1.0.1/AutoHotkey_1.1.37.02.zip', 'autohotkey.zip', '');
    DownloadPage.Add('https://github.com/gniziemazity/LEO/releases/download/v1.0.1/get-pip.py','get-pip.py','');
    DownloadPage.Show;
    try
      try
        DownloadPage.Download; // This downloads the files to {tmp}
        Result := True;
      except
        if DownloadPage.AbortedByUser then
          Log('Aborted by user.')
        else
          SuppressibleMsgBox(AddPeriod(GetExceptionMessage), mbCriticalError, MB_OK, IDOK);
        Result := False;
      end;
    finally
      DownloadPage.Hide;
    end;
  end else
    Result := True;
end;

procedure CurStepChanged( CurStep: TSetupStep);
var
  data : array[1..5] of String;
  content, output: TArrayOfString;
   lines, i: Integer;
begin
  // run this prior to install, so we have something to copy later
  if CurStep = ssInstall then
  begin
     data[1] := 'python312.zip';
     data[2] := '.';
     data[3] := ExpandConstant('{app}\code');
     data[4] := ExpandConstant('{commonappdata}\LEO\python\Lib\site-packages');
     data[5] := 'Lib\site-packages';
     SaveStringsToFile(ExpandConstant('{tmp}\python312._pth'),data,False); 
  end
  else if CurStep = ssPostInstall then
  begin
        // make start script run with proper python exec
        LoadStringsFromFile(ExpandConstant('{app}/start.bat'), content );
        lines := GetArrayLength(content);
        SetArrayLength(output,lines+2);
        output[0] := ExpandConstant('SET TCL_LIBRARY={commonappdata}\LEO\python\Lib\site-packages\tcl\tcl8.6');
        output[1] := ExpandConstant('SET LEO_PROGRAMDATA={commonappdata}\LEO');
            
        for i := 0 to lines - 1 do 
        begin
          if Pos('python code/Main.py', content[i]) = 1 then
          begin
              output[i+2] := ExpandConstant('{commonappdata}\LEO\python\python.exe code/Main.py');
          end
          else
          begin
            output[i+2] := content[i];
          end;
        end;
        
        SaveStringsToFile( ExpandConstant('{app}/start.bat'), output, False);
  end;
end;
// as described here: https://stackoverflow.com/questions/3304463/how-do-i-modify-the-path-environment-variable-when-running-an-inno-setup-install
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
    'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  { look for the path with leading and trailing semicolon }
  { Pos() returns 0 if not found }
  Result := (Pos(';' + UpperCase(ExpandConstant(Param)) + ';', ';' + UpperCase(OrigPath) + ';') = 0) and 
            (Pos(';' + UpperCase(ExpandConstant(Param)) + '\;', ';' + UpperCase(OrigPath) + ';') = 0);
end;

procedure RemovePath(RemoveEntry: string);
var
  P: Integer;
  OrigPath: string;
begin
   if not RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
    'Path', OrigPath)
  then begin
    exit;
  end;
    repeat
      P := Pos(';' + Uppercase(ExpandConstant(RemoveEntry)) + ';', ';' + Uppercase(OrigPath) + ';');
      if P = 0 then
      begin
        Log(Format('Path [%s] not found in PATH', [RemoveEntry]));
      end
        else
      begin
        if P > 1 then P := P - 1;
        Delete(OrigPath, P, Length(RemoveEntry) + 1);
        Log(Format('Path [%s] removed from PATH => ', [RemoveEntry]));

        if RegWriteStringValue(HKLM, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', OrigPath) then
        begin
          Log('PATH updated');
        end
          else
        begin
          Log('Error updating PATH');
        end;
      end;
    until P = 0;
  
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
  begin
    RemovePath(ExpandConstant('{commonappdata}\LEO\python'));
    RemovePath(ExpandConstant('{commonappdata}\LEO\python\Scripts'));
    RemovePath(ExpandConstant('{commonappdata}\LEO\autohotkey'));
  end;
end;

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; \
    ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{commonappdata}\LEO\python"; \
    Check: NeedsAddPath('{commonappdata}\LEO\python')
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; \
    ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{commonappdata}\LEO\python\Scripts"; \
    Check: NeedsAddPath('{commonappdata}\LEO\python\Scripts')
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; \
    ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{commonappdata}\LEO\autohotkey"; \
    Check: NeedsAddPath('{commonappdata}\LEO\autohotkey')

; register Autohotkey stuff (bare minimum)
Root: HKCR; Subkey: ".ahk"; ValueType: string; ValueData: "AutoHotkeyScript"; Flags: uninsdeletevalue;
;Root: HKCR; Subkey: ".ahk\ShellNew"; ValueType: string; ValueName: "FileName"; ValueData: "Template.ahk"
Root: HKCR; Subkey: "AutoHotkeyScript"; ValueType: string; ValueData: "AutoHotkey Script"; Flags: uninsdeletevalue;
Root: HKCR; Subkey: "AutoHotkeyScript\DefaultIcon"; ValueType: string; ValueData: "{commonappdata}\LEO\autohotkey\AutoHotkeyU64.exe,1"; Flags: uninsdeletevalue;
Root: HKCR; Subkey: "AutoHotkeyScript\Shell"; ValueType: string; ValueData: "Open"; Flags: uninsdeletevalue;
Root: HKCR; Subkey: "AutoHotkeyScript\Shell\Open"; ValueType: string; ValueData: "Run Script"; Flags: uninsdeletevalue;
Root: HKCR; Subkey: "AutoHotkeyScript\Shell\Open\Command"; ValueType: string; ValueData: """{commonappdata}\LEO\autohotkey\AutoHotkeyU64.exe"" ""%1"" %*"; Flags: uninsdeletevalue;

[Run]
Filename: "cmd.EXE"; Parameters: "/C mkdir  ""{commonappdata}\LEO\python"""
Filename: "cmd.EXE"; Parameters: "/C mkdir  ""{commonappdata}\LEO\autohotkey"""                                        
Filename: "tar.EXE"; Parameters: "-xf {tmp}\python.zip -C ""{commonappdata}\LEO\python"""; 
Filename: "tar.EXE"; Parameters: "-xf {tmp}\autohotkey.zip -C ""{commonappdata}\LEO\autohotkey"""

; We need pip for packages
Filename: "{commonappdata}\LEO\python\python.exe"; Parameters: """{tmp}\get-pip.py"""; Flags: waituntilterminated
; Copy modified python path settings so we can get pip working
Filename: "cmd.EXE"; Parameters: "/C copy ""{tmp}\python312._pth"" ""{commonappdata}\LEO\python"""
; Off we go with ahk and others
Filename: "{commonappdata}\LEO\python\Scripts\pip.exe"; Parameters: "install ahk";
Filename: "{commonappdata}\LEO\python\Scripts\pip.exe"; Parameters: "install setuptools";
Filename: "{commonappdata}\LEO\python\Scripts\pip.exe"; Parameters: "install tkinter-embed";

[UninstallDelete]
Type: filesandordirs; Name: """{app}\code"""
[UninstallRun]
; This takes care of last residing stuff 
Filename: "cmd.EXE"; Parameters: "/C rmdir /S /Q ""{app}\LEO"""; RunOnceId: delApp
