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
  wakati bado kwenye mikono). `LOAN_DAYS = 30` na `MAX_ACTIVE_LOANS = 5` ni constants
  juu ya app.py — maamuzi ya mwanzo, yanaweza kubadilishwa pindi sheria rasmi itakapojulikana.
- Routes: GET /loans (orodha yenye hali Kwenye mikono/Imechelewa/Imerejeshwa),
  GET+POST /loans/new (kukopesha), GET+POST /loans/<id>/return (kurejesha).
- Masharti ya kukopa yanayohakikiwa server-side: mwanachama awe active; kitabu kiwe na
  nakala zinazopatikana (copies jumla minus zinazokopeshwa); mwanachama asivuke mikopo 5
  isiyorejeshwa. Mwanachama inactive bado anaweza kurejesha mkopo wake uliopo.
- Ukurasa wa vitabu (`/`) sasa unaonyesha safu "Zinazopatikana" kando ya "Nakala" za jumla.
- Kufuta kitabu kunazuiwa kama kina historia ya mikopo; kubadilisha nakala za kitabu
  kunazuiwa kupungua chini ya idadi inayokopeshwa kwa sasa.

## Imekamilika katika hatua ya nne — Overdue na faini

- Maamuzi ya mtumiaji: faini TZS 1000 kwa siku ya kuchelewa (`FINE_PER_DAY` juu ya app.py);
  mwanachama mwenye mkopo uliochelewa azuiwe kukopa kingine mpaka arejeshe.
- `overdue_days(loan, today)`: siku za kuchelewa zinazokokotolewa kutoka due_date mpaka
  returned_at (kama tayari amerejesha) au mpaka leo (kama bado kwenye mikono — makadirio).
- Orodha ya /loans sasa inaonyesha safu ya "Faini (TZS)" na idadi ya mikopo yaliyochelewa;
  mikopo bado iliyo kwenye mikono inaonyeshwa kama "inayokadiriwa" kwa sababu bado
  haijarejeshwa rasmi.
- /loans/new inazuia mkopo mpya kama mwanachama ana angalau mkopo mmoja uliochelewa
  (returned_at tupu na due_date < leo), kabla hata ya kuangalia kikomo cha mikopo 5.
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
- Kanuni rasmi za muda wa kuazima (kwa sasa siku 30), kikomo cha mikopo (kwa sasa 5), na
  kiwango cha faini (kwa sasa TZS 1000/siku) ni maamuzi ya mwanzo ya mwanafunzi/msimamizi,
  si kanuni rasmi za taasisi — zinaweza kubadilishwa kirahisi kwenye constants za app.py.
- Kama faini zinahitaji kurekodiwa kama zimelipwa/hazijalipwa bado haijathibitishwa.
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

## Hatua zinazofuata

1. Kufanya walkthrough ya presentation kwa kutumia sample data, kisha kuthibitisha kanuni
   za muda wa uazimaji, kikomo cha vitabu na faini na msimamizi/mwalimu.

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
