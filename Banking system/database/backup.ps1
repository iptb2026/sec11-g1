# Back up the team database to database\backups\<db>_<yyyyMMdd_HHmm>.sql
#
# Take one before any risky step: bulk test data, a schema change, a demo.
#
#   MySQL installed on this PC:
#     .\backup.ps1
#   MySQL running in Docker:
#     .\backup.ps1 -Container <container-name>     (find it with: docker ps)
#
# Defaults match appserver\app\core\config.py. Override any of them, e.g.
#     .\backup.ps1 -Port 3501 -Database catarig
#
# Restore a backup with:
#     mysql -h 127.0.0.1 -P 3306 -u admin -p catarig < backups\<file>.sql

param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 3306,
    [string]$User = "admin",
    [string]$Database = "catarig",
    [string]$Container = ""
)

$ErrorActionPreference = "Stop"

$backupDir = Join-Path $PSScriptRoot "backups"
New-Item -ItemType Directory -Force $backupDir | Out-Null
$fileName = "{0}_{1}.sql" -f $Database, (Get-Date -Format "yyyyMMdd_HHmm")
$outFile = Join-Path $backupDir $fileName

$secure = Read-Host "MySQL password for $User" -AsSecureString
$password = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure))

# --single-transaction: consistent snapshot without locking the tables
# --no-tablespaces: avoids the PROCESS-privilege error for non-root users
$dumpArgs = @("--single-transaction", "--routines", "--triggers", "--no-tablespaces",
              "-u", $User, $Database)

if ($Container) {
    # Dump inside the container, then copy the file out. The file is
    # written by mysqldump itself, so PowerShell never re-encodes it.
    docker exec -e "MYSQL_PWD=$password" $Container mysqldump @dumpArgs "--result-file=/tmp/$fileName"
    if ($LASTEXITCODE -ne 0) { throw "mysqldump failed inside container $Container" }
    docker cp "${Container}:/tmp/$fileName" $outFile
    docker exec $Container rm "/tmp/$fileName"
} else {
    if (-not (Get-Command mysqldump -ErrorAction SilentlyContinue)) {
        throw "mysqldump is not on PATH. Install the MySQL client tools, or use -Container if MySQL runs in Docker."
    }
    $env:MYSQL_PWD = $password
    try {
        mysqldump -h $HostName -P $Port @dumpArgs "--result-file=$outFile"
        if ($LASTEXITCODE -ne 0) { throw "mysqldump failed" }
    } finally {
        Remove-Item Env:MYSQL_PWD -ErrorAction SilentlyContinue
    }
}

$size = [math]::Round((Get-Item $outFile).Length / 1KB, 1)
Write-Host "Backup saved: $outFile ($size KB)"
