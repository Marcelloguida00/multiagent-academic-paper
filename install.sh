#!/usr/bin/env bash
set -e

SKILLS_DIR="$HOME/.claude/skills"
COMMANDS_DIR="$HOME/.claude/commands"

mkdir -p "$SKILLS_DIR" "$COMMANDS_DIR"

TARGET="$SKILLS_DIR/agenzia-multiagente"

if [ -d "$TARGET" ]; then
    echo "Aggiorno il repository esistente..."
    git -C "$TARGET" pull
else
    echo "Clono agenzia-multiagente..."
    git clone https://github.com/Marcelloguida00/multiagent-academic-paper.git "$TARGET"
fi

# 1. Installa sembra-ai come skill autonoma di primo livello
mkdir -p "$SKILLS_DIR/sembra-ai"
cp "$TARGET/skills/sembra-ai/SKILL.md" "$SKILLS_DIR/sembra-ai/SKILL.md"
echo "✓ Skill sembra-ai installata in $SKILLS_DIR/sembra-ai"

# 2. Installa i comandi slash globali
cp "$TARGET/.claude/commands/"*.md "$COMMANDS_DIR/"
echo "✓ Comandi slash /agenzia-multiagente e /sembra-ai installati in $COMMANDS_DIR"

echo ""
echo "Installazione completata con successo! Riavvia Claude Code o apri una nuova sessione."
