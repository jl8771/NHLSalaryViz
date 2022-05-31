#! /usr/bin/pwsh

param(
    [Parameter()]
    [String]$season_to_edit
)

Write-Output "Editing $season_to_edit"

Write-Output "Starting Extract & Transform Phase"

python3 NHLAPIETL.py $season_to_edit

Write-Output "Completed Extract & Transform Phase"

Write-Output "Started Load Phase"

python3 "NHLCombineStats.py"

Write-Output "Completed Load Phase"