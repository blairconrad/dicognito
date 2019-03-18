[CmdletBinding()]
param (
    [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
    [string[]] $Commands,

    [Parameter(Mandatory = $false)]
    [string[]] $MatchingTests
)

$env:PYTHONPATH = "${env:PYTHONPATH};$PWD"

$env:PYTHONPATH = "${env:PYTHONPATH};$PWD"

if ($MatchingTests) {
    $pyTestMatching = "-k " + ($MatchingTests -join " or ")
}

$actions = @{
    'clean'        = { 'build', 'dicognito.egg-info', 'dist' | Where-Object { Test-Path $_ } | Remove-Item -Force -Recurse  }
    'testlocal'    = { $env:PYTHONPATH = "src;$env:PYTHONPATH"; python -m pytest $pyTestMatching tests }
    'testforever'  = { $env:PYTHONPATH = "src;$env:PYTHONPATH"; `python -m pytest --looponfail $pyTestMatching tests }
    'smoketest'    = { python smoketest\smoketest.py; code --diff smoketest\original.txt smoketest\anonymized.txt }
    'pack'         = { python setup.py sdist bdist_wheel }
    'publish'      = { python -m twine upload dist/* }
    'test-publish' = { python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/* }
    'help'         = { Write-Output "Usage: `r`n  build command [command...]`r`n`r`nwhere commands are:`r`n  $(($actions.Keys | Sort-Object) -join "`r`n  ")`r`n" }
}

$Commands | ForEach-Object {
    $command = $_
    $action = $actions[$command]
    if ($action) {
        Write-Output "$command starting..."
        & $action
        [int]$code = $LASTEXITCODE
        if ($code -ne 0) {
            throw "Command $command exited with code $code"
        }
        Write-Output "$command succeeded."
    }
    else {
        throw "Unknown command $command"
    }
}