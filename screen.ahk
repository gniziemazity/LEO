#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
Trans := True
^+SPACE::  Winset, Alwaysontop, , A
   return
^+u::
   WinGetPos, X, Y, Width, Height, A
   WinMove, A,, A_ScreenWidth-(1920-550+10), -2, 1920-550+20, 1080+100
   return
^+s::
   WinGetPos, X, Y, Width, Height, A
   WinMove, A,, 0, 0, 1920-300, 1200
   return
^+t::
   IF Trans
      WinSet, Transparent, 150, A
   ELSE
      WinSet, Transparent, OFF, A
   Trans := !Trans
   return
^+Right::
   WinMove, A,, A_ScreenWidth-610, 100, 600, 800
   return
^+Left::
   WinMove, A,, 0, 0, 630, 1080
   return
