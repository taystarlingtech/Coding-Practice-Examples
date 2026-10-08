<#
.SYNOPSIS
    Local IT health report: machine facts, disk, auto-start services that
    are stopped, and recent Application/System errors. Writes CSV + HTML
    next to this script.

.DESCRIPTION
    Why this script (vs the other PowerShell files in this folder)
    --------------------------------------------------------------
    NTFS / SharePoint / WSUS scripts need a file server, tenant, or WSUS
    box. Reviewers do not have those. This report runs on any Windows PC
    you can open PowerShell on - including yours.

    That is the same reason the SQL workshop uses SQLite instead of
    Infinium: evidence you can demonstrate.

    Job angle
    ---------
    ICT / desktop / sysadmin interviews often ask "how would you check
    a machine quickly?" This is that answer, in a file you can schedule
    with Task Scheduler and email as CSV.

.NOTES
    Get-CimInstance is the modern replacement for Get-WmiObject.
    Get-WinEvent is the modern replacement for Get-EventLog.

    The Security log is skipped on purpose: it usually needs elevation
    and is a poor default for a portfolio demo. Application + System
    already show whether the box is throwing errors.

    Run:
        powershell -File local_it_health_report.ps1
#>

$ErrorActionPreference = "Continue"

# $PSScriptRoot is the folder this .ps1 lives in, so output does not depend
# on whichever directory you happened to be in when you launched it.
$OutputDir = $PSScriptRoot
$Stamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$CsvPath = Join-Path $OutputDir "health-report.csv"
$HtmlPath = Join-Path $OutputDir "health-report.html"

function Get-DiskRows {
    # DriveType 3 = local disk. 2 is removable, 4 is network, 5 is CD.
    Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DriveType=3" |
        ForEach-Object {
            $sizeGb = if ($_.Size) { [math]::Round($_.Size / 1GB, 1) } else { 0 }
            $freeGb = if ($_.FreeSpace) { [math]::Round($_.FreeSpace / 1GB, 1) } else { 0 }
            $pct = if ($_.Size -and $_.Size -gt 0) {
                [math]::Round(($_.FreeSpace / $_.Size) * 100, 1)
            } else { 0 }

            [pscustomobject]@{
                Section      = "Disk"
                Name         = $_.DeviceID
                Detail       = "NTFS/local volume"
                Status       = "Free $pct%"
                Metric       = "$freeGb GB free / $sizeGb GB"
                CollectedUtc = (Get-Date).ToUniversalTime().ToString("s") + "Z"
            }
        }
}

function Get-StoppedAutoServices {
    # Automatic services that are Stopped are the usual "why is X down?"
    # list. Delayed-auto is still StartType Automatic on some OS builds,
    # so this can include a few false positives - noted in the HTML.
    Get-CimInstance -ClassName Win32_Service -Filter "StartMode='Auto' AND State='Stopped'" |
        Select-Object -First 15 |
        ForEach-Object {
            [pscustomobject]@{
                Section      = "StoppedAutoService"
                Name         = $_.Name
                Detail       = $_.DisplayName
                Status       = $_.State
                Metric       = $_.StartMode
                CollectedUtc = (Get-Date).ToUniversalTime().ToString("s") + "Z"
            }
        }
}

function Get-RecentErrors {
    param(
        [string]$LogName,
        [int]$MaxEvents = 8
    )

    # -ErrorAction SilentlyContinue: a stripped-down Windows SKU may not
    # have the log. Better to skip than to kill the whole report.
    try {
        Get-WinEvent -FilterHashtable @{ LogName = $LogName; Level = 2 } -MaxEvents $MaxEvents -ErrorAction Stop |
            ForEach-Object {
                [pscustomobject]@{
                    Section      = "EventError"
                    Name         = $LogName
                    Detail       = $_.ProviderName
                    Status       = "Error $($_.Id)"
                    Metric       = $_.TimeCreated.ToUniversalTime().ToString("s") + "Z"
                    CollectedUtc = (Get-Date).ToUniversalTime().ToString("s") + "Z"
                }
            }
    }
    catch {
        [pscustomobject]@{
            Section      = "EventError"
            Name         = $LogName
            Detail       = "Could not read log (permissions or missing log)"
            Status       = "Skipped"
            Metric       = $_.Exception.Message
            CollectedUtc = (Get-Date).ToUniversalTime().ToString("s") + "Z"
        }
    }
}

$os = Get-CimInstance -ClassName Win32_OperatingSystem
$cs = Get-CimInstance -ClassName Win32_ComputerSystem

$summary = [pscustomobject]@{
    Section      = "Machine"
    Name         = $cs.Name
    Detail       = $os.Caption
    Status       = "OK"
    Metric       = "Last boot $($os.LastBootUpTime)"
    CollectedUtc = (Get-Date).ToUniversalTime().ToString("s") + "Z"
}

$rows = @()
$rows += $summary
$rows += Get-DiskRows
$stopped = @(Get-StoppedAutoServices)
$rows += $stopped
$rows += Get-RecentErrors -LogName "System"
$rows += Get-RecentErrors -LogName "Application"

# NoTypeInformation keeps Excel from adding a "#TYPE ..." first line.
$rows | Export-Csv -Path $CsvPath -NoTypeInformation -Encoding utf8

$htmlRows = $rows |
    Select-Object Section, Name, Detail, Status, Metric |
    ConvertTo-Html -Title "Local IT health report" -PreContent "<h1>Local IT health report</h1><p>$($cs.Name) - $Stamp</p><p>Stopped automatic services listed: $($stopped.Count) (capped at 15).</p>"

$htmlRows | Out-File -FilePath $HtmlPath -Encoding utf8

Write-Host "Wrote $CsvPath"
Write-Host "Wrote $HtmlPath"
Write-Host "Rows: $($rows.Count)"
