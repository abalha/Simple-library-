import os
import sqlite3
import tempfile
import time
import unittest
from datetime import date, timedelta
from pathlib import Path
from app import create_app

TEST_LIBRARIAN_USERNAME = "test-librarian"
TEST_LIBRARIAN_PASSWORD = "test-password-not-for-production"
os.environ.setdefault("LIBRARIAN_USERNAME", TEST_LIBRARIAN_USERNAME)
os.environ.setdefault("LIBRARIAN_PASSWORD", TEST_LIBRARIAN_PASSWORD)


def login(client):
    client.get("/login")
    with client.session_transaction() as session:
        token = session["csrf_token"]
    response = client.post(
        "/login",
        data={
            "username": TEST_LIBRARIAN_USERNAME,
            "password": TEST_LIBRARIAN_PASSWORD,
            "csrf_token": token,
        },
    )
    assert response.status_code == 302
    with client.session_transaction() as session:
        return session["csrf_token"]


class LoginTest(unittest.TestCase):
    def test_login_required_and_wrong_password(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.db"
            app = create_app(path)
            app.testing = True
            client = app.test_client()
            self.assertEqual(client.get("/").status_code, 302)
            self.assertEqual(client.get("/login").status_code, 200)
            with client.session_transaction() as session:
                token = session["csrf_token"]
            response = client.post(
                "/login",
                data={"username": "admin", "password": "sipo", "csrf_token": token},
            )
            self.assertIn(b"Jina la mtumiaji au nenosiri si sahihi", response.data)
            response = client.post(
                "/login",
                data={
                    "username": "sipo",
                    "password": TEST_LIBRARIAN_PASSWORD,
                    "csrf_token": token,
                },
            )
            self.assertIn(b"Jina la mtumiaji au nenosiri si sahihi", response.data)
            self.assertIn(b'value="sipo"', response.data)
            self.assertIn(b"password-toggle", response.data)
            self.assertEqual(client.get("/").status_code, 302)
            token = login(client)
            self.assertEqual(client.get("/").status_code, 200)
            self.assertIn(b"Muhtasari wa maktaba", client.get("/").data)
            self.assertEqual(client.get("/reports/books").status_code, 200)
            self.assertEqual(client.get("/reports/loans").status_code, 200)
            self.assertEqual(client.get("/reports/members").status_code, 200)
            self.assertEqual(client.get("/logout").status_code, 405)
            token = login(client)
            self.assertEqual(
                client.post("/logout", data={"csrf_token": token}).status_code, 302
            )
            self.assertEqual(client.get("/").status_code, 302)


class LoginSecurityTest(unittest.TestCase):
    def _client(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        app = create_app(Path(folder.name) / "test.db")
        app.testing = True
        self.app = app
        return app.test_client()

    def _token(self, client):
        client.get("/login")
        with client.session_transaction() as session:
            return session["csrf_token"]

    def test_non_ascii_input_returns_error_not_crash(self):
        client = self._client()
        token = self._token(client)
        response = client.post(
            "/login",
            data={"username": "admiñ", "password": "x", "csrf_token": token},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Jina la mtumiaji au nenosiri si sahihi", response.data)
        response = client.post(
            "/login",
            data={"username": "admin", "password": "nøsenøri", "csrf_token": token},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Jina la mtumiaji au nenosiri si sahihi", response.data)

    def test_expired_form_shows_styled_page(self):
        client = self._client()
        self._token(client)
        response = client.post(
            "/login", data={"username": "admin", "password": "x", "csrf_token": "añ"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Fomu imeisha muda", response.data)
        self.assertIn(b"Rudi kwenye ukurasa wa kuingia", response.data)

    def test_lockout_after_repeated_failures(self):
        client = self._client()
        token = self._token(client)
        for _ in range(5):
            client.post(
                "/login",
                data={"username": TEST_LIBRARIAN_USERNAME, "password": "wrong", "csrf_token": token},
            )
        response = client.post(
            "/login",
            data={
                "username": TEST_LIBRARIAN_USERNAME,
                "password": TEST_LIBRARIAN_PASSWORD,
                "csrf_token": token,
            },
        )
        self.assertEqual(response.status_code, 429)
        self.assertIn(b"Majaribio mengi yamefanywa", response.data)

    def test_lockout_expires_and_grants_fresh_attempts(self):
        client = self._client()
        self.app.config["LOGIN_LOCKOUT_SECONDS"] = 1
        token = self._token(client)
        for _ in range(5):
            client.post(
                "/login",
                data={"username": TEST_LIBRARIAN_USERNAME, "password": "wrong", "csrf_token": token},
            )
        time.sleep(1.2)
        response = client.post(
            "/login",
            data={
                "username": TEST_LIBRARIAN_USERNAME,
                "password": TEST_LIBRARIAN_PASSWORD,
                "csrf_token": token,
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_intended_page_survives_login(self):
        client = self._client()
        response = client.get("/books/new")
        self.assertEqual(response.status_code, 302)
        self.assertIn("next=/books/new", response.headers["Location"])
        token = self._token(client)
        response = client.post(
            "/login",
            data={
                "username": TEST_LIBRARIAN_USERNAME,
                "password": TEST_LIBRARIAN_PASSWORD,
                "csrf_token": token,
                "next": "/books/new",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/books/new"))

    def test_open_redirect_is_rejected(self):
        client = self._client()
        for evil in ["//evil.com/x", "http://evil.com/x", "/\\evil.com/x"]:
            token = self._token(client)
            response = client.post(
                "/login",
                data={
                    "username": TEST_LIBRARIAN_USERNAME,
                    "password": TEST_LIBRARIAN_PASSWORD,
                    "csrf_token": token,
                    "next": evil,
                },
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.headers["Location"], "/")

    def test_password_toggle_keeps_stable_accessible_name(self):
        client = self._client()
        page = client.get("/login").data.decode()
        self.assertIn('aria-label="Onyesha au Ficha nenosiri"', page)
        self.assertIn('data-hide-label="Ficha"', page)
        self.assertNotIn("{{", page.split("<script>")[1])


class FooterTest(unittest.TestCase):
    def _client(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        app = create_app(Path(folder.name) / "test.db")
        app.testing = True
        return app.test_client()

    def test_footer_shows_institution_and_is_not_printed(self):
        client = self._client()
        login_page = client.get("/login").data
        self.assertIn(b'class="app-footer no-print footer-centered"', login_page)
        self.assertIn(b"Library MIS (Assignment1) Haki zote zimehifadhiwa.", login_page)
        self.assertNotIn(b'class="footer-links"', login_page)

        login(client)
        page = client.get("/").data
        self.assertIn(b'class="app-footer no-print"', page)
        self.assertIn(b'class="footer-links"', page)
        self.assertIn(b"Library MIS (Assignment1) Haki zote zimehifadhiwa.", page)
        # footer iko baada ya maudhui, ili iwe chini ya kila ukurasa
        self.assertLess(page.index(b"</main>"), page.index(b"app-footer"))

    def test_footer_translates_to_english(self):
        client = self._client()
        client.get("/login")
        with client.session_transaction() as session:
            token = session["csrf_token"]
        client.post("/language/en", data={"csrf_token": token})
        page = client.get("/login").data
        self.assertIn(b"All rights reserved.", page)


class IconActionsTest(unittest.TestCase):
    def _client(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        app = create_app(Path(folder.name) / "test.db")
        app.testing = True
        return app.test_client()

    def test_action_buttons_use_icons_with_accessible_names(self):
        client = self._client()
        token = login(client)
        client.post(
            "/books/new",
            data={
                "title": "Kitabu cha majaribio",
                "author": "Amina",
                "category": "Elimu",
                "publication_year": "2020",
                "copies": "3",
                "csrf_token": token,
            },
        )
        page = client.get("/").data
        # vitufe vya actions zina icon (SVG) na jina linaloonekana kwa screen reader
        self.assertIn(b"<svg", page)
        self.assertIn(b'class="icon"', page)
        self.assertIn(b'aria-label="Ongeza kitabu"', page)
        self.assertIn(b'aria-label="Tafuta"', page)
        self.assertIn(b'aria-label="Badilisha"', page)
        self.assertIn(b'aria-label="Futa"', page)
        # text haisomi kama maandishi kwenye vitufe hivi
        self.assertNotIn(b">Tafuta</button>", page)
        # dialog ya kufuta bado ina maandishi (hatari haipotokezi kwa icon tu)
        self.assertIn(b"Ndiyo, futa", page)


class FormUsabilityTest(unittest.TestCase):
    def _client(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        app = create_app(Path(folder.name) / "test.db")
        app.testing = True
        return app.test_client()

    def test_forms_explain_fields_and_show_errors_next_to_them(self):
        client = self._client()
        token = login(client)

        # kila fomu ina mfano ndani ya field (placeholder), alama ya "required" na autofocus
        for path, placeholder in [
            ("/books/new", b'placeholder="Jina kamili la kitabu, kwa mfano: Utenzi wa Maisha."'),
            ("/members/new", b'placeholder="Mfano: ST001"'),
            ("/loans/new", b'placeholder="Mfano: ST001"'),
        ]:
            page = client.get(path).data
            self.assertIn(placeholder, page)
            self.assertIn(b'class="required"', page)
            self.assertIn(b"autofocus", page)
            # paneli ya kanuni ipo kando ya fomu ili kutumia nafasi ya widescreen
            self.assertIn(b'class="guidance"', page)

        # hitilafu zinaonyeshwa karibu na field husika, na muhtasari wa juu una viungo
        response = client.post(
            "/books/new",
            data={
                "title": "",
                "author": "Amina",
                "category": "Elimu",
                "publication_year": "2020",
                "copies": "2",
                "csrf_token": token,
            },
        )
        page = response.data
        self.assertIn(b"Hitilafu zilizopatikana", page)
        self.assertIn(b'href="#title"', page)
        self.assertIn(b'aria-invalid="true"', page)
        self.assertIn(b'id="title-error"', page)

        # namba ya mwanachama haipo kwenye fomu ya kuazima inashikilia field yake
        response = client.post(
            "/loans/new",
            data={"member_number": "ST999", "book_id": "", "csrf_token": token},
        )
        page = response.data
        self.assertIn(b'id="member_number-error"', page)
        self.assertIn(b'href="#member_number"', page)

        # fomu ya kuazima ina orodha ya namba za wanachama waliopo (datalist)
        client.post(
            "/members/new",
            data={
                "member_number": "ST900",
                "full_name": "Zainab Omar",
                "member_type": "student",
                "csrf_token": token,
            },
        )
        page = client.get("/loans/new").data
        self.assertIn(b'<datalist id="member-numbers">', page)
        self.assertIn(b'value="ST900"', page)


class ReportsTest(unittest.TestCase):
    def _client(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        app = create_app(Path(folder.name) / "test.db")
        app.testing = True
        return app.test_client()

    def test_reports_explain_themselves(self):
        client = self._client()
        token = login(client)
        for path in [
            "/reports/books",
            "/reports/loans",
            "/reports/members",
            "/reports/current-loans",
            "/reports/overdue",
            "/reports/low-stock",
        ]:
            page = client.get(path).data
            self.assertIn(b"Muhtasari", page)
            self.assertIn(b"Maelezo ya kukokotoa", page)
            self.assertIn(b"Maelezo ya safu", page)
            self.assertIn(b"Msimamizi wa maktaba", page)
        self.assertIn(
            b"Kitabu = jina la kitabu kilichokopeshwa", client.get("/reports/loans").data
        )
        self.assertIn(
            b"vitabu 3 kwa wakati mmoja", client.get("/reports/members").data
        )

    def test_reports_translate_to_english(self):
        client = self._client()
        client.get("/login")
        with client.session_transaction() as session:
            token = session["csrf_token"]
        client.post("/language/en", data={"csrf_token": token})
        client.get("/login")
        with client.session_transaction() as session:
            token = session["csrf_token"]
        client.post(
            "/login",
            data={
                "username": TEST_LIBRARIAN_USERNAME,
                "password": TEST_LIBRARIAN_PASSWORD,
                "csrf_token": token,
            },
        )
        page = client.get("/reports/books").data
        self.assertIn(b"Summary", page)
        self.assertIn(b"How the figures are calculated", page)
        self.assertIn(b"Meaning of each column", page)


class BooksTest(unittest.TestCase):
    def test_crud_validation_and_persistence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.db"
            app = create_app(path)
            app.testing = True
            client = app.test_client()
            token = login(client)
            self.assertEqual(client.get("/").status_code, 200)
            data = dict(
                title="Kitabu cha majaribio",
                author="Amina",
                category="Elimu",
                publication_year="2020",
                copies="3",
                csrf_token=token,
            )
            self.assertEqual(
                client.post(
                    "/books/new", data={**data, "csrf_token": "wrong"}
                ).status_code,
                400,
            )
            response = client.post("/books/new", data={**data, "copies": "-1"})
            self.assertIn(b"jaza namba kamili", response.data)
            self.assertEqual(client.post("/books/new", data=data).status_code, 302)
            self.assertIn(b"Kitabu cha majaribio", client.get("/?q=Amina").data)
            self.assertIn(b"delete-dialog", client.get("/").data)
            self.assertNotIn(b"Kitabu cha majaribio", client.get("/?q=Unknown").data)
            self.assertEqual(
                client.post(
                    "/books/1/edit",
                    data={**data, "title": "<script>test</script>", "copies": "5"},
                ).status_code,
                302,
            )
            fresh_client = create_app(path).test_client()
            login(fresh_client)
            page = fresh_client.get("/").data
            self.assertIn(b"&lt;script&gt;", page)
            self.assertNotIn(b"<script>test</script>", page)
            self.assertEqual(client.get("/books/1/delete").status_code, 200)
            self.assertIn(b"&lt;script&gt;", client.get("/").data)
            self.assertEqual(
                client.post("/books/1/delete", data={"csrf_token": token}).status_code,
                302,
            )
            self.assertEqual(client.get("/books/1/edit").status_code, 404)
            self.assertEqual(
                client.post("/books/1/delete", data={"csrf_token": token}).status_code,
                404,
            )


class MembersTest(unittest.TestCase):
    def test_crud_validation_and_persistence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.db"
            app = create_app(path)
            app.testing = True
            client = app.test_client()
            token = login(client)
            self.assertEqual(client.get("/members").status_code, 200)
            data = dict(
                member_number="st001",
                full_name="Amina Said",
                member_type="student",
                csrf_token=token,
            )
            self.assertEqual(
                client.post(
                    "/members/new", data={**data, "csrf_token": "wrong"}
                ).status_code,
                400,
            )
            response = client.post("/members/new", data={**data, "full_name": ""})
            self.assertIn(b"Jina kamili", response.data)
            response = client.post("/members/new", data={**data, "member_type": "pet"})
            self.assertIn(b"Aina ya mwanachama", response.data)
            response = client.post("/members/new", data={**data, "member_number": ""})
            self.assertIn(b"Namba ya mwanachama", response.data)
            self.assertEqual(client.post("/members/new", data=data).status_code, 302)
            response = client.post("/members/1/edit", data={**data, "status": "banned"})
            self.assertIn(b"Hali", response.data)
            response = client.post(
                "/members/1/edit",
                data={**data, "member_number": "", "status": "active"},
            )
            self.assertIn(b"Namba ya mwanachama", response.data)
            # namba inahifadhiwa kwa uppercase
            self.assertIn(b"ST001", client.get("/members").data)
            # jina na namba hutafutwa
            self.assertIn(b"Amina Said", client.get("/members?q=Amina").data)
            self.assertIn(b"Amina Said", client.get("/members?q=st001").data)
            self.assertNotIn(b"Amina Said", client.get("/members?q=Unknown").data)
            # ST001 na st001 ni mwanachama mmoja; usajili wa pili ukatae
            second = dict(
                member_number="st001",
                full_name="Mwanachama mwingine",
                member_type="student",
                csrf_token=token,
            )
            response = client.post("/members/new", data=second)
            self.assertIn(b"tayari inatumika", response.data)
            # mwanachama wa pili halali kutumia namba ya kwanza wakati wa kubadilisha
            third = dict(
                member_number="ST002",
                full_name="Juma Hassan",
                member_type="teacher",
                csrf_token=token,
            )
            self.assertEqual(client.post("/members/new", data=third).status_code, 302)
            response = client.post(
                "/members/2/edit",
                data={**third, "member_number": "ST001", "status": "active"},
            )
            self.assertIn(b"tayari inatumika", response.data)
            # kubadilisha kuwa inactive kunafanya kazi na kunabaki baada ya kufungua tena
            response = client.post(
                "/members/1/edit",
                data={**data, "member_number": "ST001", "status": "inactive"},
            )
            self.assertEqual(response.status_code, 302)
            fresh_client = create_app(path).test_client()
            login(fresh_client)
            page = fresh_client.get("/members").data
            self.assertIn(b"Haifanyi kazi", page)
            self.assertEqual(client.get("/members/999/edit").status_code, 404)
            self.assertEqual(
                client.post(
                    "/members/999/edit", data={**data, "csrf_token": token}
                ).status_code,
                404,
            )


class LoansTest(unittest.TestCase):
    def test_borrow_return_and_limits(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.db"
            app = create_app(path)
            app.testing = True
            client = app.test_client()
            token = login(client)
            self.assertEqual(client.get("/loans").status_code, 200)
            self.assertIn(
                b"Hakuna matokeo ya utafutaji", client.get("/loans?q=Unknown").data
            )

            def new_book(title, copies):
                client.post(
                    "/books/new",
                    data=dict(
                        title=title,
                        author="Mwandishi",
                        category="Elimu",
                        publication_year="2020",
                        copies=str(copies),
                        csrf_token=token,
                    ),
                )

            def new_member(number, name, kind="student"):
                client.post(
                    "/members/new",
                    data=dict(
                        member_number=number,
                        full_name=name,
                        member_type=kind,
                        csrf_token=token,
                    ),
                )

            new_book("Kitabu A", 2)  # id 1, nakala 2
            for extra in range(2, 7):
                new_book(
                    f"Kitabu {extra}", 1
                )  # id 2..6, nakala 1 kila kimoja, kwa ajili ya kikomo cha mikopo 5
            new_member("st001", "Amina")
            new_member("st002", "Juma")
            new_member("st003", "Hassan", kind="teacher")
            client.post(
                "/members/3/edit",
                data=dict(
                    member_number="st003",
                    full_name="Hassan",
                    member_type="teacher",
                    status="inactive",
                    csrf_token=token,
                ),
            )

            self.assertEqual(
                client.post(
                    "/loans/new",
                    data={
                        "csrf_token": "wrong",
                        "member_number": "st001",
                        "book_id": "1",
                    },
                ).status_code,
                400,
            )
            response = client.post(
                "/loans/new",
                data=dict(member_number="st003", book_id="1", csrf_token=token),
            )
            self.assertIn("hawezi kuazima kitabu".encode(), response.data)
            response = client.post(
                "/loans/new",
                data=dict(member_number="st999", book_id="1", csrf_token=token),
            )
            self.assertIn("Namba ya mwanachama haipo".encode(), response.data)
            response = client.post(
                "/loans/new",
                data=dict(member_number="st001", book_id="999", csrf_token=token),
            )
            self.assertIn("Chagua kitabu halali".encode(), response.data)

            self.assertEqual(
                client.post(
                    "/loans/new",
                    data=dict(member_number="st001", book_id="1", csrf_token=token),
                ).status_code,
                302,
            )
            con = sqlite3.connect(path)
            loan = con.execute(
                "SELECT borrowed_at, due_date FROM loans WHERE id = 1"
            ).fetchone()
            con.close()
            self.assertEqual(
                date.fromisoformat(loan[1]) - date.fromisoformat(loan[0]),
                timedelta(days=30),
            )

            self.assertEqual(
                client.post(
                    "/loans/new",
                    data=dict(member_number="st002", book_id="1", csrf_token=token),
                ).status_code,
                302,
            )
            # nakala 2 za kitabu A zote zimekopeshwa; mwanachama mwingine hawezi kuazima hicho kitabu
            new_member("st004", "Khamis", kind="teacher")
            response = client.post(
                "/loans/new",
                data=dict(member_number="st004", book_id="1", csrf_token=token),
            )
            self.assertIn("Hakuna nakala".encode(), response.data)

            # kikomo cha mikopo 5 kwa mwanachama mmoja
            for book_id in range(2, 7):
                self.assertEqual(
                    client.post(
                        "/loans/new",
                        data=dict(
                            member_number="st004",
                            book_id=str(book_id),
                            csrf_token=token,
                        ),
                    ).status_code,
                    302,
                )
            new_book("Kitabu B", 1)  # id 7
            response = client.post(
                "/loans/new",
                data=dict(member_number="st004", book_id="7", csrf_token=token),
            )
            self.assertIn("hawezi kuazima kingine".encode(), response.data)

            # kikomo cha mwanafunzi ni 3: st002 ana mkopo 1, ongeza 2 zaidi, ya nne inakataliwa
            for extra in range(8, 10):
                new_book(f"Kitabu {extra}", 1)  # ids 8, 9
            for book_id in (8, 9):
                self.assertEqual(
                    client.post(
                        "/loans/new",
                        data=dict(
                            member_number="st002", book_id=str(book_id), csrf_token=token
                        ),
                    ).status_code,
                    302,
                )
            new_book("Kitabu 10", 1)  # id 10
            response = client.post(
                "/loans/new",
                data=dict(member_number="st002", book_id="10", csrf_token=token),
            )
            self.assertIn("hawezi kuazima kingine".encode(), response.data)

            # kufuta kitabu chenye historia ya mikopo hakuruhusiwi
            response = client.post("/books/1/delete", data={"csrf_token": token})
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                client.get("/books/1/edit").status_code, 200
            )  # kitabu bado kipo

            # nakala haziwezi kupungua chini ya zinazokopeshwa kwa sasa (2 zinakopeshwa)
            response = client.post(
                "/books/1/edit",
                data=dict(
                    title="Kitabu A",
                    author="Mwandishi",
                    category="Elimu",
                    publication_year="2020",
                    copies="1",
                    csrf_token=token,
                ),
            )
            self.assertIn("haziwezi kupungua".encode(), response.data)

            # kurejesha kunafanya kazi na kunaongeza nakala zinazopatikana
            self.assertEqual(client.get("/loans/1/return").status_code, 200)
            self.assertEqual(
                client.post("/loans/1/return", data={"csrf_token": token}).status_code,
                302,
            )
            # kurejesha mkopo uliorejeshwa tayari hakuleta hitilafu, inaarifu tu
            response = client.post(
                "/loans/1/return", data={"csrf_token": token}, follow_redirects=True
            )
            self.assertIn(b"tayari kimerejeshwa", response.data)
            response = client.post(
                "/loans/new",
                data=dict(member_number="st003", book_id="1", csrf_token=token),
            )
            # st003 bado ni inactive, hivyo bado hawezi kuazima; hii inathibitisha available iliongezeka lakini status inazuia
            self.assertIn("hawezi kuazima kitabu".encode(), response.data)

            self.assertEqual(client.get("/loans/999/return").status_code, 404)
            self.assertEqual(
                client.post(
                    "/loans/999/return", data={"csrf_token": token}
                ).status_code,
                404,
            )

    def test_overdue_blocking(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.db"
            app = create_app(path)
            app.testing = True
            client = app.test_client()
            token = login(client)
            self.assertEqual(client.get("/loans").status_code, 200)
            client.post(
                "/books/new",
                data=dict(
                    title="Kitabu A",
                    author="Mwandishi",
                    category="Elimu",
                    publication_year="2020",
                    copies="2",
                    csrf_token=token,
                ),
            )
            client.post(
                "/books/new",
                data=dict(
                    title="Kitabu B",
                    author="Mwandishi",
                    category="Elimu",
                    publication_year="2020",
                    copies="1",
                    csrf_token=token,
                ),
            )
            client.post(
                "/members/new",
                data=dict(
                    member_number="st010",
                    full_name="Zainab",
                    member_type="student",
                    csrf_token=token,
                ),
            )
            self.assertEqual(
                client.post(
                    "/loans/new",
                    data=dict(member_number="st010", book_id="1", csrf_token=token),
                ).status_code,
                302,
            )

            # Rudisha nyuma tarehe zote ili kuiga mkopo uliochelewa kwa siku 5,
            # huku due date ikiendelea kuwa baada ya tarehe ya kuazima.
            con = sqlite3.connect(path)
            overdue_due_date = (date.today() - timedelta(days=5)).isoformat()
            con.execute(
                "UPDATE loans SET borrowed_at = ?, due_date = ? WHERE id = 1",
                ((date.today() - timedelta(days=35)).isoformat(), overdue_due_date),
            )
            con.commit()
            con.close()

            page = client.get("/loans").data
            self.assertIn(b"Imechelewa siku 5", page)
            self.assertNotIn(b"TZS", page)  # faini zimeondolewa kabisa

            # mwanachama mwenye mkopo uliochelewa hawezi kuazima kingine, hata kitabu tofauti
            response = client.post(
                "/loans/new",
                data=dict(member_number="st010", book_id="2", csrf_token=token),
            )
            self.assertIn("kitabu kilichochelewa".encode(), response.data)

            # ukurasa wa kuthibitisha kurejesha unaonyesha siku zilizochelewa, bila faini
            response = client.get("/loans/1/return")
            self.assertIn(b"kimechelewa kwa siku 5", response.data)
            self.assertNotIn(b"TZS", response.data)

            # kurejesha kunaondoa uzuiaji na kuarifu siku zilizochelewa
            response = client.post(
                "/loans/1/return", data={"csrf_token": token}, follow_redirects=True
            )
            self.assertIn("Kimechelewa siku 5".encode(), response.data)
            self.assertEqual(
                client.post(
                    "/loans/new",
                    data=dict(member_number="st010", book_id="2", csrf_token=token),
                ).status_code,
                302,
            )


class LanguageTest(unittest.TestCase):
    def test_english_mode_survives_login_and_translations(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.db"
            app = create_app(path)
            app.testing = True
            client = app.test_client()
            # switcher ya lugha ipo kwenye ukurasa wa login kabla ya kuingia
            self.assertIn(b"language-switcher", client.get("/login").data)
            with client.session_transaction() as session:
                token = session["csrf_token"]
            self.assertEqual(
                client.post("/language/en", data={"csrf_token": token}).status_code,
                302,
            )
            self.assertEqual(
                client.post(
                    "/login",
                    data={
                        "username": TEST_LIBRARIAN_USERNAME,
                        "password": TEST_LIBRARIAN_PASSWORD,
                        "csrf_token": token,
                    },
                ).status_code,
                302,
            )
            # login haianguki lugha uliyochagua
            with client.session_transaction() as session:
                token = session["csrf_token"]
            self.assertIn(b"Library summary", client.get("/").data)
            for url in (
                "/members",
                "/loans",
                "/reports/books",
                "/reports/loans",
                "/reports/members",
                "/books/new",
                "/members/new",
                "/loans/new",
            ):
                self.assertEqual(client.get(url).status_code, 200)
            self.assertIn(
                b"No members yet. Start by registering a member.",
                client.get("/members").data,
            )
            # error ya validation kwa EN
            response = client.post(
                "/books/new",
                data={
                    "title": "",
                    "author": "",
                    "category": "",
                    "publication_year": "x",
                    "copies": "x",
                    "csrf_token": token,
                },
            )
            self.assertIn(b"Name: enter 1 to 150 characters", response.data)
            self.assertIn(b"Year: enter a whole number between 1 and", response.data)
            # kurudi Kiswahili
            self.assertEqual(
                client.post("/language/sw", data={"csrf_token": token}).status_code,
                302,
            )
            self.assertIn(b"Muhtasari wa maktaba", client.get("/").data)


if __name__ == "__main__":
    unittest.main()
