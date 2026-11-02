# Maktaba — Hatua ya 1, 2, 3 na 4

Project ya kujifunza CRUD kwa Python, Flask, SQLite na HTML/CSS.
Hili si toleo kamili la assignment. Limekamilisha vitabu, wanachama, mikopo na overdue/faini.

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
- Hali active/inactive kwa sasa ni taarifa tu; haizuii bado kukopesha kitabu
  kwa sababu uazimaji haujaongezwa. Mhudumu ndiye anayehakiki kitambulisho
  kabla ya kusajili; hakuna integration na mfumo wa chuo.

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

## Usalama na uhakiki (vitabu, wanachama, mikopo na faini)

- POST forms zina CSRF token; SQL hutumia parameters; templates zina escape ya maandishi.
- Database ina UNIQUE na CHECK constraints (mfano member_number ya kipekee,
  member_type/status zinazokubalika pekee) pamoja na uhakiki upande wa server.
- Namba ya mwanachama inayojirudia inaonyesha ujumbe wa kueleweka badala ya server error.
- Masharti ya mikopo (hali ya mwanachama, mkopo uliochelewa, nakala zinazopatikana, kikomo
  cha mikopo 5) yanahakikiwa upande wa server kabla ya kuhifadhi mkopo mpya.

## Jinsi code inavyoungana

1. Browser inatuma GET / , GET /members au GET /loans kupata orodha.
2. Route kwenye app.py inasoma SQLite (ikiwemo JOIN kati ya loans, books na members) na kutuma data kwenye template.
3. Mtumiaji anafungua /books/new, /members/new au /loans/new na kujaza fomu.
4. POST inakaguliwa; ikiwa sahihi INSERT/UPDATE inahifadhi taarifa.
5. Namba ya mwanachama inayojirudia inakamatwa na database (UNIQUE) na kuonyeshwa kama ujumbe rafiki.
6. Kukopesha kunaandika borrowed_at na due_date (leo + siku 30); kurejesha kunaweka returned_at.
7. Kabla ya kukopesha, server inahakiki due_date za mikopo isiyorejeshwa ya mwanachama dhidi ya
   tarehe ya leo (string za ISO format zinalinganishwa moja kwa moja) kuamua kama ana mkopo uliochelewa.
8. Redirect inarudisha orodha. UPDATE hubadilisha; DELETE ni kwa vitabu pekee (na inazuiwa kama kitabu kina historia ya mikopo).

`app.py`: routes, validation na database (vitabu, wanachama, mikopo na faini). `templates/`: HTML na Jinja.
`static/style.css`: muonekano. `requirements.txt`: dependency ya moja kwa moja.
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

Hili ni toleo la local kwenye PC moja, bila login wala ruhusa. Usiweke kwenye internet.
Wanachama hawafutwi kabisa — "inactive" pekee. Faini ni hesabu ya kuonyesha tu, si mfumo wa
malipo; hakuna login ya mhudumu wala ripoti bado. Hakuna sample data ya kujifanya taarifa halisi.
