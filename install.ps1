# Script di installazione automatica completa per Claude Code (Windows PowerShell)
$ErrorActionPreference = "Stop"

$skillsDir = "$HOME\.claude\skills"
$commandsDir = "$HOME\.claude\commands"

New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
New-Item -ItemType Directory -Force -Path $commandsDir | Out-Null

$mainTarget = "$skillsDir\agenzia-multiagente"

if (Test-Path $mainTarget) {
    Write-Host "Aggiorno il repository agenzia-multiagente..."
    git -C $mainTarget pull
} else {
    Write-Host "Clono agenzia-multiagente..."
    git clone https://github.com/Marcelloguida00/multiagent-academic-paper.git $mainTarget
}

# Elenco completo delle skill modulari
$skillList = @(
    "sembra-ai", 
    "ricerca-accademica", 
    "scrittura-paper", 
    "bonifica-tassonomia", 
    "design-scientifico",
    "legal-audit",
    "security-audit",
    "crittografia",
    "ig-audit"
)

foreach ($skill in $skillList) {
    $targetFolder = "$skillsDir\$skill"
    New-Item -ItemType Directory -Force -Path $targetFolder | Out-Null
    Copy-Item "$mainTarget\skills\$skill\*" "$targetFolder\" -Recurse -Force
    Write-Host "✓ Skill $skill installata in: $targetFolder"
}

# Installa tutti i comandi slash globali in ~/.claude/commands
Copy-Item "$mainTarget\.claude\commands\*.md" "$commandsDir\" -Force
Write-Host "✓ Comandi slash installati in: $commandsDir"

Write-Host "`nInstallazione completata! Tutte le skill (inclusi audit e crittografia) sono ora operative."
Write-Host "Riavvia Claude Code (o apri una nuova sessione con 'claude') per iniziare."
