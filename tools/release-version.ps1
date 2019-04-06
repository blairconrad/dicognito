[CmdletBinding()]
Param (
    [string]$NewVersion = $(throw "NewVersion is required")
)

# ------------------------------------------------------------------------------
$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot.Parent

try {
    $releaseNotesFile = Resolve-Path src/dicognito/release_notes.md
    $branchName = "release/$NewVersion"

    Write-Host "Releasing version $NewVersion"

    git checkout master
    git pull --ff-only origin master
    git checkout --quiet -b $branchName master

    $releaseNotesContent = [System.IO.File]::ReadAllText($releaseNotesFile)
    $releaseNotesContent = ("## $NewVersion`r`n`r`n" + $releaseNotesContent)
    [System.IO.File]::WriteAllText($releaseNotesFile, $releaseNotesContent)

    Write-Host "`r`nReleasing version $NewVersion. Changing $releaseNotesFile like so:`r`n"
    git diff $releaseNotesFile
    $response = Read-Host "`r`n  Proceed (y/N)?"
    Switch ($response) {
        y { }
        n { Write-Host "Update cancelled. Clean up yourself."; return }
        Default { Write-Host "Unknown response '$response'. Aborting."; return }
    }

    git commit --quiet --message "Set version to $NewVersion" $releaseNotesFile
    git checkout --quiet master
    git merge --quiet --no-ff $branchName
    git branch -D $branchName

    git tag $NewVersion
    git push origin $NewVersion master
}
finally {
    Pop-Location
}