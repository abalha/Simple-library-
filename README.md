# Maktaba — Hatua ya 1 hadi 5

Project ya kujifunza CRUD kwa Python, Flask, SQLite na HTML/CSS.
Hili ni toleo la assignment ya Library Management Information System. Limekamilisha
vitabu, wanachama, vitabu vilivyoazimwa, overdue/faini, login ya mhudumu mmoja na
ripoti zinazochapishika.

## Kuendesha kwenye Windows (PowerShell katika VS Code)

Sakinisha Python 3.11 au mpya zaidi ikiwa haipo. Extract ZIP kwanza, kisha fungua folder hii katika VS Code.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Fungua http://127.0.0.1:5000 kwenye browser. Kusimamisha: Ctrl+C.
Hatuhitaji ku-activate venv; commands hizi zinaepuka tatizo la PowerShell execution policy.
Ikiwa `py` haipatikani lakini `python --version` inafanya kazi, tumia `python -m venv .venv` kwenye command ya kwanza.
Database `library.db` inajitengeneza mara ya kwanza. Data zinabaki ukizima na kuwasha app.
Usifute database ukiwa unahitaji taarifa zake. SQLite haihitaji server tofauti.

## Sample data ya presentation

Kwa database tupu, unaweza kuweka vitabu, wanachama na vitabu vilivyoazimwa vya mfano
(ikiwemo kitabu kilichochelewa) kwa command hii kabla ya kuwasha app:

```powershell
.\.venv\Scripts\python.exe seed_data.py
```

Script hukataa kufanya kazi kama tayari kuna data, ili isiharibu taarifa zako. Ili kuanza upya
kwa sample data, hifadhi backup ya `library.db` kwanza, kisha futa database hiyo na uendeshe
script; usifanye hivyo ukiwa unahitaji data zako halisi.

## Kuingia

Mfumo una login ya mhudumu mmoja. Taarifa za majaribio ni username `admin` na password
`maktaba2026`. Kwa matumizi halisi, badilisha taarifa hizi kabla ya kuendesha app kwa kuweka
environment variables `LIBRARIAN_USERNAME` na `LIBRARIAN_PASSWORD`; usitumie taarifa za
majaribio kwenye kompyuta inayoshirikiwa.
Login hii ni ulinzi wa mwanzo tu: bado hakuna akaunti nyingi wala majukumu tofauti ya watumiaji.

## Yaliyopo — Vitabu

- Kuongeza, kuona, kubadilisha na kufuta kitabu baada ya uthibitisho.
- Kutafuta jina au mwandishi (SQLite lower() ina mipaka kwa herufi zisizo ASCII).
- Uhakiki wa lazima, mwaka na idadi isiyo hasi, kwenye server na fomu.
- Jumla ya rekodi na nakala; hizi si ripoti kamili za assignment.

## Yaliyopo — Wanachama

- Kusajili mwanachama: namba ya mwanachama (hadi herufi 50), jina kamili (hadi herufi 150),
  aina (mwanafunzi/mwalimu). Hali huwekwa "active" moja kwa moja wakati wa usajili.
- Kuonyesha orodha ya wanachama na kutafuta kwa namba au jina.
- Kubadilisha taarifa za mwanachama, ikiwemo kuweka active/inactive.
- Hakuna kufuta mwanachama; "inactive" hutumika kusimamisha uanachama bila kupoteza historia.
- Namba ya mwanachama huhifadhiwa kwa herufi kubwa (uppercase) na ni ya kipekee
  bila kujali herufi kubwa/ndogo (ST001 na st001 ni mwanachama mmoja).
- Mwanachama `active` pekee ndiye anayeruhusiwa kukopa kitabu kipya; aliye `inactive`
  anaweza kurejesha kitabu alichonacho, lakini hawezi kukopa kingine. Mhudumu ndiye
  anayehakiki kitambulisho cha chuo kabla ya kusajili; hakuna integration na mfumo wa chuo.

## Yaliyopo — Mikopo (uazimaji na urejeshaji)

- Kukopesha kitabu: mhudumu anaandika namba ya mwanachama na kuchagua kitabu. Tarehe ya
  mwisho (due date) huwekwa kiotomatiki siku 30 kutoka tarehe ya kukopa.
- Masharti ya kukopa: mwanachama awe "active" (inactive hawezi kukopa kipya, lakini bado
  anaweza kurejesha mkopo wake uliopo); kitabu kiwe na nakala zinazopatikana (copies za jumla
  minus zinazokopeshwa kwa sasa); mwanachama mmoja hawezi kuwa na mikopo zaidi ya 5
  ambayo bado hajairejesha kwa wakati mmoja.
- Kurejesha kitabu baada ya uthibitisho; mkopo uliorejeshwa tayari haurejeshwi mara ya pili.
- Ukurasa wa vitabu sasa unaonyesha "Zinazopatikana" (nakala za jumla minus zinazokopeshwa).
- Kitabu chenye historia ya mikopo hakiwezi kufutwa; nakala za kitabu hazipunguzwi chini ya
  idadi inayokopeshwa kwa sasa.
- Muda wa siku 30 na kikomo cha mikopo 5 ni maamuzi ya mwanzo ya mfumo; yanaweza kubadilishwa
  (LOAN_DAYS na MAX_ACTIVE_LOANS juu ya app.py) endapo sheria rasmi ya maktaba itakuwa tofauti.

## Yaliyopo — Overdue na faini

- Faini ni TZS 1000 (FINE_PER_DAY juu ya app.py) kwa kila siku ya kuchelewa baada ya due_date.
- Mikopo bado iliyo kwenye mikono (hazijarejeshwa) inaonyesha faini "inayokadiriwa" kwa kulinganisha
  due_date na tarehe ya leo; faini halisi huhesabiwa siku ya kurejesha kwa kutumia tarehe halisi
  ya kurejesha.
- Mwanachama mwenye angalau mkopo mmoja uliochelewa (returned_at ni tupu na due_date imepita)
  hawezi kukopa kitabu kingine chochote mpaka arejeshe ulio nyuma — hii inazuiwa upande wa server,
  bila kujali kama bado hajafikia kikomo cha mikopo 5.
- Ukurasa wa kurejesha unaonyesha siku zilizochelewa na faini kabla ya mhudumu kuthibitisha;
  baada ya kurejesha, ujumbe unaarifu siku zilizochelewa na faini ya mwisho.
- Faini kwa sasa ni hesabu tu inayoonyeshwa kwenye ukurasa; mfumo hauhifadhi kumbukumbu ya
  malipo (hakuna "imelipwa/haijalipwa"). Hiyo si sehemu ya hitaji lililothibitishwa bado.

## Yaliyopo — Login na ripoti

- Kurasa zote za mfumo zinalindwa kwa login ya mhudumu; mhudumu anaweza kutoka kwa kutumia
  kiungo cha "Toka".
- Kuna ripoti ya vitabu kwenye `/reports/books`, yenye rekodi za vitabu, nakala zote na
  nakala zinazopatikana, ripoti ya vitabu vilivyoazimwa kwenye `/reports/loans` yenye hali na
  faini, na ripoti ya wanachama kwenye `/reports/members`. Kila ripoti ina kitufe cha
  "Chapisha" kinachotumia print dialog ya browser.
- Mfumo una mhudumu mmoja mwenye username na password moja tu kwa sasa; hakuna usajili wa watumiaji,
  reset ya password, wala roles tofauti.

## Usalama na uhakiki (vitabu, wanachama, mikopo, faini na login)

- POST forms zina CSRF token; SQL hutumia parameters; templates zina escape ya maandishi.
- Database ina UNIQUE na CHECK constraints (mfano member_number ya kipekee,
  member_type/status zinazokubalika pekee) pamoja na uhakiki upande wa server.
- Namba ya mwanachama inayojirudia inaonyesha ujumbe wa kueleweka badala ya server error.
- Masharti ya mikopo (hali ya mwanachama, mkopo uliochelewa, nakala zinazopatikana, kikomo
  cha mikopo 5) yanahakikiwa upande wa server kabla ya kuhifadhi mkopo mpya.
- Kurasa za mfumo zinahitaji session ya login. Username na password vinaweza kuwekwa kwa
  `LIBRARIAN_USERNAME` na `LIBRARIAN_PASSWORD` badala ya taarifa za majaribio zilizopo kwenye code.

## Jinsi code inavyoungana

1. Mhudumu huingia kwanza kwenye `/login`; session yake ndiyo huruhusu kufungua kurasa za mfumo.
2. Browser inatuma GET `/`, `/members` au `/loans` kupata orodha.
3. Route kwenye `app.py` inasoma SQLite (ikiwemo JOIN kati ya loans, books na members) na kutuma data kwenye template.
4. Mtumiaji anafungua `/books/new`, `/members/new` au `/loans/new` na kujaza fomu.
5. POST inakaguliwa; ikiwa sahihi INSERT/UPDATE inahifadhi taarifa.
6. Namba ya mwanachama inayojirudia inakamatwa na database (UNIQUE) na kuonyeshwa kama ujumbe rafiki.
7. Kukopesha kunaandika borrowed_at na due_date (leo + siku 30); kurejesha kunaweka returned_at.
8. Kabla ya kukopesha, server inahakiki due_date za mikopo isiyorejeshwa ya mwanachama dhidi ya
   tarehe ya leo (string za ISO format zinalinganishwa moja kwa moja) kuamua kama ana mkopo uliochelewa.
9. `/reports/books` husoma jumla na upatikanaji wa vitabu, kisha huonyesha ripoti inayoweza kuchapishwa.
10. Redirect inarudisha orodha. UPDATE hubadilisha; DELETE ni kwa vitabu pekee (na inazuiwa kama kitabu kina historia ya mikopo).

`app.py`: app factory na configuration. `database.py`: SQLite connection na schema.
`routes/auth.py`, `routes/books.py`, `routes/members.py`, `routes/loans.py` na `routes/reports.py`:
routes na sheria za kila sehemu ya mfumo. `config.py`: constants za mfumo kama siku za uazimaji,
kikomo cha vitabu na faini. `templates/`: HTML na Jinja. `static/style.css`: muonekano.
`requirements.txt`: dependency ya moja kwa moja.
`test_app.py`: majaribio ya moja kwa moja ya vitabu, wanachama, mikopo na overdue/faini (`python -m unittest test_app`).

## Jaribio la mwanafunzi

Vitabu: Ongeza kitabu chenye nakala 3; kitafute kwa mwandishi; badilisha nakala kuwa 5;
jaribu nakala -1 (ikataliwe); ghairi kufuta kisha thibitisha kufuta.

Wanachama: Sajili mwanachama namba ST100 (mwanafunzi); jaribu kusajili st100 tena (ikataliwe);
tafuta kwa jina na kwa namba; badilisha hali kuwa inactive kisha thibitisha kwenye orodha.

Mikopo: Kopesha kitabu kwa ST100 (lazima iwe active); jaribu kukopesha kitabu kisicho na
nakala zinazopatikana (ikataliwe); rejesha mkopo na thibitisha nakala zinazopatikana zimerudi;
jaribu kufuta kitabu chenye historia ya mikopo (ikataliwe).

Overdue na faini: Kwa kuwa huwezi kusubiri siku 30 kujaribu, mwambie mwalimu/msimamizi
abadilishe due_date ya mkopo mmoja kwenye database (SQLite Viewer au DB Browser for SQLite)
kuwa tarehe iliyopita, kisha fungua /loans kuona "Imechelewa" na faini; jaribu kukopesha
kitabu kingine kwa mwanachama huyo (ikataliwe mpaka arejeshe); rejesha na soma ujumbe wa faini.

Funga na ufungue app kuthibitisha data za vitabu, wanachama na mikopo zinabaki.
Eleza tofauti kati ya rekodi moja ya kitabu na nakala zake, na tofauti kati ya "nakala za jumla" na "nakala zinazopatikana".

## Mipaka

Hili ni toleo la local kwenye PC moja, lenye login ya mhudumu mmoja tu. Usiweke kwenye internet.
Wanachama hawafutwi kabisa — "inactive" pekee. Faini ni hesabu ya kuonyesha tu, si mfumo wa
malipo; hakuna akaunti nyingi, roles, wala historia ya malipo. Sample data ipo kupitia `seed_data.py`.
