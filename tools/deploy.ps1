# Adapted from PEP 440:
# https://www.python.org/dev/peps/pep-0440/#appendix-b-parsing-version-strings-with-regular-expressions
$preReleaseRegex = "([-_\.]?(a|b|c|rc|alpha|beta|pre|preview)[-_\.]?[0-9]*)"

Push-Location (Get-Item $PSScriptRoot).Parent.FullName

try {
    Write-Output "Installing twine"
    # pip issues a warning on stdout about Python2.7 soon being deprecated.
    # This breaks the build, so don't stop on errors until after.
    pip install --quiet --quiet twine

    $ErrorActionPreference = "Stop"

    if (! $env:APPVEYOR_REPO_TAG_NAME) {
        Write-Output "No Appveyor tag name supplied. Not deploying."
        return
    }

    $releaseName = $env:APPVEYOR_REPO_TAG_NAME
    $gitHubAuthToken = $env:GITHUB_TOKEN
    $repo = $env:APPVEYOR_REPO_NAME

    $releaseNotesFile = 'release_notes.md'
    # Use Tls12 to communicate with GitHub
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

    $artifactsPattern = "dist/*"
    $releasesUrl = "https://api.github.com/repos/$repo/releases"
    $headers = @{
        "Authorization" = "Bearer $gitHubAuthToken"
        "Content-type"  = "application/json"
    }

    Write-Output "Deploying $releaseName"

    $releaseNotes = Get-Content -Encoding UTF8 $releaseNotesFile
    if (!$releaseNotes[0].StartsWith('## ')) {
        throw "$releaseNotesFile doesn't start with a release. First line is '$($releaseNotes[0])'"
    }

    $releaseNotesVersion = $releaseNotes[0].SubString(3)
    if ($releaseNotesVersion -ne $releaseName) {
        throw "Release notes version '$releaseNotesVersion' does not match release name from tag '$releaseName'. Aborting."
    }

    Write-Output "Looking for GitHub release $releaseName"

    $releases = Invoke-RestMethod -Uri $releasesUrl -Headers $headers -Method GET
    $release = $releases | Where-Object { $_.name -eq $releaseName }
    if ($release) {
        throw "Release $releaseName already exists. Aborting."
    }

    pip install -q twine

    $releaseBody = @()
    $releaseNotesLine = 1
    while (! $releaseNotes[$releaseNotesLine].StartsWith('## ')) {
        $releaseBody += $releaseNotes[$releaseNotesLine]
        $releaseNotesLine++
    }

    $createReleaseBody = @{
        tag_name   = $releaseName
        name       = $releaseName
        body       = ($releaseBody -join "`r`n").Trim()
        draft      = $false
        prerelease = $releaseName -match $preReleaseRegex
    } | ConvertTo-Json

    Write-Output "Creating GitHub release $releaseName"
    $release = Invoke-RestMethod -Uri $releasesUrl -Headers $headers -Method POST -Body $createReleaseBody -ContentType 'application/json'

    $headers["Content-type"] = "application/octet-stream"
    $uploadsUrl = "https://uploads.github.com/repos/$repo/releases/$($release.id)/assets?name="

    Write-Output "Uploading artifacts to GitHub release"

    $artifacts = Get-ChildItem -Path $artifactsPattern
    if (! $artifacts) {
        throw "Can't find any artifacts to publish"
    }

    $artifacts | ForEach-Object {
        Write-Output "Uploading $($_.Name)"
        $asset = Invoke-RestMethod -Uri ($uploadsUrl + $_.Name) -Headers $headers -Method POST -InFile $_
        Write-Output "Uploaded  $($asset.name)"
    }

    Write-Output "Uploading package to PyPi"
    & python -m twine upload $artifactsPattern

    Write-Output "Finished deploying $releaseName"
}
finally {
    Pop-Location
}