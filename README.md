# ga4-mcp

Uppsättning av Googles officiella GA4-koppling, [googleanalytics/google-analytics-mcp](https://github.com/googleanalytics/google-analytics-mcp), så att Claude (Claude Code, Claude Desktop) får **läsåtkomst** till Google Analytics 4. Kopplingen körs lokalt på din egen dator och kan inte ändra något i GA4.

Exempel på frågor när den är kopplad:

- "Vilka GA4-egendomar har jag tillgång till?"
- "Sessioner och köp per kanal de senaste 28 dagarna, jämfört med samma period i fjol."
- "Vilka landningssidor har högst avvisningsfrekvens från organisk sökning?"

## Vad repot innehåller

Ingen egen kopia av Googles kod. Repot har tre saker:

- `requirements.txt`: Googles koppling (`analytics-mcp` 1.1.0) och alla dess beroenden låsta till exakta versioner, så att ingen uppdatering kommer in utan att någon har granskat den.
- `login.py`: en inloggning i webbläsaren med teamets egen inloggningsklient. Ingen Google Cloud CLI och ingen roll i Google Cloud-projektet behövs för den som använder kopplingen.
- Den här instruktionen.

## Säkerhet i korthet

- Inloggningen ber Google om behörigheten `analytics.readonly` och inget annat. Google nekar alltså alla försök att ändra något, även om koden skulle försöka.
- Googles koppling har tre skrivande verktyg (skapa anpassad dimension, nyckelhändelse och anteckning), men de är avstängda om man inte startar den med `--allow-write`. Det gör vi aldrig, och behörigheten skulle ändå saknas.
- Kopplingen ser exakt de GA4-egendomar som ditt eget konto ser. Det finns ingen lista över tillåtna egendomar.
- Den pratar bara med Googles API (`googleapis.com`). Inloggningen tar emot Googles svar på din egen dator (`127.0.0.1`) och nås inte utifrån.
- Inloggningen sparas i `~/.ga4-mcp/credentials.json` på din dator. Den ger läsåtkomst till dina GA4-egendomar, så behandla filen som ett lösenord.
- GA4-data om kunder hamnar i Claude-konversationen. Följ det som gäller för kunddata i AI-verktyg.

## Uppsättning för dig som ska använda kopplingen

Du behöver Python 3.10 eller senare, git, åtkomst till minst en GA4-egendom och **klientfilen** (`client.json`) som du fått av den som administrerar kopplingen. Det är samma fil som för Search Console-kopplingen [gsc-mcp](https://github.com/jonathan-holmqvist/gsc-mcp). Har du redan den kopplingen behövs ingen ny fil.

Enklast: be Claude göra det. Bifoga `client.json` och klistra in:

> Klona https://github.com/jonathan-holmqvist/ga4-mcp och sätt upp kopplingen enligt README, avsnittet "Uppsättning för dig som ska använda kopplingen". Klientfilen client.json är bifogad.

Claude gör stegen nedan. Du behöver bara välja ditt jobbkonto i webbläsaren och godkänna (steg 4).

### 1. Hämta

```bash
git clone https://github.com/jonathan-holmqvist/ga4-mcp.git
```

Saknas Python: installera Python 3.12 eller senare från [python.org](https://www.python.org/downloads/) (Windows: eller `winget install Python.Python.3.12`).

### 2. Installera

Mac:

```bash
cd ga4-mcp && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Windows:

```bash
cd ga4-mcp && py -m venv .venv && .venv\Scripts\pip install -r requirements.txt
```

### 3. Lägg klientfilen på plats

Kopiera `client.json` till mappen `.ga4-mcp` i din hemkatalog:

- Mac: `~/.ga4-mcp/client.json`
- Windows: `C:\Users\<ditt namn>\.ga4-mcp\client.json`

Finns filen redan i `.gsc-mcp` (Search Console-kopplingen) hittar inloggningen den där, och steget kan hoppas över. Lägg den aldrig i repot.

### 4. Logga in (en gång)

Mac: `.venv/bin/python login.py`. Windows: `.venv\Scripts\python login.py`.

Webbläsaren öppnas. Välj ditt jobbkonto och godkänn läsåtkomsten. Skriptet skriver ut sökvägen till inloggningsfilen, som behövs i nästa steg.

### 5. Koppla in i Claude Code

Byt sökvägarna mot dina egna. Använd snedstreck framåt (`/`) även på Windows.

Mac:

```bash
claude mcp add ga4 --scope user --env "GOOGLE_APPLICATION_CREDENTIALS=/Users/<ditt namn>/.ga4-mcp/credentials.json" -- "/full/sökväg/till/ga4-mcp/.venv/bin/analytics-mcp"
```

Windows:

```bash
claude mcp add ga4 --scope user --env "GOOGLE_APPLICATION_CREDENTIALS=C:/Users/<ditt namn>/.ga4-mcp/credentials.json" -- "C:/full/sökväg/till/ga4-mcp/.venv/Scripts/analytics-mcp.exe"
```

<details>
<summary>Claude Desktop</summary>

Lägg till i `claude_desktop_config.json`, inuti det befintliga `mcpServers`:

```json
{
  "mcpServers": {
    "ga4": {
      "command": "/full/sökväg/till/ga4-mcp/.venv/bin/analytics-mcp",
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/Users/<ditt namn>/.ga4-mcp/credentials.json"
      }
    }
  }
}
```

</details>

### 6. Kontrollera

Starta om Claude och fråga:

> Använd ga4 och lista mina GA4-konton och egendomar.

## Uppsättning för den som administrerar (en gång)

Inloggningsklienten är densamma som för [gsc-mcp](https://github.com/jonathan-holmqvist/gsc-mcp) (Desktop-klient i ett Google Cloud-projekt med inloggningsskärm **Internal**). Utöver det som står där:

1. Slå på [Google Analytics Data API](https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com) och [Google Analytics Admin API](https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com) i samma projekt. De är gratis.
2. Lägg till behörigheten `https://www.googleapis.com/auth/analytics.readonly` under Data access på inloggningsskärmen.

## Uppdatera Googles koppling

Se vad som ändrats i [Googles repo](https://github.com/googleanalytics/google-analytics-mcp/releases), särskilt nya skrivande verktyg. Uppdatera sedan i en ny, tom `.venv` och lås om:

```bash
pip install analytics-mcp==NY_VERSION google-auth-oauthlib && pip freeze > requirements.txt
```

Lägg tillbaka `; sys_platform == "win32"` efter raden `pywin32` och kör `pip-audit -r requirements.txt` innan ändringen sparas.

## Felsökning

- **"Hittar ingen klientfil":** lägg `client.json` i `~/.ga4-mcp` (steg 3).
- **"access_denied" vid inloggning:** kontot hör inte till samma organisation som inloggningsklienten. Logga in med jobbkontot.
- **"invalid_grant" efter en tid:** inloggningen har gått ut eller dragits tillbaka. Kör inloggningen i steg 4 igen och starta om Claude.
- **"API has not been used in project" eller "SERVICE_DISABLED":** ett av de två API:erna är inte påslaget. Be den som administrerar göra steg 1 ovan.
- **Inga egendomar visas:** kontrollera i GA4 att jobbkontot har minst läsbehörighet på egendomen.
- **Kopplingen startar inte på Windows:** kontrollera att sökvägarna i steg 5 har snedstreck framåt.
