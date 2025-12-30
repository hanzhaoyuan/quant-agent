; Inno Setup 安装脚本
; 用途: 将独立的 quant-agent.exe 打包成专业的 Windows 安装程序
;
; 使用方法:
; 1. 先运行 python build.py 生成 dist/installer/quant-agent.exe
; 2. 下载并安装 Inno Setup (https://jrsoftware.org/isdl.php)
; 3. 在 Inno Setup Compiler 中打开此文件
; 4. 点击 Build -> Compile 生成安装程序
; 5. 输出: installer/output/QuantAgentSetup-0.1.0.exe

#define MyAppName "Quant Agent"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "FastBull"
#define MyAppURL "https://fastbull.com"
#define MyAppExeName "quant-agent.exe"

[Setup]
; 应用基本信息
AppId={{A5B3C2D1-E4F5-6789-ABCD-EF0123456789}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; 安装目录
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; 输出配置
OutputDir=installer\output
OutputBaseFilename=QuantAgentSetup-{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes

; 架构设置（仅 64 位）
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; 权限配置（需要管理员权限以注册URL协议）
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; UI配置
WizardStyle=modern
; SetupIconFile=icon.ico  ; 图标文件可选，如果没有可以注释掉
UninstallDisplayIcon={app}\{#MyAppExeName}

; 许可协议（可选）
; LicenseFile=LICENSE.txt

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startuprun"; Description: "开机自动启动 Quant Agent"; GroupDescription: "其他选项:"; Flags: unchecked

[Files]
; 安装主程序 - 这个路径是相对于 .iss 文件的位置
Source: "dist\installer\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; 如果有其他依赖文件，在此添加
; Source: "dist\installer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 开始菜单快捷方式
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; 桌面快捷方式（如果用户选择）
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; 注册 quant-agent:// URL 协议
; 这是关键部分，使浏览器能够通过 quant-agent://launch 启动应用

; 创建协议根键
Root: HKCR; Subkey: "quant-agent"; ValueType: string; ValueName: ""; ValueData: "URL:Quant Agent Protocol"; Flags: uninsdeletekey
Root: HKCR; Subkey: "quant-agent"; ValueType: string; ValueName: "URL Protocol"; ValueData: ""

; 设置协议图标
Root: HKCR; Subkey: "quant-agent\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"

; 设置协议处理程序
Root: HKCR; Subkey: "quant-agent\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[Run]
; 安装完成后的选项
Filename: "{app}\{#MyAppExeName}"; Description: "立即启动 {#MyAppName}"; Flags: nowait postinstall skipifsilent

; 如果用户选择开机自动启动
Filename: "{app}\{#MyAppExeName}"; Parameters: "--startup"; Flags: runhidden; Tasks: startuprun

[Code]
// 检查应用是否已在运行
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  // 检查端口17633是否被占用
  if Exec('cmd.exe', '/C netstat -ano | findstr ":17633"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
    begin
      if MsgBox('检测到 Quant Agent 可能正在运行。' + #13#10 +
                '建议先关闭后再继续安装。' + #13#10#13#10 +
                '是否继续安装？',
                mbConfirmation, MB_YESNO) = IDYES then
        Result := True
      else
        Result := False;
    end
    else
      Result := True;
  end
  else
    Result := True;
end;

// 卸载前检查
function InitializeUninstall(): Boolean;
var
  ResultCode: Integer;
begin
  if MsgBox('确定要卸载 Quant Agent 吗？', mbConfirmation, MB_YESNO) = IDYES then
  begin
    // 尝试关闭正在运行的进程
    Exec('taskkill', '/F /IM quant-agent.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Result := True;
  end
  else
    Result := False;
end;

[UninstallDelete]
; 卸载时删除日志等运行时生成的文件
Type: filesandordirs; Name: "{userappdata}\{#MyAppName}"
