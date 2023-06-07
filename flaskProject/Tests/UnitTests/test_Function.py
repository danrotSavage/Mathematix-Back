import unittest
import os

import numpy as np
from pony.orm import db_session, Database, PrimaryKey, Required, Optional, Set, CacheIndexError, commit

import flaskProject
from flaskProject import app
from flaskProject.Tests.UnitTests import initiate_database
from flaskProject.app import User, DB, teacherCont, studentCont, Cls, Unit
from unittest import mock
from unittest.mock import patch, MagicMock


class MyTestCase(unittest.TestCase):
    DB = None

    @classmethod
    def setUpClass(cls):
        cls.DB = Database()
        DB = cls.DB
        initiate_database(DB)

    @classmethod
    def tearDownClass(cls):
        cls.DB.drop_all_tables()
        cls.DB.disconnect()

    def tearDown(self) -> None:
        with app.app.app_context():
            app.activeControllers = {}
        with db_session:
            DB.execute('DELETE FROM ActiveUnit WHERE 1=1;')
            DB.execute('DELETE FROM Question WHERE 1=1;')
            DB.execute('DELETE FROM Unit WHERE 1=1;')
            DB.execute('DELETE FROM Cls_User WHERE 1=1;')
            DB.execute('DELETE FROM Cls WHERE 1=1;')
            DB.execute('DELETE FROM User WHERE 1=1;')




    def testPoly(self):
        p = [-3, 7, -4, 1]
        c = 0
        b = 2
        a = app.makeFunc(p, c=c, b=b)
        self.assertTrue(-219 == a(5))
        dom = app.makeDomain(p, c)
        self.assertTrue([(float('-inf'), float('inf'))] == dom)
        self.assertTrue(app.makeIntersections(a, c=c, r=dom) == [(1.65, 0.0)])
        self.assertTrue(app.makeExtremes(p, c=c) == [(0.38, 0.326), (1.18, 1.098)])
        self.assertTrue(app.makeIncDec(p, c=c) == ([(0.38, 1.18)], [(float('-inf'), 0.38), (1.18, float('inf'))]))
        self.assertTrue(app.funcString(p, c=c) == "y=-3x^3+7x^2-4x+1")
        self.assertTrue(app.deriveString(p, c=c) == "y=-9x^2+14x-4")
        self.assertTrue(app.makePosNeg(p, c=c) == ([(float('-inf'), 1.65)], [(1.65, float('inf'))]))
        self.assertTrue(app.makeAsym(p, c=c) == ([], []))

    def testExp(self): #need good assert values
        p = [-3, 7, -4, 1]
        c = 1
        b = 2
        a = app.makeFunc(p, c=c, b=b)
        self.assertTrue(1.0000000000000568 == a(5))
        dom = app.makeDomain(p, c)
        self.assertTrue([(float('-inf'), float('inf'))] == dom)
        self.assertTrue(app.makeIntersections(a, c=c, r=dom) == [])
        #self.assertTrue(app.makeExtremes(p, c=c, b=b) == [(1.167, 2.059)])
        #self.assertTrue(
        #    app.makeIncDec(p, c=c, b=b) == ([(float('-inf'), 1.167)], [ (1.167, float('inf'))]))
        self.assertTrue(app.funcString(p, c=c, b=b) == "y=2^(-3x^2+7x-4)+1")
        self.assertTrue(app.deriveString(p, c=c, b=b) == "y=ln(2)(-6x+7) * 2^(-3x^2+7x-4)")
        self.assertTrue(app.makePosNeg(p, c=c, b=b) == ([(float('-inf'), float('inf'))], []))
        self.assertTrue(app.makeAsym(p, c=c, b=b) == ([], [(float('inf'), 1.0), (float('-inf'), 1.0)]))

    def testLog(self):  # need good assert values
        p = [-3, 7, -4, 1]
        c = 2
        b = 2
        a = app.makeFunc(p, c=c, b=b)
        self.assertTrue(None == a(5))
        dom = app.makeDomain(p, c)
        self.assertTrue([(1.0, 1.333)] == dom)
        self.assertTrue(app.makeIntersections(a, c=c, r=dom) == [])
        e = app.makeExtremes(p, c=c, b=b)
        self.assertTrue(e == [(1.17, -2.586)])
        self.assertTrue(
            app.makeIncDec(p, c=c, b=b) == ([(1.0, 1.17)], [(1.17, 1.333)]))
        self.assertTrue(app.funcString(p, c=c, b=b) == "y=log2(-3x^2+7x-4)+1")
        self.assertTrue(app.deriveString(p, c=c, b=b) == "y=(-6x+7) / (-3x^2+7x-4)")
        self.assertTrue(app.makePosNeg(p, c=c, b=b) == ([], [(1.0, 1.333)]))
        #self.assertTrue(app.makeAsym(p, c=c, b=b) == ([], ([(1.0, float('-inf')), (1.333, float('-inf'))], [])))

    def testSin(self): #need good assert values
        p = [-3, 7, -4, 1]
        c = 3
        b = 2
        a = app.makeFunc(p, c=c, b=b)
        self.assertTrue(0.9822980748945864 == a(5))
        dom = app.makeDomain(p, c)
        self.assertTrue([(float('-inf'), float('inf'))] == dom)
        #self.assertTrue(app.makeIntersections(a, c=c, r=dom) == ???)
        #self.assertTrue(app.makeExtremes(p, c=c, b=b) == ????)
        #self.assertTrue(
        #    app.makeIncDec(p, c=c, b=b) == ?????)
        self.assertTrue(app.funcString(p, c=c, b=b) == "y=sin(-3x^2+7x-4)+1")
        self.assertTrue(app.deriveString(p, c=c, b=b) == "y=cos(-3x^2+7x-4)(-6x+7)")
        self.assertTrue(app.makePosNeg(p, c=c, b=b) == ([(float('-inf'), -0.46), (-0.46, float('inf'))], []))
        self.assertTrue(app.makeAsym(p, c=c, b=b) ==  ([], []))

    def testCos(self): #need good assert values
        p = [-3, 7, -4, 1]
        c = 4
        b = 2
        a = app.makeFunc(p, c=c, b=b)
        self.assertTrue(1.9998433086476912 == a(5))
        dom = app.makeDomain(p, c)
        self.assertTrue([(float('-inf'), float('inf'))] == dom)
        #self.assertTrue(app.makeIntersections(a, c=c, r=dom) == ????)
        #self.assertTrue(app.makeExtremes(p, c=c, b=b) == ????)
        #self.assertTrue(
        #    app.makeIncDec(p, c=c, b=b) == ?????)
        self.assertTrue(app.funcString(p, c=c, b=b) == "y=cos(-3x^2+7x-4)+1")
        self.assertTrue(app.deriveString(p, c=c, b=b) == "y=-sin(-3x^2+7x-4)(-6x+7)")
        self.assertTrue(app.makePosNeg(p, c=c, b=b) == ([(float('-inf'), float('inf'))], []))
        self.assertTrue(app.makeAsym(p, c=c, b=b) ==  ([], []))

    def testTan(self): #need good assert values
        p = [-3, 7, -4, 1]
        c = 5
        b = 2
        a = app.makeFunc(p, c=c, b=b)
        self.assertTrue(0.9822953007213142 == a(5))
        dom = app.makeDomain(p, c)
        #self.assertTrue(???? == dom)
        #self.assertTrue(app.makeIntersections(a, c=c, r=dom) == ????)
        #self.assertTrue(app.makeExtremes(p, c=c, b=b) == ????)
        #self.assertTrue(
        #    app.makeIncDec(p, c=c, b=b) == ?????)
        self.assertTrue(app.funcString(p, c=c, b=b) == "y=tan(-3x^2+7x-4)+1")
        self.assertTrue(app.deriveString(p, c=c, b=b) == "y=(1/cos^2(-3x^2+7x-4)")
        #self.assertTrue(app.makePosNeg(p, c=c, b=b) == ?????)
        #self.assertTrue(app.makeAsym(p, c=c, b=b) == ????)

    def testCot(self): #need good assert values
        p = [-3, 7, -4, 1]
        c = 6
        b = 2
        a = app.makeFunc(p, c=c, b=b)
        self.assertTrue(-55.48217935019511 == a(5))
        dom = app.makeDomain(p, c)
        #self.assertTrue(???? == dom)
        #self.assertTrue(app.makeIntersections(a, c=c, r=dom) == ????)
        #self.assertTrue(app.makeExtremes(p, c=c, b=b) == ????)
        #self.assertTrue(
        #    app.makeIncDec(p, c=c, b=b) == ?????)
        self.assertTrue(app.funcString(p, c=c, b=b) == "y=cot(-3x^2+7x-4)+1")
        self.assertTrue(app.deriveString(p, c=c, b=b) == "y=(-1/sin^2(-3x^2+7x-4)")
        #self.assertTrue(app.makePosNeg(p, c=c, b=b) == ?????)
        #self.assertTrue(app.makeAsym(p, c=c, b=b) == ????)

    def testRational(self):
        p = [-3, 7, -4, 1]
        c = 7
        b = 2
        a = app.makeFunc(p, c=c, b=b)
        self.assertTrue(0.42105263157894735 == a(5))
        print(p)
        dom = app.makeDomain(p, c)
        print(dom)
        self.assertTrue([(float('-inf'), 0.25), (0.25, float('inf'))] == dom)
        self.assertTrue(app.makeIntersections(a, c=c, r=dom) == [(2.33, 0.0)])
        self.assertTrue(app.makeExtremes(p, c=c) == [])
        self.assertTrue(app.makeIncDec(p, c=c) == ([(float('-inf'), 0.25), (0.25, float('inf'))], []))
        self.assertTrue(app.funcString(p, c=c) == "y=(-3x+7) / (-4x+1)")
        self.assertTrue(app.deriveString(p, c=c) == "y=(((-3) * (-4x+1)) - ((-4) * (-3x+7))) / (-4x+1)^2")
        self.assertTrue(app.makePosNeg(p, c=c) == ([(float('-inf'), 0.25), (2.33, float('inf'))], [(0.25, 2.33)]))
        self.assertTrue(app.makeAsym(p, c=c) == ([(0.25, float('-inf'))], [(float('-inf'), 0.75), (float('inf'), 0.75)]))

    def testRoot(self):
        p = [-3, 7, -4, 1]
        c = 8
        b = 2
        a = app.makeFunc(p, c=c, b=b)
        self.assertTrue(None == a(5))
        dom = app.makeDomain(p, c)
        self.assertTrue([(1.0, 1.33)] == dom)
        self.assertTrue(app.makeIntersections(a, c=c, r=dom) == [])
        self.assertTrue(app.makeExtremes(p, c=c, b=b) == [(1.17, 1.289)])
        self.assertTrue(app.makeIncDec(p, c=c, b=b) == ([(1.17, 1.33)], [(1.0, 1.17)]))
        self.assertTrue(app.funcString(p, c=c, b=b) == "y=(-3x^2+7x-4)^(0.5)+1")
        self.assertTrue(app.deriveString(p, c=c, b=b) == "y=(-6x+7) * 0.5 * (-3x^2+7x-4)^(-0.5)")
        self.assertTrue(app.makePosNeg(p, c=c, b=b) == ([(1.0, 1.33)], []))
        self.assertTrue(app.makeAsym(p, c=c, b=b) == ([(1.0, 1.0),(1.33, 1.1)], []))


if __name__ == '__main__':
    unittest.main()
