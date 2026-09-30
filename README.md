# Irok Configurator

A small launcher for the official Irok web driver ([hid.irok.cn](https://hid.irok.cn)).

It gives you a Start-menu entry for the configurator, so you can press the Windows
key, type "Irok", press Enter. No browser tab, no typing a URL, no digging through
bookmarks.

It is **not** a keyboard driver. It contains no keyboard logic of its own and talks
to your keyboard zero bytes. Every setting you change is still applied by Irok's own
web software, over HTTPS, exactly as if you had opened the site yourself. This is
just a shortcut and a window.

## Why this exists

The Irok web driver uses the **WebHID** API to reach the keyboard. WebHID is
implemented by Chromium-based browsers only. Firefox and Safari do not implement
it, and Firefox's position is that the API is harmful, so waiting does not help.

This launcher uses a browser you already have. It also runs the configurator in an
**isolated browser profile**, which means extensions such as Dark Reader cannot
alter the configurator's interface, and your normal browser profile is never
touched.

## Requirements

- Windows 10 or 11, 64-bit
- One of: Microsoft Edge, Google Chrome, Brave, Opera or Vivaldi

No .NET install, no admin rights, no background service, no telemetry. The launcher
is a single ~26 KB file and exits as soon as the browser starts.

## Install

Download `IrokConfigurator.exe` and run it.

**First run, one time only:** the configurator window opens with Chrome/Edge's
welcome screen. Dismiss it, then pick your keyboard when the device list appears.
The browser remembers that choice, so it never asks again. From then on it is one
click, every time.

The launcher appears in the Start menu and, by default, on your desktop. To remove
it, use *Settings → Apps → Installed apps → Irok Configurator → Uninstall*, or run:

```
IrokConfigurator.exe --uninstall
```

Uninstalling also closes the configurator window if it is open, and deletes the
isolated profile. It never touches your normal browser profile or anything else.

## Configuration

Settings live in a plain text file next to the executable:

```
%LOCALAPPDATA%\Programs\IrokConfigurator\config.txt
```

| Key | Values | Default | Meaning |
| --- | --- | --- | --- |
| `Url` | any URL | `https://hid.irok.cn` | Which configurator to open. Change this if Irok moves their site. |
| `Preferred` | `edge`, `chrome`, `brave`, `opera`, `vivaldi` | `edge` | Which browser to try first. Falls through to the others if not installed. |
| `BrowserPath` | full path | *(empty)* | Force a specific browser, e.g. a portable install. Wins over `Preferred`. |
| `SharedProfile` | `true`, `false` | `false` | `true` uses your normal browser profile. Convenient if you are already signed in, but your extensions will apply to the configurator. |
| `DesktopShortcut` | `true`, `false` | `true` | Whether to keep the desktop shortcut. |

Edit the file, then reopen the launcher. Delete the file to restore defaults.

### Command line

```
IrokConfigurator.exe              install if needed, then open
IrokConfigurator.exe --open       open only
IrokConfigurator.exe --uninstall  remove everything
IrokConfigurator.exe --silent     no dialogs, for scripting
```

## If Windows warns you

This binary is **not code-signed**, so SmartScreen may show *Windows protected your
PC* the first time you run it. Click **More info → Run anyway**. This is expected
for any unsigned program and is not by itself a sign of a problem.

The real fix is signing. If you maintain this project and want to remove that
prompt, you need a code-signing certificate and to sign the binary in
`build.ps1` with `signtool`. That costs money per year and is the main reason an
unofficial launcher cannot look as trustworthy as an installed driver.

## Troubleshooting

**"No supported browser was found."**
The launcher needs a Chromium browser. Edge ships with Windows; if you removed it,
install Edge or Chrome, then run the launcher again.

**The device list does not appear, or the keyboard is missing.**
Unplug and reconnect the keyboard, then click the *Connect* / *Refresh* button.
The keyboard must be on its own USB port, not through an unpowered hub. Wired only
for the web driver.

**The welcome screen keeps coming back.**
Your isolated profile may be read-only, or antivirus may be blocking writes to
`%LOCALAPPDATA%`. Try `SharedProfile=true` in `config.txt` as a workaround.

**Nothing happens when I click the icon.**
Read `%LOCALAPPDATA%\Programs\IrokConfigurator\IrokConfigurator.log`. It records
which browser was chosen and the exact command line used.

**The site changed and the configurator looks wrong.**
This is a launcher, so it cannot be broken by the site changing, but it can be
pointed at a different address with `Url=` in `config.txt`.

## Building from source

Requirements: Windows with the .NET Framework (present by default) and nothing
else. No Visual Studio, no NuGet, no network access needed if `assets\irok.ico`
exists.

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

Output: `dist\IrokConfigurator.exe`, with the SHA-256 printed.

The source is one file, `src\IrokConfigurator.cs`, written to compile with the
in-box `csc.exe`, which is a C# 5 compiler and rejects newer syntax.

## Legal

Unofficial community project. Not affiliated with, endorsed by, or supported by
Irok or KBDfans. All trademarks belong to their owners. The configurator itself is
served by Irok at `hid.irok.cn`; this project only opens it.
