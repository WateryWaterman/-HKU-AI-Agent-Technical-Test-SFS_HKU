[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('entity', 'type', 'pset', 'qto', 'prop', 'express', 'psd', 'old', 'all')]
    [string]$Kind,

    [Parameter(Mandatory = $true, Position = 1)]
    [string]$Term,

    [int]$After = 0,
    [int]$Max = 40
)

$ErrorActionPreference = 'SilentlyContinue'

$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
$Research = Join-Path $Root 'research'
if (-not (Test-Path $Research)) { $Research = 'D:\ProgramData\ArchiTestMajun\research' }

$Docs = Join-Path $Research 'IFC4.3.x-development\docs'
$Exp = Join-Path $Research 'IFC4_3\HTML\IFC4X3_ADD2.exp'
$Psd = Join-Path $Research 'IFC4_3\HTML\psd'
$Lexical = Join-Path $Research 'IFC4_3\HTML\lexical'
$OldRef = Join-Path $Research 'IFC4.3.x-development\reference_schemas'

function Out-Section([string]$Label, $Items) {
    if ($Items -and @($Items).Count -gt 0) {
        foreach ($i in @($Items)) { Write-Output "$Label $i" }
    }
    else {
        Write-Output "$Label NOT FOUND"
    }
}

function Find-DocsMd([string]$Name, [string[]]$FolderNames) {
    Get-ChildItem -Path (Join-Path $Docs 'schemas') -Recurse -Filter "$Name.md" -File |
    Where-Object { $FolderNames -contains $_.Directory.Name } |
    ForEach-Object { $_.FullName }
}

function Find-ExpLines([string]$Pattern, [int]$CtxAfter) {
    $hits = Select-String -Path $Exp -Pattern $Pattern -CaseSensitive:$false
    $out = @()
    foreach ($h in ($hits | Select-Object -First $Max)) {
        $out += ('{0}: {1}' -f $h.LineNumber, $h.Line.TrimEnd())
        if ($CtxAfter -gt 0) {
            $ctx = Get-Content $Exp | Select-Object -Skip $h.LineNumber -First $CtxAfter
            foreach ($c in $ctx) { $out += ('{0}' -f $c.TrimEnd()) }
        }
    }
    return $out
}

switch ($Kind) {

    'entity' {
        Out-Section '[docs-md]' (Find-DocsMd $Term @('Entities'))
        $lex = Join-Path $Lexical "$Term.htm"
        if (Test-Path $lex) { Out-Section '[lexical-htm]' $lex } else { Out-Section '[lexical-htm]' $null }
        Out-Section '[exp]' (Find-ExpLines "^ENTITY $Term\b" $After)
    }

    'type' {
        Out-Section '[docs-md]' (Find-DocsMd $Term @('Types', 'PropertyEnumerations'))
        $lex = Join-Path $Lexical "$Term.htm"
        if (Test-Path $lex) { Out-Section '[lexical-htm]' $lex } else { Out-Section '[lexical-htm]' $null }
        Out-Section '[exp]' (Find-ExpLines "^TYPE $Term\b" $After)
    }

    'pset' {
        Out-Section '[docs-md]' (Find-DocsMd $Term @('PropertySets'))
        $xml = Join-Path $Psd "$Term.xml"
        if (Test-Path $xml) { Out-Section '[psd-xml]' $xml } else { Out-Section '[psd-xml]' $null }
    }

    'qto' {
        Out-Section '[docs-md]' (Find-DocsMd $Term @('QuantitySets'))
        $xml = Join-Path $Psd "$Term.xml"
        if (Test-Path $xml) { Out-Section '[psd-xml]' $xml } else { Out-Section '[psd-xml]' $null }
    }

    'prop' {
        $letter = $Term.Substring(0, 1).ToLower()
        $md = Join-Path $Docs "properties\$letter\$Term.md"
        if (Test-Path $md) { Out-Section '[docs-md]' $md } else { Out-Section '[docs-md]' $null }
        $inPsets = Select-String -Path (Join-Path $Psd '*.xml') -Pattern "<Name>$Term</Name>" -List |
        ForEach-Object { $_.Filename } | Sort-Object -Unique | Select-Object -First $Max
        Out-Section '[used-in-psd]' $inPsets
    }

    'express' {
        Out-Section '[exp]' (Find-ExpLines $Term $After)
    }

    'psd' {
        $hits = Select-String -Path (Join-Path $Psd '*.xml') -Pattern $Term |
        Select-Object -First $Max |
        ForEach-Object { '{0}:{1}: {2}' -f $_.Filename, $_.LineNumber, $_.Line.Trim() }
        Out-Section '[psd-hit]' $hits
    }

    'old' {
        $files = Get-ChildItem -Path $OldRef -Recurse -File |
        Where-Object { $_.Extension -in '.exp', '.xml', '.json' }
        $hits = $files | Select-String -Pattern $Term |
        Select-Object -First $Max |
        ForEach-Object { '{0}:{1}: {2}' -f $_.Path.Replace("$OldRef\", ''), $_.LineNumber, $_.Line.Trim() }
        Out-Section '[old-ref]' $hits
    }

    'all' {
        $mdHits = Get-ChildItem -Path $Docs -Recurse -Filter "*$Term*.md" -File |
        Select-Object -First $Max | ForEach-Object { $_.FullName }
        Out-Section '[docs-md]' $mdHits
        $psdFiles = Get-ChildItem -Path $Psd -Filter "*$Term*.xml" -File |
        Select-Object -First $Max | ForEach-Object { $_.FullName }
        Out-Section '[psd-xml]' $psdFiles
        Out-Section '[exp]' (Find-ExpLines "\b\w*$Term\w*\b" 0 | Select-Object -First 20)
    }
}
