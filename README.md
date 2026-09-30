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

Direct access to the [Irok web software](https://hid.irok.cn).

The Irok driver lives in a browser tab, so reaching it means opening a browser and
finding the page. This saves you those steps: one shortcut and the configurator is
open, in its own window.

It only launches. Keyboard settings aren't touched here and nothing is sent to
your keyboard — that all still happens on Irok's site.

### Why I made it

I use Firefox, and the Irok software needs a browser feature that Firefox doesn't
have, so for me every change meant opening a second browser, navigating, and
closing it again. Switching profiles a few times a day, that adds up.

That's specific to my setup. If you already have a compatible browser open and
remember the address, this saves you a handful of clicks.

## What you get

- A Start menu and desktop entry
- The configurator in its own window, with no tabs or address bar
- Works with Edge, Chrome, Brave, Opera or Vivaldi, whichever you already have
- A separate browser profile, so extensions like Dark Reader don't interfere with
  the interface
- One file, no installer, no admin rights, no background process, no analytics

## Install

Grab `IrokConfigurator-v1.0.0.zip` from the
[releases page](https://github.com/zxkodas/irok-configurator/releases), extract
`IrokConfigurator.exe`, run it.

On first launch the browser shows its welcome screen, then asks you to select your
keyboard. Dismiss the first and pick your keyboard in the second. The browser
remembers the choice, so it won't ask again.

To remove it: **Settings → Apps → Installed apps → Irok Configurator**, or run
`IrokConfigurator.exe --uninstall`.

<details>
<summary><b>You'll see "Windows protected your PC"</b></summary>

The executable isn't code-signed, so SmartScreen warns about any unsigned
program. Choose **More info → Run anyway**.

Being unsigned is the only reason for the warning. To confirm the file matches
this repository, the release includes a `.sha256.txt` produced by this repo's own
build from the tagged source.
</details>

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

- The Irok web driver is **wired only**, and needs the keyboard on its own USB
  port rather than through an unpowered hub.
- If the configurator ever looks broken, check whether the same page works in a
  normal browser window. That distinguishes a problem with Irok's site from a
  problem with this launcher.

## Building

Requires only Windows. No Visual Studio, no packages.

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

## Legal

Unofficial community project. Not affiliated with, endorsed by, or supported by
Irok or KBDfans. All trademarks belong to their owners. The configurator is served
by Irok at [hid.irok.cn](https://hid.irok.cn); this project only opens it.
