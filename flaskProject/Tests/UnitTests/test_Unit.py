import unittest
import os
from pony.orm import db_session, Database, PrimaryKey, Required, Optional, Set, CacheIndexError, commit
from flaskProject import app
from flaskProject.app import User, DB, teacherCont, studentCont, Cls, Unit
from unittest import mock
from unittest.mock import patch



class MyTestCase(unittest.TestCase):
    def setUp(self):
        DB = Database()
        DB.bind(provider='sqlite', filename='..\\..\\dbtest.sqlite', create_db=True)

        class User(DB.Entity):
            name = PrimaryKey(str)
            password = Required(str)
            type = Required(int)
            teaching = Set('Cls', reverse='teacher', cascade_delete=False)
            inClass = Set('Cls_User', cascade_delete=False)
            activeUnits = Set("ActiveUnit", reverse='student')

        class Cls(DB.Entity):
            name = PrimaryKey(str)
            teacher = Required(User, reverse='teaching')
            students = Set('Cls_User')
            hasUnits = Set('Unit', reverse='cls', cascade_delete=False)

        class Cls_User(DB.Entity):
            cls = Required(Cls)
            user = Required(User)
            approved = Required(bool)
            PrimaryKey(cls, user)

        class Unit(DB.Entity):
            name = Required(str)
            cls = Required(Cls, reverse='hasUnits')
            desc = Optional(str)
            template = Required(str)
            Qnum = Required(str)
            maxTime = Required(str)
            subDate = Required(str)
            instances = Set('ActiveUnit', reverse='unit')
            order = Required(int)
            next = Optional(str)
            PrimaryKey(name, cls)

        class Question(DB.Entity):
            id = Required(int)
            question_preamble = Required(str)
            question = Required(str)
            answer1 = Required(str)
            answer2 = Required(str)
            answer3 = Required(str)
            answer4 = Required(str)
            correct_ans = Required(int)
            active_unit = Required('ActiveUnit', reverse='questions')
            solved_correctly = Optional(bool)
            PrimaryKey(active_unit, id)

        class ActiveUnit(DB.Entity):
            inProgress = Required(bool)
            attempt = Required(int)
            questions = Set('Question', reverse='active_unit')
            unit = Required(Unit, reverse='instances')
            student = Required(User, reverse='activeUnits')
            grade = Optional(int)
            consecQues = Required(int)
            quesAmount = Required(int)
            currentQuestion = Required(int)
            totalCorrect = Required(int)
            lastTimeAnswered = Optional(str)
            PrimaryKey(unit, student, attempt)

        # Generate mapping and create tables

        DB.generate_mapping(create_tables=True)

    def tearDown(self):
        DB.disconnect()
        # Remove the test database file after testing
        cwd = os.getcwd()
        os.remove('\\'.join(cwd.split('\\')[:-2]) + r'\dbtest.sqlite')

    @patch('flaskProject.app.isLogin')
    def test_editUnit_incorrect_teacher(self, mock_isLogin):
        # Set up the mock
        mock_isLogin.return_value = False
        mock_isLogin.side_effect = lambda x: False

        # Add test data
        with db_session:
            teacher = User(name="John", password="123", type=1)
            c = Cls(name="Math", teacher=teacher)
            u = Unit(
                name="Math",
                cls=c,
                desc="Basic algebra",
                template="template1",
                Qnum="10",
                maxTime="60",
                subDate="2023-05-31",
                order=1,
                # next=None
            )

            # Check that the unit was not edited
            with db_session:
                unit = Unit.get(name="Math")
                self.assertEqual(unit.desc, "Basic algebra")
                self.assertEqual(unit.template, "template1")
                self.assertEqual(unit.Qnum, "10")
                self.assertEqual(unit.maxTime, "60")
                self.assertEqual(unit.subDate, "2023-05-31")
                self.assertEqual(unit.order, 1)
                self.assertEqual(unit.next, '')

        # Test that editUnit returns "user <teacherName> not logged in." and status code 400
        response, status_code = app.editUnit_buisness("Math", "Math", "Calculus", "10", "60", "2023-05-31", "Advanced calculus", "Johny")
        self.assertEqual(response, "user Johny is not a teacher")
        self.assertEqual(status_code, 400)

    @patch('flaskProject.app.isLogin')
    def test_editUnit_non_existent_unit(self, mock_isLogin):
        # Set up the mock
        mock_isLogin.return_value = True

        # Add test data
        with db_session:
            teacher = User(name="John", password="123", type=1)
            c = Cls(name="Math", teacher=teacher)
            u = Unit(
                name="Mathx",
                cls=c,
                desc="Basic algebra",
                template="template1",
                Qnum="10",
                maxTime="60",
                subDate="2023-05-31",
                order=1,
                # next=None
            )

        # Test that attempting to edit a non-existent unit returns an error message and status code 400
        with db_session:
            response = app.editUnit_buisness("Math", "Math", "Calculus", "10", "60", "2023-05-31", "Advanced calculus", "John")
            error_message, status_code = response
            self.assertEqual(error_message, "Unit['Math',Cls['Math']]")
            self.assertEqual(status_code, 400)


    @patch('flaskProject.app.isLogin')
    def test_editUnit_successful(self, mock_isLogin):
        # Set up the mock
        mock_isLogin.return_value = True

        # Add test data
        with db_session:
            teacher = User(name="John", password="123", type=1)
            c = Cls(name="Math", teacher=teacher)
            u = Unit(
                name="Math",
                cls=c,
                desc="Basic algebra",
                template="template1",
                Qnum="10",
                maxTime="60",
                subDate="2023-05-31",
                order=1,
                # next=None
            )

            # Test that editUnit returns "successful" and status code 200
            response = app.editUnit_buisness("Math", "Math", "Calculus", "10", "60", "2023-05-31", "Advanced calculus", "John")
            self.assertEqual(response, ({'message': 'successful'}, 200))


            # Assert that the unit was renamed and updated in the database
            self.assertIsNotNone(Unit.get(name="Calculus", cls=c))

            self.assertIsNone(Unit.get(name="Algebra", cls=c))

            unit = Unit.get(name="Calculus", cls=c)
            self.assertEqual(unit.desc, "Advanced calculus")
            self.assertEqual(unit.Qnum, "10")
            self.assertEqual(unit.maxTime, "60")
            self.assertEqual(unit.subDate, "2023-05-31")

        # success test
        with db_session:
            teacher = User(name="Jane", password="456", type=1)
            c = Cls(name="Science", teacher=teacher)
            u = Unit(
                name="Chemistry",
                cls=c,
                desc="Basic chemistry",
                template="template1",
                Qnum="15",
                maxTime="90",
                subDate="2023-06-30",
                order=1,
                # next=None
            )

            response, status_code = app.editUnit_buisness("Chemistry", "Science", "Biology", "10", "60", "2023-05-31", "Basic biology", "John")

            self.assertEqual(response, {"message": "successful"})
            self.assertEqual(status_code, 200)

    @patch('flaskProject.app.isLogin')
    def test_editUnit_not_teacher(self, mock_isLogin):
        # Set up the mock
        mock_isLogin.return_value = True

        # Add test data
        with db_session:
            teacher = User(name="teacher", password="123", type=2)
            c = Cls(name="Math", teacher=teacher)
            u = Unit(
                name="Math",
                cls=c,
                desc="Basic algebra",
                template="template1",
                Qnum="10",
                maxTime="60",
                subDate="2023-05-31",
                order=1,
                # next=None
            )

            # Test that editUnit returns "successful" and status code 200
            response = app.editUnit_buisness("Math", "Math", "Calculus", "10", "60", "2023-05-31", "Advanced calculus", "John")
            self.assertEqual(response, ('user John is not a teacher', 400))


    @patch('flaskProject.app.isLogin')
    def test_removeUnit_incorrect_class(self, mock_isLogin):
        # Set up the mock
        mock_isLogin.return_value = True

        # Add test data
        with db_session:
            teacher = User(name="John", password="123", type=1)
            c = Cls(name="Math", teacher=teacher)
            u = Unit(
                name="Calculus",
                cls=c,
                desc="Advanced calculus",
                template="template1",
                Qnum="10",
                maxTime="60",
                subDate="2023-05-31",
                order=1,
                # next=None
            )

            # Test that removeUnit_for_test returns an error message and status code 400
            response, status_code = app.removeUnit_buisness("Calculus", "English", "John")
            self.assertIn("Cls['English']", response)
            self.assertEqual(status_code, 400)

            # Assert that the unit was not removed from the database
            self.assertIsNotNone(Unit.get(name="Calculus", cls=c))

    def test_teacherOpenUnit_exception_class_not_found(self):
        unitName = "Unit 2"
        teacherName = "John Doe"
        className = "Math Class"
        template = "Template B"
        Qnum = "15"
        maxTime = "90"
        subDate = "2023-05-25"
        first = 'true'
        prev = "Prev Unit"
        desc = "Unit 2 description"

        result = app.teacherOpenUnit(unitName, teacherName, className, template, Qnum, maxTime, subDate, first, prev,
                                 desc)
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[0], "Cls['Math Class']")
        self.assertEqual(result[1], 400)


    def test_teacherOpenUnit_success(self):
        unitName = "Unit 1"
        teacherName = "John Doe"
        className = "English Class"
        template = "Template A"
        Qnum = "10"
        maxTime = "60"
        subDate = "2023-05-20"
        first = 'true'
        prev = None
        desc = "Unit 1 description"
        with db_session:
            teacher = app.makeUser("teacher1", "123", 1)
            app.makeClass("teacher1", "English Class")
            result = app.teacherOpenUnit(unitName, teacherName, className, template, Qnum, maxTime, subDate, first, prev, desc)
            self.assertEqual(result, "success")
            result = app.teacherOpenUnit(unitName, teacherName, className, template, Qnum, maxTime, subDate,
                                         first,
                                         prev, desc)
            self.assertEqual(result, ("Cannot create Unit: instance with primary key Unit 1, Cls['English Class'] "'already exists', 400))

    @patch('flaskProject.app.db_session')
    def test_teacherOpenUnit_fail_name_unique(self, mock_isLogin=None):
        # Set up the mock
        mock_isLogin.return_value = True

        unitName = "Unit 2"
        teacherName = "John Doe"
        className = "English Class"
        template = "Template A"
        Qnum = "10"
        maxTime = "60"
        subDate = "2023-05-20"
        first = 'true'
        prev = None
        desc = "Unit 2 description"
        with db_session:
            teacher = app.makeUser("teacher1", "123", 1)
            app.makeClass("teacher1", "English Class")
            result = app.teacherOpenUnit(unitName, teacherName, className, template, Qnum, maxTime, subDate, first,
                                         prev, desc)
            self.assertEqual(result, "success")
            result = app.teacherOpenUnit(unitName, teacherName, className, template, Qnum, maxTime, subDate,
                                         first,
                                         prev, desc)
            self.assertEqual(result, (
            "Cannot create Unit: instance with primary key Unit 2, Cls['English Class'] "'already exists', 400))


    @patch('flaskProject.app.db_session')
    def test_teacherOpenUnit_failure_incorrect_class_name(self, mock_db_session):
        unitName = "Unit 1"
        teacherName = "John Doe"
        className = "English Class"
        template = "Template A"
        Qnum = "10"
        maxTime = "60"
        subDate = "2023-05-20"
        first = 'true'
        prev = None
        desc = "Unit 3 description"


        # Raise an exception within the db_session context
        mock_db_session.side_effect = Exception("Something went wrong")


        with db_session:
            teacher = app.makeUser("teacher1", "123", 1)
            app.makeClass("teacher1", "English Classs")
            result = app.teacherOpenUnit(unitName, teacherName, className, template, Qnum, maxTime, subDate, first,
                                     prev, desc)

            self.assertEqual(result, ("Cls['English Class']", 400))



    @patch('flaskProject.app.isLogin')
    def test_deleteUnit_success(self, mock_isLogin):
        # Set up the mock
        mock_isLogin.return_value = True
        with db_session:
            teacher = User(name="John Doe", password="password", type=1)
            cls = Cls(name="English Class", teacher=teacher)
            unit = Unit(name="Unit", cls=cls, desc="Unit description", template="Template A",
                        Qnum="10", maxTime="60", subDate="2023-05-20", order=1)
            commit()
            # Call the deleteUnit function
            result = app.deleteUnit_buisness("Unit", "English Class", "John Doe")
            # Verify that the unit was deleted successfully
            with db_session:
                units = app.select(u for u in Unit if u.name == "Unit" and u.cls.name == "English Class")[:]
                self.assertEqual(len(units), 0)

            # Assert that the correct response was returned
            self.assertEqual(result, "deleted successfully")

    @patch('flaskProject.app.isLogin')
    def test_deleteUnit_incorrect_unit_name(self, mock_isLogin):
        # Set up the mock
        mock_isLogin.return_value = True
        with db_session:
            teacher = User(name="John Doe", password="password", type=1)
            cls = Cls(name="English Class", teacher=teacher)
            unit = Unit(name="Unitt", cls=cls, desc="Unit description", template="Template A",
                        Qnum="10", maxTime="60", subDate="2023-05-20", order=1)
            commit()
        # Call the deleteUnit function
        result = app.deleteUnit_buisness("Unit", "English", "Jane Smith")
        # Verify that the unit was not deleted
        with db_session:
            units = app.select(u for u in Unit if u.name == "Unit" and u.cls.name == "English Class")[:]
            self.assertEqual(len(units), 0)

        # Assert that the correct response was returned
        self.assertEqual(result, ("Cls['English']", 400))

    @patch('flaskProject.app.isLogin')
    def test_getClassUnits_success(self, mock_isLogin):
        # Set up the mock
        mock_isLogin.return_value = True
        with db_session:
            teacher = User(name="John Doe", password="password", type=1)
            cls = Cls(name="English Class", teacher=teacher)
            unit1 = Unit(name="Unit 1", cls=cls, desc="Unit 1 description", template="Template A",
                         Qnum="10", maxTime="60", subDate="2023-05-20", order=1)
            unit2 = Unit(name="Unit 2", cls=cls, desc="Unit 2 description", template="Template B",
                         Qnum="5", maxTime="30", subDate="2023-06-01", order=2)
            commit()
        # Call the getClassUnits function
        result = app.getClassUnits_buisness("English Class", "John Doe")

        # Verify the returned units
        expected_units = [
            {
                "id": 1,
                "primary": "Unit 1",
                "secondary": "Unit 1 description",
                "due": "2023-05-20"
            }
        ]
        self.assertEqual(result, expected_units)

    @patch('flaskProject.app.isLogin')
    def test_getClassUnits_incorrect_class(self, mock_isLogin):
        # Set up the mock
        mock_isLogin.return_value = False
        mock_isLogin.side_effect = lambda x: False
        with db_session:
            teacher = User(name="John Doe", password="password", type=1)
            cls = Cls(name="English Class", teacher=teacher)
            unit1 = Unit(name="Unit 1", cls=cls, desc="Unit 1 description", template="Template A",
                         Qnum="10", maxTime="60", subDate="2023-05-20", order=1)
            unit2 = Unit(name="Unit 2", cls=cls, desc="Unit 2 description", template="Template B",
                         Qnum="5", maxTime="30", subDate="2023-06-01", order=2)
            commit()

        # Call the getClassUnits function
        result = app.getClassUnits_buisness("English", "Jane Smith")

        # Verify that the user is not logged in
        self.assertEqual(result, ("Cls['English']", 400))

    def test_getUnitDetails_existing_unit(self):
        with db_session:
            teacher = User(name="John", password="password", type=1)
            cls = Cls(name="English Class", teacher=teacher)
            unit = Unit(name="Unit 1", cls=cls, desc="Unit 1 description", template="Template A",
                        Qnum="10", maxTime="60", subDate="2023-05-20", order=1)
            commit()
        # Call the getUnitDetails_for_tests function with an existing unit
        result = app.getUnitDetails_buisness("English Class", "Unit 1", "John Doe")

        # Verify the returned unit details
        expected_unit = {'Qnum': '10',
                     'desc': 'Unit 1 description',
                     'maxTime': '60',
                     'name': 'Unit 1',
                     'next': '',
                     'order': 1,
                     'subDate': '2023-05-20',
                     'template': 'Template A'}


        self.assertEqual(result, expected_unit)

    def test_getUnitDetails_nonexistent_unit(self):
        # Set up a test database with a sample class and a nonexistent unit
        with db_session:
            teacher = User(name="John Doe", password="password", type=1)
            cls = Cls(name="English Class", teacher=teacher)
            commit()

        # Call the getUnitDetails_for_tests function with the query parameters for a nonexistent unit
        result = app.getUnitDetails_buisness("English", "Unit", "John Doe")

        # Verify that an empty string is returned
        self.assertEqual(result, "")

    @patch('flaskProject.app.isLogin')
    def test_editUnit_nonexistent_class(self, mock_isLogin):
        # Set up the mock
        mock_isLogin.return_value = False
        mock_isLogin.side_effect = lambda x: False

        # Add test data
        with db_session:
            teacher = User(name="John", password="123", type=1)
            c = Cls(name="Math", teacher=teacher)
            u = Unit(
                name="Math",
                cls=c,
                desc="Basic algebra",
                template="template1",
                Qnum="10",
                maxTime="60",
                subDate="2023-05-31",
                order=1,
                # next=None
            )

            # Check that the unit was not edited
            with db_session:
                unit = Unit.get(name="Math")
                self.assertEqual(unit.desc, "Basic algebra")
                self.assertEqual(unit.template, "template1")
                self.assertEqual(unit.Qnum, "10")
                self.assertEqual(unit.maxTime, "60")
                self.assertEqual(unit.subDate, "2023-05-31")
                self.assertEqual(unit.order, 1)
                self.assertEqual(unit.next, '')

        # Test that editUnit returns "user <teacherName> not logged in." and status code 400
        response, status_code = app.editUnit_buisness("Math", "Mathemathic", "Calculus", "10", "60", "2023-05-31", "Advanced calculus", "John")
        self.assertEqual(response, "Cls['Mathemathic']")
        self.assertEqual(status_code, 400)

    @patch('flaskProject.app.isLogin')
    def test_removeUnit_successful(self, mock_isLogin):
        # Set up the mock
        mock_isLogin.return_value = True

        # Add test data
        with db_session:
            teacher = User(name="John", password="123", type=1)
            c = Cls(name="Math", teacher=teacher)
            u = Unit(
                name="Calculus",
                cls=c,
                desc="Advanced calculus",
                template="template1",
                Qnum="10",
                maxTime="60",
                subDate="2023-05-31",
                order=1,
                # next=None
            )

            # Test that removeUnit_for_test returns "successful" and status code 200
            response, status_code = app.removeUnit_buisness("Calculus", "Math", "John")
            self.assertEqual(response, "successful")
            self.assertEqual(status_code, 200)

            # Assert that the unit was removed from the database
            self.assertIsNone(Unit.get(name="Calculus", cls=c))




if __name__ == '__main__':
    unittest.main()