from flask_restful import Resource, Api
from data.organization import Organization
from data.FinancialIndicator import FinancialIndicator
from data.Tax import Tax
from data.adresses import Address
from data.Okved import Okved
from data.Contact import Contact
from main import app

api = Api(app)

class OrganizationListAPI(Resource):
    def get(self):
        # Логика для получения списка организаций
        organizations = Organization.query.all()
        # Здесь вы можете использовать Marshmallow для сериализации объектов
        return [{'id': org.id, 'name': org.name, 'inn': org.inn} for org in organizations]

    def post(self):
        # Логика для добавления новой организации
        pass

class OrganizationAPI(Resource):
    def get(self, organization_id):
        # Логика для получения одной организации по ID
        pass

    def put(self, organization_id):
        # Логика для обновления организации
        pass

    def delete(self, organization_id):
        # Логика для удаления организации
        pass

# Добавление ресурсов в API
api.add_resource(OrganizationListAPI, '/api/organizations')
api.add_resource(OrganizationAPI, '/api/organizations/<int:organization_id>')