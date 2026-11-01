# Tech Lead Agent Memory System

## Structure
```
.techlead-memory/
├── README.md                    # This file
├── session-2026-11-01.md        # Session 1: Initial review + Kanban setup
├── session-YYYY-MM-DD.md        # Future sessions
└── latest-session.md            # Symlink to most recent (optional)
```

## Usage Protocol

### After Every Session
1. **Create session memory**: `session-YYYY-MM-DD.md`
2. **Update techlead-agent.md** with new patterns/decisions
3. **Move Kanban cards** in `cards/` (ready→in-progress→review→done)
4. **Update Technical Debt Registry** in `TECHLEAD_REVIEW.md`
5. **Record ADRs** in `docs/adr/` for architectural decisions

### Session Memory Template
```markdown
---
date: YYYY-MM-DD
session_type: review|planning|incident|retrospective|feature
participants: ["user", "techlead-agent", "backend-agent", ...]
---

# Session: Brief Title

## Summary
2-3 sentences on what was accomplished.

## Accomplishments
- Bullet points of done work

## Decisions Made
| Decision | Options Considered | Rationale |
|----------|-------------------|-----------|
| ...      | ...               | ...       |

## Technical Debt Updates
- TD-XXX: status change (Open → Ready → In Progress → Done)
- New debt items discovered

## Card Movements
- Card XX: column_from → column_to
- New cards created

## Metrics Updated
- Coverage: X% → Y%
- Debt count: X → Y
- Deploy frequency: ...

## Blockers / Risks
- Item blocking progress

## Next Session Focus
1. Priority 1
2. Priority 2
3. Priority 3

## Context for Next Session
Key files to read, people to sync with, decisions pending
```

## Quick Commands
```bash
# Latest session
cat .techlead-memory/$(ls -t .techlead-memory/*.md | head -1)

# All sessions
ls -la .techlead-memory/

# Current sprint cards
ls cards/ready/

# Debt registry
grep "TD-" TECHLEAD_REVIEW.md
```

## Integration with Agents
- **Tech Lead Agent** reads latest memory on startup
- **Other agents** can be delegated with context from memory
- **Kanban cards** reference session decisions