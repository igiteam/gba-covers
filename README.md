# N64 Covers

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

A collection of N64 covers for use with emulators. This repository serves as a centralized database of N64 game cover art specifically designed to work with the new QT-based version of Project64, [P64-QT](https://github.com/IanSkelskey/p64-qt).

## Label Examples

<div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 15px;">
  <img src="default-label.png" alt="Default Label" width="180" height="auto">
  <img src="./labels/NUS-NDYE-USA-1.png" alt="Diddy Kong Racing" width="180" height="auto">
  <img src="./labels/NUS-CZLE-USA.png" alt="Legend of Zelda: Ocarina of Time" width="180" height="auto">
  <img src="./labels/NUS-NKTE-USA.png" alt="Mario Kart 64" width="180" height="auto">
  <img src="./labels/NUS-NFXE-USA-1.png" alt="Star Fox 64" width="180" height="auto">
  <img src="./labels/NUS-NSME-USA.png" alt="Super Mario 64" width="180" height="auto">
  <img src="./labels/NUS-NPFE-USA.png" alt="Pokemon Snap" width="180" height="auto">
  <img src="./labels/NUS-NMXE-USA.png" alt="Excitebike 64" width="180" height="auto">
  <img src="./labels/NUS-NMKE-USA.png" alt="Mortal Kombat Trilogy" width="180" height="auto">
</div>

## Box Examples

<div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 15px;">
  <img src="./covers/NUS-NDOE-USA.png" alt="Donkey Kong 64" width="300" height="auto">
  <img src="./covers/NUS-NTFE-USA.png" alt="Tony Hawk's Pro Skater" width="300" height="auto">
  <img src="./covers/NUS-NWGE-USA.png" alt="Wayne Gretzky's 3D Hockey" width="300" height="auto">
</div>

<!-- BEGIN N64 SUMMARY -->

## Progress Summary by Region

| Region                                                                                         | Label Art                                         | Box Art                                           |
| ---------------------------------------------------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------- |
| <img src='https://cdn.jsdelivr.net/gh/lipis/flag-icons/flags/4x3/us.svg' width='30'> USA       | <img alt="28%" src="https://progress-bar.xyz/28"> | <img alt="31%" src="https://progress-bar.xyz/31"> |
| <img src='https://cdn.jsdelivr.net/gh/lipis/flag-icons/flags/4x3/eu.svg' width='30'> Europe    | <img alt="4%" src="https://progress-bar.xyz/4">   | <img alt="0%" src="https://progress-bar.xyz/0">   |
| <img src='https://cdn.jsdelivr.net/gh/lipis/flag-icons/flags/4x3/jp.svg' width='30'> Japan     | <img alt="7%" src="https://progress-bar.xyz/7">   | <img alt="0%" src="https://progress-bar.xyz/0">   |
| <img src='https://cdn.jsdelivr.net/gh/lipis/flag-icons/flags/4x3/de.svg' width='30'> Germany   | <img alt="0%" src="https://progress-bar.xyz/0">   | <img alt="0%" src="https://progress-bar.xyz/0">   |
| <img src='https://cdn.jsdelivr.net/gh/lipis/flag-icons/flags/4x3/fr.svg' width='30'> France    | <img alt="4%" src="https://progress-bar.xyz/4">   | <img alt="0%" src="https://progress-bar.xyz/0">   |
| <img src='https://cdn.jsdelivr.net/gh/lipis/flag-icons/flags/4x3/it.svg' width='30'> Italy     | <img alt="0%" src="https://progress-bar.xyz/0">   | <img alt="0%" src="https://progress-bar.xyz/0">   |
| <img src='https://cdn.jsdelivr.net/gh/lipis/flag-icons/flags/4x3/es.svg' width='30'> Spain     | <img alt="0%" src="https://progress-bar.xyz/0">   | <img alt="0%" src="https://progress-bar.xyz/0">   |
| <img src='https://cdn.jsdelivr.net/gh/lipis/flag-icons/flags/4x3/au.svg' width='30'> Australia | <img alt="37%" src="https://progress-bar.xyz/37"> | <img alt="0%" src="https://progress-bar.xyz/0">   |

<!-- END N64 SUMMARY -->

## Project64 QT Redesign

I am currently working on redesigning Project64 with a QT framework frontend. The project is currently in **early development** stage and is not yet a working emulator, but rather a foundational UI framework that will eventually connect to the Project64 emulation core.

Features planned for P64-QT include:

- Cover grid view (already implemented)
- Integrated cover downloader (planned)
- Modern Qt-based interface with better scaling and theming

You can find the QT redesign project here: [P64-QT Repository](https://github.com/IanSkelskey/p64-qt)

## Cover Grid View

The new Project64 QT version features a grid view that displays game covers:

![Project64 QT Demo GIF](https://raw.githubusercontent.com/IanSkelskey/p64-qt/main/Screenshots/demo.gif)

## Cover Naming Convention

For proper detection in Project64-QT, all cover images must be named according to the game's full cartridge ID code. This is the complete code found on the N64 cartridge label (e.g., NUS-NFXE-USA-1).

### Where to Find the Cartridge Code

_Screenshots showing where to find the full cartridge code on N64 cartridges will be added here._

### Examples

Below are some examples of how to name cover files based on the cartridge code:

| Game                             | Cartridge Code | Cover Filename     |
| -------------------------------- | -------------- | ------------------ |
| Diddy Kong Racing                | NUS-NDYE-USA-1 | NUS-NDYE-USA-1.png |
| Legend of Zelda: Ocarina of Time | NUS-CZLE-USA   | NUS-CZLE-USA.png   |
| Mario Kart 64                    | NUS-NKTE-USA   | NUS-NKTE-USA.png   |
| Star Fox 64                      | NUS-NFXE-USA-1 | NUS-NFXE-USA-1.png |
| Super Mario 64                   | NUS-NSME-USA   | NUS-NSME-USA.png   |
| Pokemon Snap                     | NUS-NPFE-USA   | NUS-NPFE-USA.png   |

## Contributing

If you'd like to contribute covers to this repository, please read our [contribution guidelines](CONTRIBUTING.md).
