from flask_script import Server, Manager, Command, Shell, Option
from flask_migrate import Migrate, MigrateCommand
from api import app, db

class CreateDbTables(Command):
    """Create db tables"""
    def run(self, **kwargs):
        app.db.create_all()
        print ('Done.')

class DropDbTables(Command):
    """Drop db tables"""
    def run(self, **kwargs):
        app.db.drop_all()
        print ('Dropped.')


manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command("runserver", Server(host="127.0.0.1", port=8050))
manager.add_command('db', MigrateCommand)
manager.add_command("createdb", CreateDbTables())
manager.add_command("dropdb", DropDbTables())
# manager.add_command("testdatadel", RemoveTestData())

if __name__ == '__main__':
    manager.run()

