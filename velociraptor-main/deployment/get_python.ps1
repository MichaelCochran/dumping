$username = $Env:EFOSS_USER
$password = $Env:EFOSS_TOKEN
Invoke-WebRequest -Uri "https://crl.external.lmco.com/trust/pem/combined/Combined_pem.pem" -OutFile "Combined_pem.pem"
Import-Certificate -FilePath "Combined_pem.pem" -CertStoreLocation Cert:\LocalMachine\root

$url = "https://nexus.global.lmco.com/repository/efoss-raw/python/3.11.2/python3.11.2amd64.exe"
$pair = "$($username):$($password)"

$encodedCreds = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes($pair))

$basicAuthValue = "Basic $encodedCreds"

$headers = @{
    Authorization = $basicAuthValue
}

Invoke-WebRequest -Uri $url -OutFile "python-installer.exe" -Headers $headers
Start-Process python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait
Remove-Item python-installer.exe