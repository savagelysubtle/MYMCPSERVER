# Test-Rename.ps1
# Test script for rename.ps1

# --- Setup ---
# Define paths
$scriptPath = (Get-Item $PSScriptRoot).Parent.Parent.FullName
$renameScriptPath = Join-Path $scriptPath "scripts\renamer\rename.ps1"
$testDir = Join-Path $PSScriptRoot "test_files"
$appDataDir = Join-Path $env:APPDATA "RenameScript"
$configFile = Join-Path $appDataDir "rename_config.txt"

# Ensure the AppData directory for the config exists
if (-not (Test-Path $appDataDir)) {
    New-Item -Path $appDataDir -ItemType Directory -Force | Out-Null
}

# *** Dot-source the script to load its functions ***
. $renameScriptPath

# --- Test Helper Functions ---

# Function to set up the test environment
function Initialize-TestEnvironment {
    Write-Host "Setting up test environment in $testDir..." -ForegroundColor Gray
    # Create test directory if it doesn't exist
    if (-not (Test-Path $testDir)) {
        New-Item -Path $testDir -ItemType Directory -Force | Out-Null
    }
    else {
        # Clean up any existing test files
        Remove-Item -Path "$testDir\*" -Force -Recurse -ErrorAction SilentlyContinue
    }

    # Create test subdirectories
    $subDir1 = Join-Path $testDir "subdir1"
    $subDir2 = Join-Path $testDir "subdir2"
    New-Item -Path $subDir1 -ItemType Directory -Force | Out-Null
    New-Item -Path $subDir2 -ItemType Directory -Force | Out-Null

    # Create test .mdc files
    "Test content 1" | Out-File -FilePath (Join-Path $testDir "test1.mdc") -Force -Encoding UTF8
    "Test content 2" | Out-File -FilePath (Join-Path $testDir "test2.mdc") -Force -Encoding UTF8
    "Test content 3" | Out-File -FilePath (Join-Path $subDir1 "test3.mdc") -Force -Encoding UTF8
    "Test content 4" | Out-File -FilePath (Join-Path $subDir2 "test4.mdc") -Force -Encoding UTF8

    # Create some other file types for testing
    "Test md content" | Out-File -FilePath (Join-Path $testDir "testmd.md") -Force -Encoding UTF8
    "Test txt content" | Out-File -FilePath (Join-Path $testDir "testtxt.txt") -Force -Encoding UTF8

    # Remove config file if it exists
    if (Test-Path $configFile) {
        Remove-Item -Path $configFile -Force
    }

    Write-Host "Test environment set up." -ForegroundColor Gray
}

# Function to clean up the test environment
function Remove-TestEnvironment {
    Write-Host "Cleaning up test environment..." -ForegroundColor Gray
    if (Test-Path $testDir) {
        Remove-Item -Path $testDir -Force -Recurse -ErrorAction SilentlyContinue
    }

    if (Test-Path $configFile) {
        Remove-Item -Path $configFile -Force -ErrorAction SilentlyContinue
    }
    Write-Host "Test environment cleaned up." -ForegroundColor Gray
}

# --- Test Functions ---

# Function to test the Get-SavedDirectoryAppData function
function Test-GetSavedDirectoryAppData {
    Write-Host "Testing Get-SavedDirectoryAppData function..." -ForegroundColor Cyan

    # Test when no config file exists
    if (Test-Path $configFile) {
        Remove-Item -Path $configFile -Force
    }

    # Call the *actual* function from rename.ps1
    $result = Get-SavedDirectoryAppData

    if ($null -eq $result) {
        Write-Host "✅ Get-SavedDirectoryAppData correctly returned null when no config file exists." -ForegroundColor Green
    }
    else {
        Write-Host "❌ Get-SavedDirectoryAppData did not return null when no config file exists. Returned: $result" -ForegroundColor Red
    }

    # Test when config file exists
    $testPath = "C:\TestPath"
    $testPath | Out-File -FilePath $configFile -Force -Encoding UTF8

    # Call the *actual* function again
    $result = Get-SavedDirectoryAppData

    if ($result -eq $testPath) {
        Write-Host "✅ Get-SavedDirectoryAppData correctly returned saved path." -ForegroundColor Green
    }
    else {
        Write-Host "❌ Get-SavedDirectoryAppData did not return the expected saved path. Expected: $testPath, Got: $result" -ForegroundColor Red
    }
}

# Function to test the Save-DirectoryAppData function
function Test-SaveDirectoryAppData {
    Write-Host "Testing Save-DirectoryAppData function..." -ForegroundColor Cyan

    # Remove existing config file
    if (Test-Path $configFile) {
        Remove-Item -Path $configFile -Force
    }

    $testPath = "C:\TestSavePath"

    # Call the *actual* function from rename.ps1
    Save-DirectoryAppData -DirectoryPath $testPath

    if (Test-Path $configFile) {
        $savedContent = (Get-Content $configFile -ErrorAction SilentlyContinue).Trim()
        if ($savedContent -eq $testPath) {
            Write-Host "✅ Save-DirectoryAppData correctly saved the directory path." -ForegroundColor Green
        }
        else {
            Write-Host "❌ Save-DirectoryAppData did not save the expected directory path. Expected: $testPath, Found: $savedContent" -ForegroundColor Red
        }
    }
    else {
        Write-Host "❌ Save-DirectoryAppData did not create the config file at $configFile." -ForegroundColor Red
    }
}

# Function to test file renaming
function Test-RenameFiles {
    Write-Host "Testing Rename-Files function..." -ForegroundColor Cyan

    # --- Test 1: Invalid Directory ---
    Write-Host "  Testing with invalid directory..." -ForegroundColor Gray
    # Call the *actual* function from rename.ps1
    $result = Rename-Files -DirectoryPath "C:\NonExistentDirectory\Path" -FromExt ".mdc" -ToExt ".md"

    if ($result -eq $false) {
        Write-Host "  ✅ Rename-Files correctly returned false for invalid directory." -ForegroundColor Green
    }
    else {
        Write-Host "  ❌ Rename-Files did not return false for invalid directory." -ForegroundColor Red
    }

    # --- Test 2: .mdc to .md ---
    Write-Host "  Testing .mdc to .md conversion..." -ForegroundColor Gray
    # Reset environment for this specific test case
    Initialize-TestEnvironment

    # Call the *actual* function from rename.ps1
    $result = Rename-Files -DirectoryPath $testDir -FromExt ".mdc" -ToExt ".md"

    if ($result -eq $true) {
        Write-Host "  ✅ Rename-Files correctly returned true for valid .mdc -> .md operation." -ForegroundColor Green

        # Verify files were renamed
        $mdcFiles = Get-ChildItem -Path $testDir -Filter "*.mdc" -Recurse -File -ErrorAction SilentlyContinue
        $mdFiles = Get-ChildItem -Path $testDir -Filter "*.md" -Recurse -File -ErrorAction SilentlyContinue
        $otherFiles = Get-ChildItem -Path $testDir -Exclude "*.md", "*.mdc" -Recurse -File -ErrorAction SilentlyContinue

        # Expected counts after renaming .mdc to .md
        $expectedMdcCount = 0
        $initialMdcCount = 4 # As created in Initialize-TestEnvironment
        $initialMdCount = 1  # As created in Initialize-TestEnvironment
        $expectedMdCount = $initialMdcCount + $initialMdCount # All .mdc become .md, plus the original .md
        $initialOtherCount = 1 # The .txt file

        if (($null -eq $mdcFiles -or $mdcFiles.Count -eq $expectedMdcCount) -and ($null -ne $mdFiles -and $mdFiles.Count -eq $expectedMdCount)) {
            Write-Host "  ✅ All .mdc files were successfully renamed to .md. Found $($mdFiles.Count) .md files." -ForegroundColor Green
        }
        else {
            Write-Host "  ❌ File rename verification failed (.mdc -> .md). Expected MDC: $expectedMdcCount (Found: $($mdcFiles.Count)), Expected MD: $expectedMdCount (Found: $($mdFiles.Count))" -ForegroundColor Red
        }
        if ($otherFiles.Count -ne $initialOtherCount) {
            Write-Host "  ❌ Other files were unexpectedly modified/deleted. Expected: $initialOtherCount, Found: $($otherFiles.Count)" -ForegroundColor Red
        }

    }
    else {
        Write-Host "  ❌ Rename-Files did not return true for valid .mdc -> .md operation." -ForegroundColor Red
    }

    # --- Test 3: .md to .mdc ---
    Write-Host "  Testing .md to .mdc conversion..." -ForegroundColor Gray
    # Reset environment - starts with .mdc files again
    Initialize-TestEnvironment

    # First, rename the initial .md file to .mdc as if it was part of the set
    Rename-Item -Path (Join-Path $testDir "testmd.md") -NewName "testmd.mdc" -Force
    # Now, rename ALL .mdc back to .md (preparing for the actual test)
    Rename-Files -DirectoryPath $testDir -FromExt ".mdc" -ToExt ".md" | Out-Null

    # Now perform the actual test: .md -> .mdc
    $result = Rename-Files -DirectoryPath $testDir -FromExt ".md" -ToExt ".mdc"

    if ($result -eq $true) {
        Write-Host "  ✅ Rename-Files correctly returned true for valid .md -> .mdc operation." -ForegroundColor Green

        # Verify files were renamed
        $mdFiles = Get-ChildItem -Path $testDir -Filter "*.md" -Recurse -File -ErrorAction SilentlyContinue
        $mdcFiles = Get-ChildItem -Path $testDir -Filter "*.mdc" -Recurse -File -ErrorAction SilentlyContinue
        $otherFiles = Get-ChildItem -Path $testDir -Exclude "*.md", "*.mdc" -Recurse -File -ErrorAction SilentlyContinue

        # Expected counts after renaming .md to .mdc
        $expectedMdCount = 0
        $initialMdCountAfterPrep = 5 # 4 original + 1 renamed from md
        $expectedMdcCount = $initialMdCountAfterPrep
        $initialOtherCount = 1 # The .txt file

        if (($null -eq $mdFiles -or $mdFiles.Count -eq $expectedMdCount) -and ($null -ne $mdcFiles -and $mdcFiles.Count -eq $expectedMdcCount)) {
            Write-Host "  ✅ All .md files were successfully renamed to .mdc. Found $($mdcFiles.Count) .mdc files." -ForegroundColor Green
        }
        else {
            Write-Host "  ❌ File rename verification failed (.md -> .mdc). Expected MD: $expectedMdCount (Found: $($mdFiles.Count)), Expected MDC: $expectedMdcCount (Found: $($mdcFiles.Count))" -ForegroundColor Red
        }
        if ($otherFiles.Count -ne $initialOtherCount) {
            Write-Host "  ❌ Other files were unexpectedly modified/deleted. Expected: $initialOtherCount, Found: $($otherFiles.Count)" -ForegroundColor Red
        }
    }
    else {
        Write-Host "  ❌ Rename-Files did not return true for valid .md -> .mdc operation." -ForegroundColor Red
    }

    # --- Test 4: No matching files ---
    Write-Host "  Testing with no matching files..." -ForegroundColor Gray
    # Reset environment
    Initialize-TestEnvironment

    $result = Rename-Files -DirectoryPath $testDir -FromExt ".nonexistent" -ToExt ".whatever"
    if ($result -eq $true) {
        Write-Host "  ✅ Rename-Files correctly returned true when no matching files are found." -ForegroundColor Green
    }
    else {
        Write-Host "  ❌ Rename-Files did not return true when no matching files were found." -ForegroundColor Red
    }
}


# --- Test Execution ---

# Function to run all tests
function Invoke-AllTests {
    Write-Host "Running all tests for rename.ps1..." -ForegroundColor Yellow

    # Run setup once initially for config tests
    Initialize-TestEnvironment

    Test-GetSavedDirectoryAppData
    Test-SaveDirectoryAppData

    # Cleanup after config tests, Rename test handles its own setup/cleanup per case
    Remove-TestEnvironment

    # Run the rename tests (includes setup/cleanup within)
    Test-RenameFiles

    Write-Host "All tests completed." -ForegroundColor Yellow
}

# Run all tests
Invoke-AllTests