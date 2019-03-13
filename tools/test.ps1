# Change to a non-source folder to make sure we run the tests on the
# installed library.
$testsDir = Get-Item tests

Push-Location C:\

Write-Output "tests found in: $testsDir"

# --pyargs argument is used to make sure we run the tests on the
# installed package rather than on the local folder
py.test --pyargs dicognito $testsDir -k 'not performance'

Pop-Location

exit $LastExitCode
