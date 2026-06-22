# ============================================================
# Rime dictionary format converter
# Converts ; multi-aux format to [ moqi aux format
# Pinyin with >2 letters is converted to xiaohe shuangpin
# Pinyin with 1-2 letters is kept as-is
#
# Usage:
#   1. Modify $inFile path below to point to your dictionary
#   2. Run: powershell -NoProfile -ExecutionPolicy Bypass -File convert_dict.ps1
#
# The script creates a .yaml.bak backup before modifying
# ============================================================

$inFile = 'd:\Rime\cn_dicts_moqi\base1.dict.yaml'

$rules = @(
    @('iong','s'), @('iang','l'), @('uang','l'), @('uai','k'),
    @('uan','r'), @('iao','n'), @('ing','k'), @('eng','g'),
    @('ang','h'), @('ong','s'), @('ian','m'), @('ua','x'),
    @('ia','x'), @('iu','q'), @('ei','w'), @('ai','d'),
    @('ao','c'), @('ou','z'), @('an','j'), @('en','f'),
    @('in','b'), @('un','y'), @('ui','v'), @('uo','o'),
    @('ie','p'), @('ve','t'), @('ue','t'), @('er','r')
)

function cv($py) {
    $s = ''; $y = ''
    if ($py.StartsWith('zh')) { $s = 'v'; $y = $py.Substring(2) }
    elseif ($py.StartsWith('ch')) { $s = 'i'; $y = $py.Substring(2) }
    elseif ($py.StartsWith('sh')) { $s = 'u'; $y = $py.Substring(2) }
    elseif ($py -match '^[bpmfdtnlgkhjqxrzcsyw]') { $s = $py[0]; $y = $py.Substring(1) }
    else { $s = $py[0]; $y = $py }
    $k = ''
    foreach ($r in $rules) { if ($y.StartsWith($r[0])) { $k = $r[1]; break } }
    if ($k -eq '') { $k = $y }
    return $s + $k
}

function cs($seg) {
    $seg = $seg.TrimEnd(';')
    $f = $seg -split ';'
    if ($f.Count -ge 2) {
        $py = $f[0].Trim()
        $ax = $f[1].Trim()
        if ($ax -match ',') { $ax = ($ax -split ',')[0] }
        if ($py.Length -gt 2) { return (cv $py) + '[' + $ax }
        else { return $py + '[' + $ax }
    }
    return $seg
}

$bak = $inFile -replace '\.yaml$', '.yaml.bak'
Copy-Item $inFile $bak -Force
Write-Host ('Backup: ' + $bak)

$d = [System.IO.File]::ReadAllLines($inFile, [System.Text.UTF8Encoding]::new($false))
$n = New-Object System.Collections.ArrayList
$st = $false; $c = 0

foreach ($l in $d) {
    if (-not $st) {
        if ($l -eq '...') { $st = $true }
        [void]$n.Add($l)
        continue
    }
    if ($l.StartsWith('#') -or $l.Trim() -eq '') {
        [void]$n.Add($l)
        continue
    }
    $p = $l.Split("`t")
    if ($p.Count -ge 2) {
        $w = $p[0]
        $cd = $p[1]
        $rt = ''
        if ($p.Count -gt 2) { $rt = "`t" + ($p[2..($p.Count-1)] -join "`t") }
        $sgs = $cd -split ' '
        $ns = @()
        foreach ($sg in $sgs) {
            if ($sg -match ';') { $ns += cs $sg }
            else { $ns += $sg }
        }
        $nc = $ns -join ' '
        $c++
        [void]$n.Add($w + "`t" + $nc + $rt)
    }
    else { [void]$n.Add($l) }
}

[System.IO.File]::WriteAllLines($inFile, $n, [System.Text.UTF8Encoding]::new($false))
Write-Host ('Converted: ' + $c + ' entries')