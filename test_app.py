import sqlite3
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from app import create_app, DEFAULT_LIBRARIAN_PASSWORD


def login(client):
    client.get('/login')
    with client.session_transaction() as session:
        token = session['csrf_token']
    response = client.post('/login', data={'password': DEFAULT_LIBRARIAN_PASSWORD, 'csrf_token': token})
    assert response.status_code == 302
    return token


class LoginTest(unittest.TestCase):
    def test_login_required_and_wrong_password(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'test.db'
            app = create_app(path)
            app.testing = True
            client = app.test_client()
            self.assertEqual(client.get('/').status_code, 302)
            self.assertEqual(client.get('/login').status_code, 200)
            with client.session_transaction() as session:
                token = session['csrf_token']
            response = client.post('/login', data={'password': 'sipo', 'csrf_token': token})
            self.assertIn(b'Password si sahihi', response.data)
            self.assertEqual(client.get('/').status_code, 302)
            self.assertEqual(login(client), token)
            self.assertEqual(client.get('/').status_code, 200)
            self.assertEqual(client.get('/logout').status_code, 302)
            self.assertEqual(client.get('/').status_code, 302)


class BooksTest(unittest.TestCase):
    def test_crud_validation_and_persistence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'test.db'
            app = create_app(path)
            app.testing = True
            client = app.test_client()
            token = login(client)
            self.assertEqual(client.get('/').status_code, 200)
            data = dict(title='Kitabu cha majaribio', author='Amina', category='Elimu', publication_year='2020', copies='3', csrf_token=token)
            self.assertEqual(client.post('/books/new', data={**data, 'csrf_token': 'wrong'}).status_code, 400)
            response = client.post('/books/new', data={**data, 'copies': '-1'})
            self.assertIn(b'jaza namba kamili', response.data)
            self.assertEqual(client.post('/books/new', data=data).status_code, 302)
            self.assertIn(b'Kitabu cha majaribio', client.get('/?q=Amina').data)
            self.assertNotIn(b'Kitabu cha majaribio', client.get('/?q=Unknown').data)
            self.assertEqual(client.post('/books/1/edit', data={**data, 'title': '<script>test</script>', 'copies': '5'}).status_code, 302)
            fresh_client = create_app(path).test_client()
            login(fresh_client)
            page = fresh_client.get('/').data
            self.assertIn(b'&lt;script&gt;', page)
            self.assertNotIn(b'<script>test</script>', page)
            self.assertEqual(client.get('/books/1/delete').status_code, 200)
            self.assertIn(b'&lt;script&gt;', client.get('/').data)
            self.assertEqual(client.post('/books/1/delete', data={'csrf_token': token}).status_code, 302)
            self.assertEqual(client.get('/books/1/edit').status_code, 404)
            self.assertEqual(client.post('/books/1/delete', data={'csrf_token': token}).status_code, 404)


class MembersTest(unittest.TestCase):
    def test_crud_validation_and_persistence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'test.db'
            app = create_app(path)
            app.testing = True
            client = app.test_client()
            token = login(client)
            self.assertEqual(client.get('/members').status_code, 200)
            data = dict(member_number='st001', full_name='Amina Said', member_type='student', csrf_token=token)
            self.assertEqual(client.post('/members/new', data={**data, 'csrf_token': 'wrong'}).status_code, 400)
            response = client.post('/members/new', data={**data, 'full_name': ''})
            self.assertIn(b'Jina kamili', response.data)
            response = client.post('/members/new', data={**data, 'member_type': 'pet'})
            self.assertIn(b'Aina ya mwanachama', response.data)
            response = client.post('/members/new', data={**data, 'member_number': ''})
            self.assertIn(b'Namba ya mwanachama', response.data)
            self.assertEqual(client.post('/members/new', data=data).status_code, 302)
            response = client.post('/members/1/edit', data={**data, 'status': 'banned'})
            self.assertIn(b'Hali', response.data)
            response = client.post('/members/1/edit', data={**data, 'member_number': '', 'status': 'active'})
            self.assertIn(b'Namba ya mwanachama', response.data)
            # namba inahifadhiwa kwa uppercase
            self.assertIn(b'ST001', client.get('/members').data)
            # jina na namba hutafutwa
            self.assertIn(b'Amina Said', client.get('/members?q=Amina').data)
            self.assertIn(b'Amina Said', client.get('/members?q=st001').data)
            self.assertNotIn(b'Amina Said', client.get('/members?q=Unknown').data)
            # ST001 na st001 ni mwanachama mmoja; usajili wa pili ukatae
            second = dict(member_number='st001', full_name='Mwanachama mwingine', member_type='student', csrf_token=token)
            response = client.post('/members/new', data=second)
            self.assertIn(b'tayari inatumika', response.data)
            # mwanachama wa pili halali kutumia namba ya kwanza wakati wa kubadilisha
            third = dict(member_number='ST002', full_name='Juma Hassan', member_type='teacher', csrf_token=token)
            self.assertEqual(client.post('/members/new', data=third).status_code, 302)
            response = client.post('/members/2/edit', data={**third, 'member_number': 'ST001', 'status': 'active'})
            self.assertIn(b'tayari inatumika', response.data)
            # kubadilisha kuwa inactive kunafanya kazi na kunabaki baada ya kufungua tena
            response = client.post('/members/1/edit', data={**data, 'member_number': 'ST001', 'status': 'inactive'})
            self.assertEqual(response.status_code, 302)
            fresh_client = create_app(path).test_client()
            login(fresh_client)
            page = fresh_client.get('/members').data
            self.assertIn(b'Haifanyi kazi', page)
            self.assertEqual(client.get('/members/999/edit').status_code, 404)
            self.assertEqual(client.post('/members/999/edit', data={**data, 'csrf_token': token}).status_code, 404)


class LoansTest(unittest.TestCase):
    def test_borrow_return_and_limits(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'test.db'
            app = create_app(path)
            app.testing = True
            client = app.test_client()
            token = login(client)
            self.assertEqual(client.get('/loans').status_code, 200)

            def new_book(title, copies):
                client.post('/books/new', data=dict(title=title, author='Mwandishi', category='Elimu',
                                                      publication_year='2020', copies=str(copies), csrf_token=token))

            def new_member(number, name, kind='student'):
                client.post('/members/new', data=dict(member_number=number, full_name=name, member_type=kind, csrf_token=token))

            new_book('Kitabu A', 2)  # id 1, nakala 2
            for extra in range(2, 7):
                new_book(f'Kitabu {extra}', 1)  # id 2..6, nakala 1 kila kimoja, kwa ajili ya kikomo cha mikopo 5
            new_member('st001', 'Amina')
            new_member('st002', 'Juma')
            new_member('st003', 'Hassan', kind='teacher')
            client.post('/members/3/edit', data=dict(member_number='st003', full_name='Hassan', member_type='teacher',
                                                       status='inactive', csrf_token=token))

            self.assertEqual(client.post('/loans/new', data={'csrf_token': 'wrong', 'member_number': 'st001', 'book_id': '1'}).status_code, 400)
            response = client.post('/loans/new', data=dict(member_number='st003', book_id='1', csrf_token=token))
            self.assertIn('hawezi kukopa kitabu'.encode(), response.data)
            response = client.post('/loans/new', data=dict(member_number='st999', book_id='1', csrf_token=token))
            self.assertIn('Namba ya mwanachama haipo'.encode(), response.data)
            response = client.post('/loans/new', data=dict(member_number='st001', book_id='999', csrf_token=token))
            self.assertIn('Chagua kitabu halali'.encode(), response.data)

            self.assertEqual(client.post('/loans/new', data=dict(member_number='st001', book_id='1', csrf_token=token)).status_code, 302)
            con = sqlite3.connect(path)
            loan = con.execute('SELECT borrowed_at, due_date FROM loans WHERE id = 1').fetchone()
            con.close()
            self.assertEqual(date.fromisoformat(loan[1]) - date.fromisoformat(loan[0]), timedelta(days=30))

            self.assertEqual(client.post('/loans/new', data=dict(member_number='st002', book_id='1', csrf_token=token)).status_code, 302)
            # nakala 2 za kitabu A zote zimekopeshwa; mwanachama mwingine hawezi kukopa hicho kitabu
            new_member('st004', 'Khamis')
            response = client.post('/loans/new', data=dict(member_number='st004', book_id='1', csrf_token=token))
            self.assertIn('Hakuna nakala'.encode(), response.data)

            # kikomo cha mikopo 5 kwa mwanachama mmoja
            for book_id in range(2, 7):
                self.assertEqual(client.post('/loans/new', data=dict(member_number='st004', book_id=str(book_id), csrf_token=token)).status_code, 302)
            new_book('Kitabu B', 1)  # id 7
            response = client.post('/loans/new', data=dict(member_number='st004', book_id='7', csrf_token=token))
            self.assertIn('hawezi kukopa kingine'.encode(), response.data)

            # kufuta kitabu chenye historia ya mikopo hakuruhusiwi
            response = client.post('/books/1/delete', data={'csrf_token': token})
            self.assertEqual(response.status_code, 302)
            self.assertEqual(client.get('/books/1/edit').status_code, 200)  # kitabu bado kipo

            # nakala haziwezi kupungua chini ya zinazokopeshwa kwa sasa (2 zinakopeshwa)
            response = client.post('/books/1/edit', data=dict(title='Kitabu A', author='Mwandishi', category='Elimu',
                                                                publication_year='2020', copies='1', csrf_token=token))
            self.assertIn('haziwezi kupungua'.encode(), response.data)

            # kurejesha kunafanya kazi na kunaongeza nakala zinazopatikana
            self.assertEqual(client.get('/loans/1/return').status_code, 200)
            self.assertEqual(client.post('/loans/1/return', data={'csrf_token': token}).status_code, 302)
            # kurejesha mkopo uliorejeshwa tayari hakuleta hitilafu, inaarifu tu
            response = client.post('/loans/1/return', data={'csrf_token': token}, follow_redirects=True)
            self.assertIn(b'tayari kimerejeshwa', response.data)
            response = client.post('/loans/new', data=dict(member_number='st003', book_id='1', csrf_token=token))
            # st003 bado ni inactive, hivyo bado hawezi kukopa; hii inathibitisha available iliongezeka lakini status inazuia
            self.assertIn('hawezi kukopa kitabu'.encode(), response.data)

            self.assertEqual(client.get('/loans/999/return').status_code, 404)
            self.assertEqual(client.post('/loans/999/return', data={'csrf_token': token}).status_code, 404)

    def test_overdue_fine_and_blocking(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'test.db'
            app = create_app(path)
            app.testing = True
            client = app.test_client()
            token = login(client)
            self.assertEqual(client.get('/loans').status_code, 200)
            client.post('/books/new', data=dict(title='Kitabu A', author='Mwandishi', category='Elimu',
                                                  publication_year='2020', copies='2', csrf_token=token))
            client.post('/books/new', data=dict(title='Kitabu B', author='Mwandishi', category='Elimu',
                                                 publication_year='2020', copies='1', csrf_token=token))
            client.post('/members/new', data=dict(member_number='st010', full_name='Zainab', member_type='student', csrf_token=token))
            self.assertEqual(client.post('/loans/new', data=dict(member_number='st010', book_id='1', csrf_token=token)).status_code, 302)

            # rudisha nyuma tarehe ya mwisho (due_date) ili kuiga mkopo uliochelewa kwa siku 5
            con = sqlite3.connect(path)
            overdue_due_date = (date.today() - timedelta(days=5)).isoformat()
            con.execute('UPDATE loans SET due_date = ? WHERE id = 1', (overdue_due_date,))
            con.commit()
            con.close()

            page = client.get('/loans').data
            self.assertIn(b'Imechelewa siku 5', page)
            self.assertIn(b'5000', page)  # faini: siku 5 x TZS 1000

            # mwanachama mwenye mkopo uliochelewa hawezi kukopa kingine, hata kitabu tofauti
            response = client.post('/loans/new', data=dict(member_number='st010', book_id='2', csrf_token=token))
            self.assertIn('mkopo uliochelewa'.encode(), response.data)

            # ukurasa wa kuthibitisha kurejesha unaonyesha faini
            response = client.get('/loans/1/return')
            self.assertIn(b'umechelewa kwa siku 5', response.data)
            self.assertIn(b'5000', response.data)

            # kurejesha kunaondoa uzuiaji na kuarifu faini
            response = client.post('/loans/1/return', data={'csrf_token': token}, follow_redirects=True)
            self.assertIn('Kimechelewa siku 5; faini TZS 5000'.encode(), response.data)
            self.assertEqual(client.post('/loans/new', data=dict(member_number='st010', book_id='2', csrf_token=token)).status_code, 302)


if __name__ == '__main__':
    unittest.main()
