# SEDARScraper
O projeto é um **scraper automatizado de relatórios técnicos** do portal canadense [SEDAR+](https://www.sedarplus.ca), com as seguintes características:

**Objetivo:** Coletar diariamente relatórios técnicos NI 43-101 (documentos de mineração/recursos naturais exigidos por regulação canadense) publicados no dia anterior e armazená-los no SharePoint da empresa.

**Fluxo de execução:**

1. **Navegação** — Usa Playwright (browser headless) para abrir o SEDAR+, acessar a área de busca de documentos e filtrar por tipo `Technical Report NI 43-101` com intervalo de datas (ontem → hoje).

2. **Resolução de Captcha** — Se o site redirecionar para o validador hCaptcha (`validate.perfdrive.com`), o sistema resolve automaticamente via desafio de acessibilidade (perguntas em texto), usando um LLM Azure para responder cada pergunta.

3. **Download** — Para cada página de resultados, baixa os PDFs em lote (ZIP) via botão "Download All". Se o lote for grande demais, baixa um por um. O ZIP é nomeado com as datas dos documentos e número da página.

4. **Descompactação** — Extrai os PDFs do ZIP, renomeando cada arquivo com um UUID para evitar colisões de nome.

5. **Envio ao SharePoint** — Usa a Microsoft Graph API (autenticação via `client_credentials`) para fazer upload chunked (~13 MB por chunk) dos PDFs para uma biblioteca específica do SharePoint (`gamabotvalebase › Documentos › Persona de Benchmark`).

6. **Limpeza** — Remove a pasta `output` local ao final de cada página processada e ao encerrar.

**Tecnologias:** Python, Playwright (async), httpx (async), Microsoft Graph API, Azure OpenAI (para o captcha).

**Conceito central:** pipeline de scraping regulatório totalmente autônomo — sem intervenção humana, com tratamento de captcha por IA e entrega direta ao repositório corporativo no SharePoint.
