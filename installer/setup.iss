; Inno Setup 安装脚本
; 用途: 将独立的 quant-agent.exe 打包成专业的 Windows 安装程序
;
; 使用方法:
; 1. 先运行 python build.py 生成 dist/quant-agent.exe
; 2. 下载并安装 Inno Setup (https://jrsoftware.org/isdl.php)
; 3. 在 Inno Setup Compiler 中打开此文件
; 4. 点击 Build -> Compile 生成安装程序
; 5. 输出: installer/output/QuantAgentSetup-0.1.0.exe

[Setup]
; 应用信息
AppName=Quant Agent
AppVersion=0.1.0
AppPublisher=Your Company
AppPublisherURL=https://your-company.com
AppSupportURL=https://your-company.com/support
AppUpdatesURL=https://your-company.com/downloads

; 安装路径
DefaultDirName={autopf}\QuantAgent
DefaultGroupName=Quant Agent
DisableProgramGroupPage=yes

; 输出设置
OutputDir=installer\output
OutputBaseFilename=QuantAgentSetup-0.1.0
Compression=lzma2/max
SolidCompression=yes

; 架构设置（仅 64 位）
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; 安装向导设置
WizardStyle=modern
; SetupIconFile=installer\icon.ico
; UninstallDisplayIcon={app}\quant-agent.exe

; 权限设置
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Files]
; 复制独立的可执行文件到安装目录
; 这个 .exe 包含了 Python 解释器和所有依赖，完全独立
Source: "..\dist\installer\quant-agent.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 开始菜单快捷方式
Name: "{group}\Quant Agent"; Filename: "{app}\quant-agent.exe"
Name: "{group}\卸载 Quant Agent"; Filename: "{uninstallexe}"

; 桌面快捷方式（可选）
Name: "{autodesktop}\Quant Agent"; Filename: "{app}\quant-agent.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加选项:"

[Registry]
; 注册自定义协议 quant-agent://
; 这样 Web 端可以通过 quant-agent://launch 唤起应用
Root: HKCR; Subkey: "quant-agent"; ValueType: string; ValueName: ""; ValueData: "URL:Quant Agent Protocol"; Flags: uninsdeletekey
Root: HKCR; Subkey: "quant-agent"; ValueType: string; ValueName: "URL Protocol"; ValueData: ""
Root: HKCR; Subkey: "quant-agent\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\quant-agent.exe,0"
Root: HKCR; Subkey: "quant-agent\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\quant-agent.exe"" ""%1"""

[Run]
; 安装完成后可选择立即运行
Filename: "{app}\quant-agent.exe"; Description: "立即启动 Quant Agent"; Flags: nowait postinstall skipifsilent

[Code]
// 检查是否已有实例在运行
function InitializeSetup(): Boolean;
begin
  Result := True;

  // 可以在这里添加检查逻辑
  // 例如检查服务是否正在运行
end;

// 卸载前的清理
function InitializeUninstall(): Boolean;
begin
  Result := True;

  // 尝试停止正在运行的服务
  MsgBox('如果 Quant Agent 正在运行，请先关闭程序再继续卸载。', mbInformation, MB_OK);
end;

[UninstallDelete]
; 卸载时删除的文件（如日志等）
Type: filesandordirs; Name: "{app}"
