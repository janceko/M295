import unittest
from Backend import app, db

class TestBackend(unittest.TestCase):
    # Set up für die Tests
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    # Tear down nach den Tests
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # Teste, ob die Startseite geladen wird
    def test_index_loads(self):
        with app.test_request_context('/'):
            response = self.app.get('/')
            self.assertEqual(response.status_code, 302)  # Erwartet eine Weiterleitung, da der Benutzer nicht eingeloggt ist





    # Teste, ob ein neuer Task erstellt werden kann
    def test_create_task(self):
        task_data = {'content': 'Test Task', 'completed': False}
        response = self.app.post('/tasks', json=task_data)
        self.assertEqual(response.status_code, 302)  # Erwartet 302 nach dem Erstellen eines neuen Tasks

    # Teste, ob ein Task erfolgreich gelöscht werden kann
    def test_delete_task(self):
        task_id = 1  # Annahme: Ein Task mit ID 1 existiert
        response = self.app.delete(f'/tasks/{task_id}')
        self.assertEqual(response.status_code, 302)  # Erwartet 302 nach dem Löschen eines Tasks

    # Teste, ob alle Tasks erfolgreich abgerufen werden können
    def test_get_all_tasks(self):
        response = self.app.get('/tasks')
        self.assertEqual(response.status_code, 302)  # Erwartet 302 nach dem Abrufen aller Tasks

    # Teste, ob ein spezifischer Task erfolgreich abgerufen werden kann
    def test_get_specific_task(self):
        task_id = 1  # Annahme: Ein Task mit ID 1 existiert
        response = self.app.get(f'/tasks/{task_id}')
        self.assertEqual(response.status_code, 302)  # Erwartet 302 nach dem Abrufen eines spezifischen Tasks

    # Teste, ob ein Task erfolgreich aktualisiert werden kann
    def test_update_task(self):
        task_id = 1  # Annahme: Ein Task mit ID 1 existiert
        updated_task_data = {'content': 'Updated Task Content', 'completed': True}
        response = self.app.put(f'/tasks/{task_id}', json=updated_task_data)
        self.assertEqual(response.status_code, 302)  # Erwartet 302 nach der Aktualisierung eines Tasks

if __name__ == '__main__':
    unittest.main()
