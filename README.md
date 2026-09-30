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

A launcher for the [Irok web software](https://hid.irok.cn).

Unofficial, and not made by Irok. It only opens their page.

## What it does

Like most peripheral brands now, Irok ships a single web-based software option
instead of an installable program. That saves resources and is practical compared
to an installer, but it costs you in the day-to-day: to adjust something you open
a browser, find the page, connect your keyboard, and change what you want to
change. This turns that into one shortcut on your Start menu and your Desktop,
which opens the web driver in a window of its own. No need to open a new browser
tab.

It holds no keyboard settings and never sends anything to your keyboard. Irok's
site does all of that, and this only gets you there.

### What it runs

There's no interface of its own. When you open it, it looks for a browser you
already have — Edge, Chrome, Brave, Opera or Vivaldi, in that order — and asks it
to open the Irok page in a dedicated window, without tabs or an address bar.

It also hands that window its own browser profile, kept in a separate folder.
That's what keeps extensions like Dark Reader from changing how the configurator
looks. You can change the browser order, or turn the separate profile off, in
`config.txt`. See **Options**.

### Why I made it

I use Firefox, and sadly, Irok's software doesn't support it. It reaches your
keyboard over **WebHID**, an API that only Chromium browsers implement, so it
can't run in Firefox. Every time I wanted to switch a profile, the routine was:
open Chrome, navigate, make the change, close it again. A few times a day, and it
added up. I wanted it to behave like a normal app so I wouldn't need to open
another browser, so I made one.

If you're already on a compatible browser, this saves fewer clicks than it did
for me, but it makes the web driver feel more integrated into your system,
without it necessarily being so.

## Install

Download the `.zip` from the [latest release](https://github.com/zxkodas/irok-configurator/releases/latest)
and extract it. You'll get a single file called `IrokConfigurator.exe`.

Double-click it. That's the whole installation. It copies itself into
`%LOCALAPPDATA%\Programs\IrokConfigurator`, adds a Start menu entry, and opens
the configurator.

**Windows will probably warn you.** You'll get a blue window saying *Windows
protected your PC* and offering *More info*. Click **More info**, then **Run
anyway**.

That warning is expected. Windows shows it for any program that isn't signed with
a paid certificate, and this one isn't, because signing costs money that a free
open-source tool doesn't have. Nothing is wrong with the file.

The release also includes a `.sha256.txt`, and it's worth knowing what it does and
doesn't prove. It confirms the file you downloaded is the same one this build
produced, which rules out a corrupted or tampered download. It does not confirm
anything on its own: the checksum is published by the same build that produced the
binary, so if you don't already trust this repository and GitHub, verifying against
it tells you nothing new. That check only matters if you already had a reason to
trust the source.

## Uninstall

Open Windows Settings, go to **Apps**, and find **Irok Configurator** in the list.
On Windows 11 it's under *Installed apps*; on Windows 10 it's *Apps & features*.
Click it and choose Uninstall.

It removes the launcher, its icon, and its separate browser profile. Your regular
browser profile is left completely untouched.

**Export your profiles before uninstalling.** Keyboard profiles are stored in the
browser profile, which is the folder this removes, so anything you created in the
configurator goes with it. Open the configurator, use its export function, and
save the file somewhere outside the launcher before you uninstall. You can import
it again later from any browser.

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

## Options

Settings live in a plain text file:

```
%LOCALAPPDATA%\Programs\IrokConfigurator\config.txt
```

| Key | Default | Meaning |
| --- | --- | --- |
| `Url` | `https://hid.irok.cn` | Page to open. Update if Irok moves their site. |
| `Preferred` | `edge` | Browser to try first: `edge`, `chrome`, `brave`, `opera`, `vivaldi`. It falls back to the others if that one isn't installed. |
| `SharedProfile` | `false` | `true` uses your normal browser profile. Your existing profiles show up without importing, but your extensions then apply to the configurator too. |
| `DesktopShortcut` | `true` | Whether to keep the shortcut on your desktop. |

To edit it, open the file with Notepad or any text editor, change the value, save,
and reopen the launcher. Delete the file to go back to the defaults.

## If something goes wrong

**The configurator looks broken.** Open `https://hid.irok.cn` in your normal
browser. If it looks the same there, the problem is on Irok's side rather than
this launcher.

**The keyboard doesn't show up in the device list.** Unplug it, plug it back into
a different port, and wait a few seconds. Check that the cable is seated at both
ends, and try the port the keyboard came with.

**Your profiles are gone.** They live in the browser that created them, and this
launcher uses a separate one. See **First launch** for how to bring them over. If
you already uninstalled, they're gone for good — export them next time before
removing anything.

**Nothing happens when you click it.** Open `%LOCALAPPDATA%\Programs\IrokConfigurator\IrokConfigurator.log`.
It records which browser got picked and the exact command line used, which is
usually enough to see what went wrong.

**It picks the wrong browser.** Set `Preferred` in `config.txt` to the one you
want. See **Options**.

**Antivirus removed the file.** Some security software removes unsigned programs
that install themselves. Allow it, or download again and run the uninstall
command to clean up what's left.

## Building

Needs only Windows. No Visual Studio, no packages.

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

## Legal

Unofficial community project. Not affiliated with, endorsed by, or supported by
Irok or KBDfans. All trademarks belong to their owners. The configurator is served
by Irok at [hid.irok.cn](https://hid.irok.cn); this project only opens it.
