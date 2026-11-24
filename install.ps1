# Script di installazione automatica per Claude Code (Windows PowerShell)
$ErrorActionPreference = "Stop"

$skillsDir = "$HOME\.claude\skills"
$commandsDir = "$HOME\.claude\commands"

# Assicura le cartelle
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
New-Item -ItemType Directory -Force -Path $commandsDir | Out-Null

$target = "$skillsDir\agenzia-multiagente"

if (Test-Path $target) {
    Write-Host "Aggiorno il repository esistente..."
    git -C $target pull
} else {
    Write-Host "Clono agenzia-multiagente..."
    git clone https://github.com/Marcelloguida00/multiagent-academic-paper.git $target
}

# 1. Installa sembra-ai come skill autonoma di primo livello
$sembraAiTarget = "$skillsDir\sembra-ai"
New-Item -ItemType Directory -Force -Path $sembraAiTarget | Out-Null
Copy-Item "$target\skills\sembra-ai\SKILL.md" "$sembraAiTarget\SKILL.md" -Force
Write-Host "✓ Skill sembra-ai installata in: $sembraAiTarget"

# 2. Installa i comandi slash globali in ~/.claude/commands
Copy-Item "$target\.claude\commands\*.md" "$commandsDir\" -Force
Write-Host "✓ Comandi slash /agenzia-multiagente e /sembra-ai installati in: $commandsDir"

Write-Host "`nInstallazione completata con successo! Riavvia Claude Code o apri una nuova sessione."
