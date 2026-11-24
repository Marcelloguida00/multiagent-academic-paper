#!/usr/bin/env bash
set -e

SKILLS_DIR="$HOME/.claude/skills"
COMMANDS_DIR="$HOME/.claude/commands"

mkdir -p "$SKILLS_DIR" "$COMMANDS_DIR"

MAIN_TARGET="$SKILLS_DIR/agenzia-multiagente"

if [ -d "$MAIN_TARGET" ]; then
    echo "Aggiorno il repository agenzia-multiagente..."
    git -C "$MAIN_TARGET" pull
else
    echo "Clono agenzia-multiagente..."
    git clone https://github.com/Marcelloguida00/multiagent-academic-paper.git "$MAIN_TARGET"
fi

# Elenco completo delle 5 skill specializzate oltre all'orchestratore
SKILL_LIST=("sembra-ai" "ricerca-accademica" "scrittura-paper" "bonifica-tassonomia" "design-scientifico")

for skill in "${SKILL_LIST[@]}"; do
    mkdir -p "$SKILLS_DIR/$skill"
    cp "$MAIN_TARGET/skills/$skill/SKILL.md" "$SKILLS_DIR/$skill/SKILL.md"
    echo "✓ Skill $skill installata in $SKILLS_DIR/$skill"
done

# Installa tutti i comandi slash globali
cp "$MAIN_TARGET/.claude/commands/"*.md "$COMMANDS_DIR/"
echo "✓ Comandi slash installati in $COMMANDS_DIR"

echo ""
echo "Installazione completata! Tutte le 6 skill (incluso design-scientifico) sono ora operative."
echo "Riavvia Claude Code o apri una nuova sessione con 'claude'."
