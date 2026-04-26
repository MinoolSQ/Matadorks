---
name: matadorks-workflow
description: Upravljanje Matadorks razvojnim ciklusom. Koristi se za koordinaciju između Claude-a (PO) i agenata (implementeri), heartbeat monitoring, delegaciju zadataka na osnovu kvaliteta modela i eskalaciju blokera.
---

# Matadorks Workflow

Ovaj skill definiše kako agenti treba da funkcionišu unutar Matadorks ekosistema.

## Arhitektura Uloga

- **Claude (Product Owner)**: Glavni mozak projekta. On brainstorm-uje, kreira planove, deli ih na sub-taskove i dodeljuje ih agentima. Claude je jedini koji donosi finalne arhitektonske odluke.
- **Implementer Agenti**: Rade u izolovanim worktree-ovima. Svaki agent dobija specifičan task i relevantan "Role Skill" (npr. senior-backend).

## Operativni Protokol

### 1. Preuzimanje Zadataka
Pre početka rada, agent mora:
- Pročitati zadatak iz `ostava/tasks/<task-name>.md` ili `ostava/GEMINI.MD`.
- Proveriti `ostava/agent_quality.json` kako bi razumeo svoj Tier i očekivanja.
- Učitati relevantan Role Skill iz `skills/roles/`.

### 2. Monitoring (Heartbeat)
Uvek se oslanjaj na status koji daje heartbeat skripta:
- `bash ostava/check_quotas.sh`: Provera dostupnosti API-jeva.
- `bash ostava/heartbeat.sh`: Provera statusa svih aktivnih agenata i zombie procesa.

### 3. Komunikacija i Inbox
- **Globalni Log**: Svaki bitan progres loguj u `ostava/INBOX.MD`.
- **Eskalacija**: Ako naiđeš na **blocker**, **arhitektonsku dilemu** ili **kritičan bug**, u log upiši oznaku `[ESCALATION]`. To je signal Claudiu da mora da interveniše.
- **Forma loga**: `[YYYY-MM-DD] [AGENT:ime] -> CLAUDE: [ESCALATION] Opis problema.`

### 4. Delegacija
- Gemini agenti **MOGU** delegirati pod-zadatke drugim agentima (npr. Cerebras ili OpenRouter) koristeći `invoke_agent`.
- Agenti **NE SMEJU** direktno zvati Claude-a (Claude čeka u glavnom threadu i čita inbox).
- Delegacija mora biti proporcionalna tier-u agenta (`agent_quality.json`).

## Kontrola Kvaliteta
- **T1 Agenti**: Arhitektura i kompleksni refaktoring.
- **T2 Agenti**: Standardna implementacija modula.
- **T3 Agenti**: Bugfixes i config izmene.

## Brzi Komandi
- `watch -n 900 bash ostava/heartbeat.sh`: Pokretanje monitoringa u pozadini.
- `bash ostava/launch_all_agents.sh`: Masovno pokretanje planiranih agenata.
