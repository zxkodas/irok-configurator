<div align="center">
  <img src="docs/hero.png" alt="Irok Configurator launcher" width="100%">
</div>

<div align="center">

[![Release](https://img.shields.io/github/v/release/zxkodas/irok-configurator?style=flat-square&label=release&color=ff6b4a)](https://github.com/zxkodas/irok-configurator/releases/latest)
[![CI](https://github.com/zxkodas/irok-configurator/actions/workflows/build.yml/badge.svg)](https://github.com/zxkodas/irok-configurator/actions/workflows/build.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Windows 10/11](https://img.shields.io/badge/windows-10%20%7C%2011-0078d6?style=flat-square&logo=windows)](https://learn.microsoft.com/en-us/windows/release-health/windows-11-release-information)
[![Size](https://img.shields.io/badge/size-26%20KB-success?style=flat-square)](https://github.com/zxkodas/irok-configurator/releases/latest)

</div>

# Irok Configurator

A launcher for the [Irok web software](https://hid.irok.cn). It saves you a few
clicks every time you want to change something on your keyboard.

## Install

Download the `.zip` from the [latest release](https://github.com/zxkodas/irok-configurator/releases/latest)
and extract it. You'll get a single file called `IrokConfigurator.exe`.

Double-click it. That's the whole installation. It copies itself into your user
folder, adds a Start menu entry, and opens the configurator.

**Windows will probably warn you.** You'll get a blue window saying *Windows
protected your PC* and offering *More info*. Click **More info**, then **Run
anyway**.

That warning is expected. Windows shows it for any program that isn't signed with
a paid certificate, and this one isn't, because signing costs money that a free
open-source tool doesn't have. Nothing is wrong with the file. If you'd rather
check before you run it, the release also includes a `.sha256.txt` — compare it
against the zip and you're looking at the same build that came out of this
repository.

## Uninstall

Open Windows Settings, go to **Apps**, and find **Irok Configurator** in the list.
On Windows 11 it's under *Installed apps*; on Windows 10 it's *Apps & features*.
Click it and choose Uninstall.

It removes the launcher, its icon, and its separate browser profile. It leaves
your regular browser profile completely untouched.

If you'd rather do it from a terminal, the launcher cleans up after itself:

```
IrokConfigurator.exe --uninstall
```

## First launch

You'll get the browser's welcome screen. Dismiss it.

Then it asks you to pick your keyboard. Do that. The browser remembers the choice
from then on, so you only see this once.

**You won't have your old profiles.** Profiles live in the browser that created
them, and this launcher runs the configurator in its own profile so extensions
can't get in the way. A fresh profile starts empty.

If you've already built profiles somewhere else, they're still there. Open the
configurator in that other browser once, use its export function to save them to a
file, then import that file from the launcher. Everything shows up where you left
it, and it stays from then on.

## What it does

The Irok software is a web app. Reaching it means opening a browser, finding the
page, connecting your keyboard and picking a profile. This turns that into a
shortcut on your Start menu that opens the configurator in a window of its own.

Under the hood it's a launcher and nothing more. It picks a browser you already
have and gets out of the way. It holds no keyboard settings and never sends
anything to your keyboard — Irok's site does that part.

### Why I made it

I use Firefox. The Irok software reaches the keyboard over **WebHID**, an API that
only Chromium browsers implement, so for me it couldn't run in the browser I
actually use. Every time I wanted to switch a profile, the routine was: open
Chrome, navigate, change it, close it again. A few times a day, and it added up.

For anyone on a compatible browser, this saves fewer clicks than it did for me.
It exists because I wanted the thing to behave like an app instead of a detour.

## Options

Settings live in a plain text file:

```
%LOCALAPPDATA%\Programs\IrokConfigurator\config.txt
```

| Key | Meaning |
| --- | --- |
| `Url` | Page to open. Update if Irok moves their site. |
| `Preferred` | Browser to try first: `edge`, `chrome`, `brave`, `opera`, `vivaldi`. |
| `SharedProfile` | `true` uses your normal browser profile. Your existing profiles show up without importing, but your extensions then apply to the configurator too. |
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
