# Maendeleo — 4 Novemba 2026

Deadline: 20 Novemba 2026. Delivery: Presentation.

## Maamuzi ya kazi

- Mada inayofanyiwa kazi: Library Management Information System ya taasisi.
- Python + Flask + SQLite + HTML/CSS; setup ya kwanza kwenye Windows ya msimamizi.
- Mwanafunzi ashiriki kuingiza data, kupima, kueleza na kufanya mabadiliko madogo.
- Roadmap ya fullstack ni lengo tofauti.

## Imekamilika katika hatua ya kwanza

- CRUD ya vitabu, utafutaji, validation na jumla za vitabu/nakala.
- Maelekezo ya setup na mazoezi.

## Imekamilika katika hatua ya pili

- Jedwali la `members`: id, member_number (hadi herufi 50, UNIQUE bila kujali uppercase/lowercase,
  huhifadhiwa kwa herufi kubwa), full_name (hadi herufi 150), member_type (student/teacher pekee),
  status (active/inactive pekee, default active).
- Routes: GET /members (orodha + utafutaji wa namba/jina), GET+POST /members/new,
  GET+POST /members/<id>/edit. Hakuna delete; "inactive" hutumika kusimamisha uanachama.
- Database UNIQUE + CHECK constraints pamoja na uhakiki wa server; namba inayojirudia
  inaonyesha ujumbe rafiki badala ya server error, kwenye create na update.

## Imekamilika katika hatua ya tatu

- Jedwali la `loans`: id, book_id, member_id, borrowed_at, due_date, returned_at (NULL
  wakati bado kwenye mikono). `LOAN_DAYS = 30` na kikomo cha mikopo ni constants
  kwenye `config.py` — maamuzi ya mwanzo, yanaweza kubadilishwa pindi sheria rasmi itakapojulikana.
- Routes: GET /loans (orodha yenye hali Kwenye mikono/Imechelewa/Imerejeshwa),
  GET+POST /loans/new (kukopesha), GET+POST /loans/<id>/return (kurejesha).
- Masharti ya kukopa yanayohakikiwa server-side: mwanachama awe active; kitabu kiwe na
  nakala zinazopatikana (copies jumla minus zinazokopeshwa); mwanachama asivuke kikomo
  cha mikopo isiyorejeshwa. Mwanachama inactive bado anaweza kurejesha mkopo wake uliopo.
- Ukurasa wa vitabu (`/`) sasa unaonyesha safu "Zinazopatikana" kando ya "Nakala" za jumla.
- Kufuta kitabu kunazuiwa kama kina historia ya mikopo; kubadilisha nakala za kitabu
  kunazuiwa kupungua chini ya idadi inayokopeshwa kwa sasa.

## Imekamilika katika hatua ya nne — Overdue na faini

- Maamuzi ya mtumiaji: faini TZS 1000 kwa siku ya kuchelewa (`FINE_PER_DAY` kwenye config.py);
  mwanachama mwenye mkopo uliochelewa azuiwe kukopa kingine mpaka arejeshe.
- `overdue_days(loan, today)`: siku za kuchelewa zinazokokotolewa kutoka due_date mpaka
  returned_at (kama tayari amerejesha) au mpaka leo (kama bado kwenye mikono — makadirio).
- Orodha ya /loans sasa inaonyesha safu ya "Faini (TZS)" na idadi ya mikopo yaliyochelewa;
  mikopo bado iliyo kwenye mikono inaonyeshwa kama "inayokadiriwa" kwa sababu bado
  haijarejeshwa rasmi.
- /loans/new inazuia mkopo mpya kama mwanachama ana angalau mkopo mmoja uliochelewa
  (returned_at tupu na due_date < leo), kabla hata ya kuangalia kikomo cha mikopo.
- /loans/<id>/return inaonyesha onyo la siku zilizochelewa na faini kabla ya kuthibitisha,
  na baada ya kurejesha inaarifu faini ya mwisho (iliyohesabiwa kwa tarehe halisi ya kurejesha).
- Faini ni hesabu ya kuonyesha tu kwa sasa — hakuna jedwali la malipo/kumbukumbu ya
  "imelipwa"; hiyo haijaombwa bado.
- Backup ya `library.db` yenye timestamp ilitengenezwa kabla ya mabadiliko haya (hakuna
  schema mpya, logic tu, lakini backup ilitengenezwa kwa tahadhari).
- Majaribio ya moja kwa moja (`test_app.py`, sasa tests 4) yanathibitisha: nakala/jedwali
  la awali, usajili/update/uniqueness ya wanachama, kukopesha/kurejesha/kikomo/kuzuia
  kufuta-kupunguza-nakala, na sasa overdue/faini/uzuiaji wa kukopa kwa mwenye mkopo
  uliochelewa (kwa kuiga due_date ya zamani moja kwa moja kwenye test database).

## Bado haijathibitishwa

- Kozi ya mwanafunzi na uhusiano wa mada na field yake.
- Akaunti ya mhudumu pekee ni pendekezo, si hitaji lililothibitishwa.
- Kanuni rasmi za muda wa kuazima (kwa sasa siku 30) na kikomo cha mikopo (kwa sasa
  mwanafunzi 3, mwalimu 5) ni maamuzi ya mwanzo ya mwanafunzi/msimamizi, si kanuni rasmi
  za taasisi — zinaweza kubadilishwa kirahisi kwenye constants za config.py.
- OS/vifaa vya mwanafunzi na muda wake wa kujifunza.

## Imekamilika katika hatua ya tano — Login na ripoti

- Login ya mhudumu mmoja inalinda kurasa za vitabu, wanachama, mikopo na ripoti; route ya
  `/logout` huondoa session.
- Taarifa za majaribio ni username `admin` na password `maktaba2026`; zinaweza kubadilishwa
  kwa environment variables `LIBRARIAN_USERNAME` na `LIBRARIAN_PASSWORD` kabla ya kuendesha app.
- Route ya `/reports/books` huonyesha rekodi za vitabu, jumla ya nakala na nakala
  zinazopatikana, na ina kitufe cha kuchapisha kupitia browser.
- Route ya `/reports/loans` huonyesha vitabu vilivyoazimwa, hali zake, overdue na makadirio ya faini;
  pia inaweza kuchapishwa.
- Route ya `/reports/members` huonyesha wanachama, aina zao na hali ya uanachama;
  pia inaweza kuchapishwa.
- Majaribio ya moja kwa moja sasa ni tests 5; yanajumuisha login, vitabu, wanachama,
  mikopo, overdue na faini.

## Imekamilika katika hatua ya sita — kikomo kwa aina, tafsiri kamili, na usafi wa git

- Kikomo cha mikopo sasa kinatofautishwa kwa aina ya mwanachama: mwanafunzi vitabu 3
  (`MAX_STUDENT_LOANS`), mwalimu vitabu 5 (`MAX_TEACHER_LOANS`) — constants kwenye
  config.py, zimebadilishwa kutoka `MAX_ACTIVE_LOANS` moja ya awali.
- seed_data.py ilirekebishwa: wanachama walikuwa wame-comment out hivyo kuweka sample data
  kuliangukia na FOREIGN KEY constraint; sasa inaweka vitabu 6, wanachama 5, mikopo 4
  kama ilivyoahidiwa.
- Backup za database (`library.db.backup_*`) zimeondolewa kwenye git tracking (files
  zimebaki kwenye kompyuta); .gitignore sasa inalinda `*.db` na `library.db.backup_*`.
- Tafsiri ya English imekamilika: error messages zote za validation na sheria za mikopo,
  ukurasa wa kurejesha, dialogs za kufuta, ripoti tatu, na search labels — sasa zote zina
  tafsiri kwenye i18n.py. Language switcher ipo pia kwenye ukurasa wa login, na login
  hai tena haituwi lugha uliyochagua (session.clear inahifadhi "language").
- README: maelekezo ya macOS/Linux yameongezwa, na maelezo ya kikomo cha mikopo yamesasishwa.
- Test ya mikopo sasa inathibitisha kikomo cha mwanafunzi (3) kando ya cha mwalimu (5).
- `active_loans_for_book` imeunganishwa mahali pamoja kwenye routes/loans.py — ilikuwa
  imeandikwa mara mbili (books.py na loans.py) na ingeweza kutofautiana siku moja.
- SECRET_KEY sasa inahifadhiwa kwenye `.secret_key` (git-ignored) badala ya kuzalishwa
  upya kila uzinduzi — mhudumu habude kuingia tena kila app ikizimwa na kuwashwa.
- Test mpya ya sita (LanguageTest) inalinda tafsiri ya English: switcher kwenye login,
  lugha isipotee kwenye login, kurasa kuu zote, error ya validation, na kurudi Kiswahili.

## Imekamilika katika hatua ya saba — faini zimeondolewa (7 Novemba 2026)

- Maamuzi rasmi: maktaba HAINA faini. Hii inabadilisha maamuzi ya hatua ya nne
  (faini TZS 1000/siku) — hati hii hapa juu inabaki kama kumbukumbu ya historia tu.
- Kila kitu cha faini kimeondolewa: `FINE_PER_DAY` (config.py), safu ya "Faini (TZS)"
  kwenye /loans na ripoti ya mikopo, "Makadirio ya faini" kwenye dashboard na ripoti,
  onyo la faini kwenye ukurasa wa kurejesha, ujumbe wa faini baada ya kurejesha,
  na tafsiri zake zote kwenye i18n.py.
- Adhabu pekee ya kuchelewa ni uzuiaji: mwanachama mwenye mkopo uliochelewa hawezi
  kukopa kitabu kingine mpaka arejeshe (`member_has_overdue` kwenye routes/loans.py).
- Siku zilizochelewa bado zinaonyeshwa ("Imechelewa siku X") kama taarifa, si pesa.
- Test ya overdue imesasishwa: inathibitisha kurasa hazionyeshi "TZS" yoyote, na
  kuwa uzuiaji unaondolewa baada ya kurejesha.

## Imekamilika katika hatua ya nane — Usalama wa ukurasa wa kuingia (11 Novemba 2026)

- Ukurasa wa kuingia ulipitiwa kwa mabadiliko yote yaliyoelezwa hapa chini; majaribio 13
  sasa yanapita (`test_app.py`, wawili 7 mpya).
- `secrets.compare_digest` ilikuwa ikihitilafu `TypeError` kwa herufi za non-ASCII (jina
  la mtumiaji au nenosiri lenye "ñ"), ikihitilafu ukurasa wa 500 badala ya ujumbe wa kosa.
  Sasa `_same()` ina-encode UTF-8 kabla ya kulinganisha.
- Kizuizi cha majaribio: baada ya 5 kumbukumbu za kufaili (`LOGIN_MAX_ATTEMPTS`) akaunti
  hufungwa kwa sekunde 300 (`LOGIN_LOCKOUT_SECONDS`) kwa kila IP. Hesabu ipo kwenye
  kumbukumbu ya app (moja kwa app moja); baada ya kifungu kuisha hesabu inaanza upya.
- Ukurasa wa 400 (fomu ya CSRF iliyochaka) sasa unapanda kwa mtindo wa app kwenye
  `templates/error.html` badala ya ukurasa chafu wa Flask, na ujumbe unatafsiriwa.
- Ukurasa uliotarajiwa umehifadhiwa: `require_login` huingiza `?next=...` na baada ya
  kuingia mtumiaji anarudi kwenye ukurasa uliotaka. URL za nje zinakataliwa (`_safe_next`).
- Button ya kuonyesha nenosiri sasa ina jina la kile accessibility lililoshara (`aria-label`
  ya kudumu + `aria-pressed`); maandishi ya "Onyesha/Ficha" yamewekwa kwenye `data-`
  attributes badala ya Jinja ndani ya `<script>`.
- CSS: `.password-control` sasa ni flex na button ya nenosiri imeondolewa 3px chini ya
  input; kadi ya ukurasa wa hitilafu ina mitindo yake.
- Session ina muda wa mwisho wa saa 8 (`PERMANENT_SESSION_LIFETIME`).
- App inaonyesha onyo kwenye kuanzia ikiwa nenosiri la majaribio linatumika.
- Brute-force imejaribiwa dhidi ya server inayorusha kwa kweli: majaribio 4 ya bure, ya
  tano na zilizobaki zinakataliwa kwa 429; lockout inaendelea hata kwa session mpya.

## Imekamilika katika hatua ya tisa — Ripoti za muundo wa kitaalamu (11 Novemba 2026)

- Kila ripoti (vitabu, mikopo, wanachama) sasa ina muundo rasmi: kichwa chenye nembo, jina
  la mfumo, jina la ripoti na subtituli, tarehe ya kutengenezwa na jina la msimamizi wa
  maktaba; **Muhtasari**; kadi za takwimu; **Maelezo ya kukokotoa** (jinsi kila namba
  ilivyopatikana, kwa mfano kinao); jedwali; **Maelezo ya safu** (maana ya kila safu);
  **Maelezo ya hali**; **Kanuni zilizotumika** (muda wa kuazimaji na vikomo vya mwanafunzi
  na mwalimu, vinavyotokana na `config.py` ili zibaki sahihi); na mguu wa ripoti.
- Sehemu hizi zinatumika kwa madokezo yote matatu (`templates/_report.html`), hivyo
  muundo wa ripoti unashirikiwa na hakuna kunakiliwa.
- Uchapishaji: sidebar na header za app hazitakiwi; mguu wa ripoti unaonyesha kila
  ukurasa; maelezo hayawezi kukatika katika ukurasa wa A4.
- Maelezo yote yameongezwa kwenye `i18n.py` kwa Kiswahili na English; majaribio 15
  (wawili 2 mpya) yanathibitisha kawa ripoti zinaeleweka na zina tafsiri kwa English.

## Imekamilika katika hatua ya kumi — Footer ya kiwango cha mfumo (12 Novemba 2026)

- Kila ukurasa (kuwa ndogo ya ukurasa wa kuingia) sasa una footer ya kizana: nembo na jina
  la mfumo, viungo vya menyu (Vitabu, Wanachama, Vilivyoazimwa, Ripoti — zinaonekana tu
  mtu ameingia), jina la msimamizi wa maktaba na taarifa ya toleo la mafunzo, na mguu wa
  haki za uandikishaji (`© 2026 Maktaba — Library MIS`).
- Footer imewekwa ndani ya kila maudhui (`.shell-body`), kwa hiyo inalingana na safu ya
  ukurasa huku ya upande wa kulia; sidebar inabaki kwa urefu wote. Kwenye ukurasa wa
  kuingia footer huwa nafasi ya kati, ili isionekane kuwa tupu.
- Mguu wa mfumo ni `no-print`: kuchapisha ripoti hupangi na footer ya app (kila ripoti
  ina mguu wake wa data). Majaribio 17 (wawili 2 mpya) yanathibitisha kuwango, mchango
  wa haki za uandikishaji na tafsiri ya English.

## Imekamilika katika hatua ya kumi na moja — Vitufe kwa alama (icons) badala ya maneno (12 Novemba 2026)

- Kila kitufe na kiungo cha hatua sasa kinaonyesha alama (icon) badala ya maneno: kuongeza
  (+), kutafuta (kioo), kuonyesha vyote (orodha), kubadilisha (karatasi), kufuta (chupa),
  kurejesha (←), kuhifadhi (diski), kufuta (×), kupinga (printer) na kutoka (kufungua mlango).
- Alama zimeandikwa ndani ya `templates/_icons.html` kama macro ya SVG — hakuna dependency
  ya nje na hakuna internet, hivyo mfumo bado unaenda offline kama ulivyokuwa.
- Kila kitufe chenye alama pekee lina `title` (tooltip) na `aria-label` yenye maana tafsiri
  iliyopo tayari kwenye `i18n.py`; maana hizi hazihitaji mistari mpya ya tafsiri.
- Majiko ya uthibitisho ("Ndiyo, futa" / "Ghairi") na kitufe cha kuingia bado zinaonyesha
  maneno, ili hatari ionekane wazi kabla ya kufanya jambo lisio reversible.
- Majaribio 18 (moja mpya) yanathibitisha kuwa vitufe vina alama zilizo na majina yanayopatikana
  kwa kipeperushi, na kuwa maneno ya vitufe sasa yameondolewa kwenye vitufe vya hatua.

## Imekamilika katika hatua ya kumi na mbili — Fomu rahisi kutumia (UI/UX) (12 Novemba 2026)

- Fomu zote tatu (kitabu, mwanachama, kukopesha kitabu) sasa zinatumia mwundo mmoja
  (`templates/_form.html`): lebo yenye alama ya `*`, maelezo ya kusaidia chini ya kila field,
  `aria-describedby`, `aria-invalid` kwenye field zenye hitilafu, na autofocus kwenye field
  ya kwanza.
- Hitilafu sasa zinashikiliwa na field yake badala ya kuorodhesha tu: routes zinatumia
  `errors` kama kamusi (dict) badala ya orodha, na kila fomu inaonyesha muhtasari wa hitilafu
  mwandamoni wenye viungo vinavyounda kwenye field husika pamoja na ujumbe chini ya field.
  Maadili ya yaliyojazwa hapo awali zinabaki.
- Vitufe vya kuwasilisha na kughairi vina alama pamoja na maandishi ("Hifadhi", "Ghairi",
  "Kopesha kitabu") ili hatua ya msingi ionekane wazi kabla ya kubofya.
- Fomu ya kukopesha kitabu: orodha ya namba za wanachama walio hai (datalist), nakala
  zinazopatikana kwa kila kitabu (zinazobaki hazichagulikiwi), na onyesho la tarehe ya
  mwisho kabla ya kukopa.
- Majaribio 19 (moja mpya) yanathibitisha maelezo ya kusaidia, alama za required, autofocus,
  hitilafu zilizo karibu na field zake, muhtasari wa hitilafu wenye viungo, na datalist ya
  wanachama.

## Hatua zinazofuata

1. Kufanya walkthrough ya presentation kwa kutumia sample data, kisha kuthibitisha kanuni
   za muda wa uazimaji, kikomo cha vitabu na faini na msimamizi/mwalimu.
2. Ikiwa app itaendeshwa kwa zaidi ya mmoja process au nyuma ya reverse proxy, counter ya
   lockout inapaswa kushirikwa (database/Redis) na `ProxyFix` kuwasha ili `remote_addr`
   iwe IP ya mteja — sasa wote watumiaji wangeishare hesabu moja.
3. Nenosiri la mhudumu bado liko kwa plaintext kwenye `config.py`; kuihash ni mabadiliko
   makubwa ya jinsi taarifa hiyo inavyowekwa, hivyo inahitaji maamuzi mapya.

## Maandalizi ya presentation

- `seed_data.py` huweka sample data kwenye database tupu pekee: vitabu 6, wanachama 5,
  mikopo 4, na mifano ya mkopo wa kawaida, uliochelewa na uliorejeshwa.
- Code imepangwa kwa modules: `database.py` kwa SQLite, `config.py` kwa constants, na
  `routes/` kwa authentication, vitabu, wanachama, vitabu vilivyoazimwa na ripoti.

Mhudumu ndiye anayehakiki kitambulisho kabla ya usajili; hakuna integration ya moja
kwa moja na mfumo wa chuo. Historia ya mikopo isifutwe baadaye.

## Kumbuko la kiufundi

Wakati wa majaribio ya hatua ya tatu, process ya zamani ya `python app.py` ilikuwa
bado inaendesha kwenye port 5000 kutoka kwenye terminal nyingine (bila routes mpya za
mikopo), jambo lililosababisha matokeo ya 404 ya muda kwenye smoke test. Ikiwa browser
inaonyesha tabia ya zamani baada ya mabadiliko ya app.py, simamisha terminal zote
zinazoendesha app.py (Ctrl+C) kisha uanzishe tena moja tu.
