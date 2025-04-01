# Updated rename.ps1
# This script supports bidirectional conversion:
#    .mdc -> .md   OR   .md -> .mdc
#
# It now:
# - Prompts the user to enter 1 or 2 for the conversion type.
# - Prompts for a directory to scan.
# - Saves the chosen directory in the user's AppData folder (to avoid cluttering your project folder).
# - Uses retro console colors (dark magenta, magenta, cyan) for messages.
# - Includes error handling.

# --- Function Definitions ---

# Save config to a folder in the user's AppData folder
$global:appDataDir = Join-Path $env:APPDATA "RenameScript" # Use global scope for visibility in tests
if (-not (Test-Path $global:appDataDir)) {
    New-Item -Path $global:appDataDir -ItemType Directory | Out-Null
}
$global:configFile = Join-Path $global:appDataDir "rename_config.txt"

function Get-SavedDirectoryAppData {
    if (Test-Path $global:configFile) {
        return (Get-Content $global:configFile -ErrorAction SilentlyContinue).Trim()
    }
    return $null
}

function Save-DirectoryAppData {
    param(
        [string]$DirectoryPath
    )
    # Ensure the directory exists before saving the path
    $configDir = Split-Path $global:configFile -Parent
    if (-not (Test-Path $configDir)) {
        New-Item -Path $configDir -ItemType Directory -Force | Out-Null
    }
    $DirectoryPath | Out-File -FilePath $global:configFile -Force -Encoding UTF8
    Write-Host "Directory path saved for future use." -ForegroundColor Cyan
}

function Rename-Files {
    param(
        [string]$DirectoryPath,
        [string]$FromExt,
        [string]$ToExt
    )
    if (-not (Test-Path $DirectoryPath)) {
        Write-Host "Error: Directory not found. Please enter a valid directory path." -ForegroundColor Red
        return $false
    }

    try {
        # Get all files with the extension (recursively)
        $files = Get-ChildItem -Path $DirectoryPath -Filter "*$FromExt" -Recurse -File
        if ($files.Count -eq 0) {
            Write-Host "No files with extension $FromExt found in the specified directory." -ForegroundColor Yellow
            return $true # Not an error if no files found
        }
        $renamedCount = 0
        foreach ($file in $files) {
            # Properly construct the new file name by replacing just the extension
            $newName = $file.BaseName + $ToExt
            Rename-Item -Path $file.FullName -NewName $newName -Force
            $renamedCount++
        }
        Write-Host "Successfully renamed $renamedCount file(s) from $FromExt to $ToExt" -ForegroundColor Cyan
        return $true
    }
    catch {
        Write-Host "Error during rename operation: $_" -ForegroundColor Red
        Write-Host "Details: $($_.ScriptStackTrace)" -ForegroundColor Red
        return $false
    }
}


# --- Main script execution logic ---
# Only run when script is executed directly
if ($MyInvocation.MyCommand.CommandType -eq 'ExternalScript') {

    # --- Conversion Type Selection ---
    Write-Host "Select conversion type:" -ForegroundColor DarkMagenta
    Write-Host "1. Convert .mdc files to .md files" -ForegroundColor Magenta
    Write-Host "2. Convert .md files to .mdc files" -ForegroundColor DarkMagenta

    $conversionInput = Read-Host "Enter your selection (1 or 2)"

    if ($conversionInput -eq "1") {
        $extensionFrom = ".mdc"
        $extensionTo = ".md"
        $conversionMsg = "Renaming from .mdc to .md"
    }
    elseif ($conversionInput -eq "2") {
        $extensionFrom = ".md"
        $extensionTo = ".mdc"
        $conversionMsg = "Renaming from .md to .mdc"
    }
    else {
        Write-Host "Invalid selection. Exiting." -ForegroundColor Red
        exit 1 # Use non-zero exit code for error
    }

    Write-Host $conversionMsg -ForegroundColor Blue

    # --- Directory Selection and Saving Preference ---
    $savedDir = Get-SavedDirectoryAppData
    if ($savedDir) {
        Write-Host "Found saved directory: $savedDir" -ForegroundColor Magenta
        $response = Read-Host "Do you want to use this directory? (y/n)"
        if ($response.ToLower() -eq 'y') {
            $directoryPath = $savedDir
        }
        else {
            $directoryPath = Read-Host "Please enter the full path to the directory you want to scan"
        }
    }
    else {
        $directoryPath = Read-Host "Please enter the full path to the directory you want to scan"
    }

    # Save the directory if it's new or changed
    if ($directoryPath -ne $savedDir) {
        $saveResponse = Read-Host "Do you want to save this directory for future use? (y/n)"
        if ($saveResponse.ToLower() -eq 'y') {
            # Call the function to save
            Save-DirectoryAppData -DirectoryPath $directoryPath
        }
    }

    Write-Host "Scanning directory: $directoryPath" -ForegroundColor Cyan

    # --- Execute Renaming ---
    $result = Rename-Files -DirectoryPath $directoryPath -FromExt $extensionFrom -ToExt $extensionTo

    # --- Report Outcome ---
    if ($result) {
        Write-Host "Operation completed successfully." -ForegroundColor Cyan
        exit 0 # Success
    }
    else {
        Write-Host "Operation failed." -ForegroundColor Red
        exit 1 # Failure
    }
}
