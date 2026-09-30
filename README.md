<div align="center">
  <img src="docs/hero.png" alt="Irok Configurator launcher" width="100%">
</div>

<div align="center">

[![Release](https://img.shields.io/github/v/release/zxkodas/irok-configurator?style=flat-square&label=release&color=ff6b4a)](https://github.com/zxkodas/irok-configurator/releases)
[![CI](https://github.com/zxkodas/irok-configurator/actions/workflows/build.yml/badge.svg)](https://github.com/zxkodas/irok-configurator/actions/workflows/build.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Windows 10/11](https://img.shields.io/badge/windows-10%20%7C%2011-0078d6?style=flat-square&logo=windows)](https://learn.microsoft.com/en-us/windows/release-health/windows-11-release-information)
[![Size](https://img.shields.io/badge/size-26%20KB-success?style=flat-square)](https://github.com/zxkodas/irok-configurator/releases)

</div>

# Irok Configurator

A launcher for the [Irok web software](https://hid.irok.cn). It saves you a few
clicks every time you want to change something on your keyboard.

## Install

Grab `IrokConfigurator-v1.0.0.zip` from the
[releases page](https://github.com/zxkodas/irok-configurator/releases), extract
`IrokConfigurator.exe`, run it. Done.

<details>
<summary><b>You'll see "Windows protected your PC"</b></summary>

The executable isn't code-signed, so SmartScreen warns about any unsigned program.
Choose **More info → Run anyway**.

Being unsigned is the only reason for the warning. To confirm the file matches
this repository, the release includes a `.sha256.txt` produced by this repo's own
build from the tagged source.
</details>

To remove it: **Settings → Apps → Installed apps → Irok Configurator**, or run
`IrokConfigurator.exe --uninstall`.

## First launch

You'll get the browser's welcome screen. Dismiss it.

Then it asks you to pick your keyboard. Do that. The browser remembers the choice
from then on, so you only see this once.

## What it does

- Adds an entry to your Start menu and desktop
- Opens the configurator in its own window, no tabs and no address bar
- Works with Edge, Chrome, Brave, Opera or Vivaldi, whichever you already have
- Runs the configurator in a separate profile, so extensions like Dark Reader don't
  mess with the interface
- One file, no installer, no admin rights, nothing running in the background, no
  analytics

It does nothing else. There are no keyboard settings in here, and nothing is ever
sent to your keyboard. That all still happens on Irok's site.

## Options

Settings live in a plain text file:

```
%LOCALAPPDATA%\Programs\IrokConfigurator\config.txt
```

| Key | Meaning |
| --- | --- |
| `Url` | Page to open. Update if Irok moves their site. |
| `Preferred` | Browser to try first: `edge`, `chrome`, `brave`, `opera`, `vivaldi`. |
| `SharedProfile` | `true` uses your normal browser profile. Your extensions then apply to the configurator. |
| `DesktopShortcut` | `true` or `false`. |

## Notes

- The Irok web driver is **wired only**, and wants the keyboard on its own USB
  port rather than through an unpowered hub.
- If the configurator ever looks broken, check whether the same page works in a
  normal browser window. That tells you whether it's Irok's site or this launcher.

## Building

Needs only Windows. No Visual Studio, no packages.

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

## Legal

Unofficial community project. Not affiliated with, endorsed by, or supported by
Irok or KBDfans. All trademarks belong to their owners. The configurator is served
by Irok at [hid.irok.cn](https://hid.irok.cn); this project only opens it.
