[CmdletBinding()]
param (
  [Parameter(Mandatory = $false)]
  [string]$ProjectRoot = "D:\Coding\Python_Projects\MYMCPSERVER",

  [Parameter(Mandatory = $false)]
  [string]$DocsFolder = "docs-obsidian",

  [Parameter(Mandatory = $false)]
  [switch]$DryRun,

  [Parameter(Mandatory = $false)]
  [switch]$NoConfirm
)

# --- INITIALIZATION ---
# Set up logging
$LogFile = Join-Path -Path $ProjectRoot -ChildPath "movedocs_log.txt"
$OperationsCount = @{
  "DirectoriesCreated" = 0
  "FilesRenamed"       = 0
  "FilesMoved"         = 0
}

# Helper function for logging
function Write-LogMessage {
  param (
    [Parameter(Mandatory = $true)]
    [string]$Message,

    [Parameter(Mandatory = $false)]
    [string]$Color = "White"
  )

  $TimeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  $LogMessage = "[$TimeStamp] $Message"

  # Output to console
  Write-Host $LogMessage -ForegroundColor $Color

  # Output to log file
  Add-Content -Path $LogFile -Value $LogMessage
}

# Define the base path for documentation
$DocsPath = Join-Path -Path $ProjectRoot -ChildPath $DocsFolder
# Define the dump path for old/redundant files
$DumpPath = Join-Path -Path $DocsPath -ChildPath "userDump"

Write-LogMessage "Script started with parameters:" -Color Cyan
Write-LogMessage "  Project Root: $ProjectRoot" -Color Cyan
Write-LogMessage "  Docs Folder: $DocsFolder" -Color Cyan
Write-LogMessage "  Docs Path: $DocsPath" -Color Cyan
Write-LogMessage "  Dry Run: $DryRun" -Color Cyan
if ($DryRun) {
  Write-LogMessage "RUNNING IN DRY RUN MODE - No changes will be made" -Color Yellow
}

# --- STEP 1: Create New Core Directories ---
Write-LogMessage "Creating new core directories..." -Color Yellow
$CoreDirectories = @(
  $DumpPath,
    (Join-Path -Path $DocsPath -ChildPath "languages\python"),
    (Join-Path -Path $DocsPath -ChildPath "languages\typescript"),
    (Join-Path -Path $DocsPath -ChildPath "projects\myMcpServer")
)

foreach ($dir in $CoreDirectories) {
  if (-not (Test-Path -Path $dir -PathType Container)) {
    if (-not $DryRun) {
      New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    Write-LogMessage "Created directory: $dir" -Color Green
    $OperationsCount.DirectoriesCreated++
  }
  else {
    Write-LogMessage "Directory already exists: $dir" -Color Gray
  }
}

# --- STEP 2: Create New Language Category Directories ---
Write-LogMessage "Creating language category directories..." -Color Yellow
$LanguageCategories = "core-concepts", "best-practices", "testing", "libraries-frameworks", "common-error-fixing"
$Languages = "python", "typescript"
foreach ($lang in $Languages) {
  foreach ($category in $LanguageCategories) {
    $dir = Join-Path -Path $DocsPath -ChildPath "languages\$lang\$category"
    if (-not (Test-Path -Path $dir -PathType Container)) {
      if (-not $DryRun) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
      }
      Write-LogMessage "Created directory: $dir" -Color Green
      $OperationsCount.DirectoriesCreated++
    }
    else {
      Write-LogMessage "Directory already exists: $dir" -Color Gray
    }
  }
}

# --- STEP 3: Ensure Subdirectory Structure and Indices ---
# ... (keep the rest of your script with similar modifications)
# ... add logging and dry run checks to each operation

# --- STEP 4: Rename Core Files ---
Write-LogMessage "Renaming core files..." -Color Yellow
$RenamePairs = @{
    (Join-Path -Path $DocsPath -ChildPath "Home.md")                       = "_index.md";
    (Join-Path -Path $DocsPath -ChildPath "docsGuide\templates\README.md") = "_index.md";
}
foreach ($pair in $RenamePairs.GetEnumerator()) {
  if (Test-Path -Path $pair.Key -PathType Leaf) {
    try {
      if (-not $DryRun) {
        Rename-Item -Path $pair.Key -NewName $pair.Value -ErrorAction Stop
      }
      Write-LogMessage "Renamed '$($pair.Key)' to '$($pair.Value)'" -Color Green
      $OperationsCount.FilesRenamed++
    }
    catch {
      Write-LogMessage "Failed to rename '$($pair.Key)': $_" -Color Red
    }
  }
  else {
    Write-LogMessage "File not found, skipping rename: $($pair.Key)" -Color Yellow
  }
}

# --- STEP 5: Move Old MOCs and READMEs to userDump ---
Write-LogMessage "Moving old MOCs and READMEs to '$DumpPath'..." -Color Yellow
$FilesToDump = @(
  # Top Level MOCs (excluding Fleeting MOC for now)
  "Concepts MOC.md",
  "MCP MOC.md",
  "Processes MOC.md",
  "Project MOC.md",
  "Reference MOC.md",
  "Tech MOC.md",
  # Subdirectory MOCs/READMEs
  "generalKnowledge\README.md",
  "generalKnowledge\General Knowledge MOC.md",
  "languages\python\Python MOC.md",
  "languages\typescript\TypeScript MOC.md",
  "mcpKnowledge\README.md",
  "mcpKnowledge\MCP Knowledge MOC.md",
  "projects\myMcpServer\README.md",
  "projects\myMcpServer\Project MOC.md",
  # Optional removals (uncomment if desired)
  # "lists\_index.md",
  # "tags\_index.md",
  "docsGuide\templates\MOC Template.md" # Delete MOC template
)

foreach ($file in $FilesToDump) {
  $SourcePath = Join-Path -Path $DocsPath -ChildPath $file
  if (Test-Path -Path $SourcePath -PathType Leaf) {
    try {
      if (-not $DryRun) {
        Move-Item -Path $SourcePath -Destination $DumpPath -ErrorAction Stop
      }
      Write-LogMessage "Moved '$SourcePath' to '$DumpPath'" -Color Green
      $OperationsCount.FilesMoved++
    }
    catch {
      Write-LogMessage "Failed to move '$SourcePath': $_" -Color Red
    }
  }
  else {
    Write-LogMessage "File not found, skipping move: $SourcePath" -Color Yellow
  }
}

# --- STEP 6: Summary and Confirmation ---
Write-LogMessage "-----------------------------------------" -Color Green
Write-LogMessage "Dry Run Summary:" -Color Cyan
Write-LogMessage "- Directories to create: $($OperationsCount.DirectoriesCreated)" -Color Cyan
Write-LogMessage "- Files to rename: $($OperationsCount.FilesRenamed)" -Color Cyan
Write-LogMessage "- Files to move: $($OperationsCount.FilesMoved)" -Color Cyan
Write-LogMessage "-----------------------------------------" -Color Green

# If in dry run mode, prompt for confirmation
if ($DryRun -and -not $NoConfirm) {
  $confirmation = Read-Host "Do you want to execute these operations? (y/n)"
  if ($confirmation -eq 'y') {
    Write-LogMessage "User confirmed execution. Running operations..." -Color Green
    # Re-run the script without dry run
    $scriptPath = $MyInvocation.MyCommand.Path
    & $scriptPath -ProjectRoot $ProjectRoot -DocsFolder $DocsFolder -NoConfirm
    exit
  }
  else {
    Write-LogMessage "User cancelled execution. Exiting..." -Color Yellow
    exit
  }
}

# If not in dry run mode and executing changes
if (-not $DryRun) {
  Write-LogMessage "-----------------------------------------" -Color Green
  Write-LogMessage "Directory restructuring script complete." -Color Green
  Write-LogMessage "-----------------------------------------" -Color Green
  Write-LogMessage "NEXT STEPS:" -Color Yellow
  Write-LogMessage "1. Manually review the '$DumpPath' folder."
  Write-LogMessage "2. Copy relevant overview/linking content from the dumped files into the corresponding new '_index.md' files."
  Write-LogMessage "3. Delete files from '$DumpPath' once content is merged."
  Write-LogMessage "4. Update the frontmatter (especially the 'up' field) in all moved/existing files and the new '_index.md' files to reflect the new hierarchy."
  Write-LogMessage "5. Update the content of 'docsGuide/templates/Note Template.md' and create 'docsGuide/templates/_index Template.md' with the new standard structure."
  Write-LogMessage "6. Review and update the linking guides in 'docsGuide/'."
  Write-LogMessage "7. Configure your Obsidian Breadcrumbs plugin settings (e.g., hierarchy fields, typed link relationships)."
}